from typing import List, Dict, Any, Optional
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain_community.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NovaPromptEngineer:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model_name="gpt-4.1",  # You can change this to your preferred model
            temperature=0.7,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.vectorstore = Pinecone.from_existing_index(
            index_name=os.getenv('PINECONE_INDEX'),
            embedding=self.embeddings
        )

    def create_custom_prompt_template(self, template: str) -> PromptTemplate:
        """
        Create a custom prompt template with the specified format.
        
        Args:
            template (str): The prompt template string with placeholders
            
        Returns:
            PromptTemplate: A configured prompt template
        """
        return PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )

    def get_relevant_context(self, query: str, k: int = 4) -> List[str]:
        """
        Retrieve relevant context from the vector store based on the query.
        
        Args:
            query (str): The user's question
            k (int): Number of relevant chunks to retrieve
            
        Returns:
            List[str]: List of relevant context chunks
        """
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

    def generate_response(
        self,
        query: str,
        custom_prompt: Optional[str] = None,
        context_k: int = 4,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using the RAG system with custom prompt engineering.
        
        Args:
            query (str): The user's question
            custom_prompt (str, optional): Custom prompt template
            context_k (int): Number of context chunks to retrieve
            **kwargs: Additional parameters for the LLM chain
            
        Returns:
            Dict[str, Any]: Response containing the answer and metadata
        """
        try:
            # Get relevant context
            context = self.get_relevant_context(query, k=context_k)
            context_str = "\n\n".join(context)

            # Use default prompt if none provided
            if custom_prompt is None:
                custom_prompt = """
                You are Nova, a highly capable, always-available virtual medical receptionist and patient intake assistant. You greet patients, collect demographic and insurance details, confirm coverage, and help them with scheduling and general information. You must:
                - Use only the provided context to answer the patient’s question.  
                - Prioritize clarity, accuracy, and empathy.
                - Always clarify coverage limitations and next steps when insurance or eligibility is unclear.
                - Offer to connect the patient to a human specialist or escalate to another agent (e.g., clinical triage, financial counselor) when their need is outside your scope.
                - If a required document, rule, or process is not present in the context, say: "Based on the information I have, I don't have a specific answer for that. Would you like me to connect you with a specialist or provide general guidance?"
                - For appointment questions, specify required documents, preparation steps, cancellation/rescheduling policies, and any waitlist options.
                - For insurance or coverage inquiries, explain active coverage, co-pay, deductible, and authorizations as clearly as possible.
                - Be professional, friendly, and use plain language.
                - For privacy or sensitive topics, remind the patient their information is confidential.

                Context:
                {context}

                Patient’s Question: {question}

                Nova’s Response:

                """

            # Create and run the chain
            prompt = self.create_custom_prompt_template(custom_prompt)
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            response = chain.run(
                context=context_str,
                question=query,
                **kwargs
            )

            return {
                "answer": response,
                "context_used": context,
                "prompt_template": custom_prompt
            }

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    def analyze_prompt_performance(
        self,
        query: str,
        custom_prompt: str,
        expected_response: str
    ) -> Dict[str, Any]:
        """
        Analyze the performance of a custom prompt.
        
        Args:
            query (str): The test question
            custom_prompt (str): The prompt template to test
            expected_response (str): The expected response
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            response = self.generate_response(query, custom_prompt)
            
            # Create analysis prompt
            analysis_prompt = """
            Analyze the following response against the expected response:
            
            Query: {query}
            Expected Response: {expected}
            Actual Response: {actual}
            
            Provide analysis on:
            1. Relevance
            2. Completeness
            3. Accuracy
            4. Suggestions for improvement
            """
            
            analysis_chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    input_variables=["query", "expected", "actual"],
                    template=analysis_prompt
                )
            )
            
            analysis = analysis_chain.run(
                query=query,
                expected=expected_response,
                actual=response["answer"]
            )
            
            return {
                "analysis": analysis,
                "response": response,
                "prompt_used": custom_prompt
            }
            
        except Exception as e:
            logger.error(f"Error analyzing prompt performance: {str(e)}")
            raise 