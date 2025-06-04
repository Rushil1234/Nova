import os
from dotenv import load_dotenv
from pathlib import Path
import PyPDF2
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from pinecone import Pinecone as PineconeClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        load_dotenv()
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.index_name = os.getenv('PINECONE_INDEX')

    def process_pdf(self, file_path):
        try:
            logger.info(f"Processing PDF: {file_path}")

            # Read PDF file
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split into {len(chunks)} chunks.")

            # Make metadata for each chunk
            metadatas = [{
                'source': Path(file_path).name,
                'chunk': i
            } for i in range(len(chunks))]

            # Actually upsert vectors to Pinecone
            vectorstore = LangchainPinecone.from_texts(
                texts=chunks,
                embedding=self.embeddings,
                index_name=self.index_name,
                metadatas=metadatas,
            )
            logger.info(f"Uploaded {len(chunks)} vectors to Pinecone index '{self.index_name}'.")

            # Optionally: check how many vectors are in the index
            pc = PineconeClient(api_key=self.pinecone_api_key)
            index = pc.Index(self.index_name)
            stats = index.describe_index_stats()
            logger.info(f"Index stats: {stats}")

            logger.info(f"Successfully processed {file_path}")
            return True

        except Exception as error:
            logger.error(f"Error processing PDF {file_path}: {error}")
            raise error

    def process_all_pdfs(self):
        try:
            pdfs_dir = (Path(__file__).parent.parent.parent / 'data' / 'pdfs').resolve()
            pdf_files = list(pdfs_dir.glob('*.pdf'))
            if not pdf_files:
                logger.warning(f"No PDF files found in {pdfs_dir}")
            for file in pdf_files:
                self.process_pdf(str(file))

            logger.info("All PDFs processed successfully")

        except Exception as error:
            logger.error(f"Error processing PDFs: {error}")
            raise error

if __name__ == "__main__":
    processor = PDFProcessor()
    processor.process_all_pdfs()
