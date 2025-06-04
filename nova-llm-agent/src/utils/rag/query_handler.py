import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGQueryHandler:
    def __init__(self):
        load_dotenv()
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.pc = Pinecone(
            api_key=os.getenv('PINECONE_API_KEY')
        )
        self.model = ChatOpenAI(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            temperature=0.7,
            model_name='gpt-4'
        )

    async def query(self, question: str, context: str = '') -> str:
        try:
            # Get the index
            index_name = os.getenv('PINECONE_INDEX')
            index = self.pc.Index(index_name)
            
            # Create vector store
            vectorstore = PineconeVectorStore.from_existing_index(
                embedding=self.embeddings,
                index_name=index_name,
                pinecone_index=index
            )
            
            # Get relevant documents
            results = vectorstore.similarity_search(question, k=3)
            relevant_docs = "\n\n".join([doc.page_content for doc in results])
            
            # Create prompt with context
            prompt = f"""
Context: {context}

Relevant Information from Documents:
{relevant_docs}

Question: {question}

Please provide a helpful response based on the context and relevant information above. If the information is not available in the documents, please say so.
"""
            
            # Generate response
            response = await self.model.ainvoke(prompt)
            return response.content.strip()
            
        except Exception as error:
            logger.error(f"Error in RAG query: {error}")
            raise error 