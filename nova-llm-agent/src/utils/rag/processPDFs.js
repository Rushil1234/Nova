require('dotenv').config();
const fs = require('fs').promises;
const path = require('path');
const pdfParse = require('pdf-parse');
const { OpenAIEmbeddings } = require('@langchain/openai');
const { PineconeStore } = require('@langchain/pinecone');
const { Pinecone } = require('@pinecone-database/pinecone');
const { RecursiveCharacterTextSplitter } = require('langchain/text_splitter');
const { logger } = require('../logger');

class PDFProcessor {
  constructor() {
    this.embeddings = new OpenAIEmbeddings({
      openAIApiKey: process.env.OPENAI_API_KEY,
    });
    this.pineconeClient = new Pinecone({
      apiKey: process.env.PINECONE_API_KEY,
      host: `${process.env.PINECONE_INDEX}-${process.env.PINECONE_ENV}.pinecone.io`
    });
    this.textSplitter = new RecursiveCharacterTextSplitter({
      chunkSize: 1000,
      chunkOverlap: 200,
    });
  }

  async initialize() {
    // No initialization needed for Pinecone v1.x
  }

  async processPDF(filePath) {
    try {
      logger.info(`Processing PDF: ${filePath}`);

      // Read PDF file
      const dataBuffer = await fs.readFile(filePath);
      const pdfData = await pdfParse(dataBuffer);

      // Split text into chunks
      const chunks = await this.textSplitter.splitText(pdfData.text);

      // Create embeddings and store in Pinecone
      const index = this.pineconeClient.index(process.env.PINECONE_INDEX); // <-- lowercase 'i'
      const vectorStore = await PineconeStore.fromTexts(
        chunks,
        chunks.map((_, i) => ({
          source: path.basename(filePath),
          chunk: i
        })),
        this.embeddings,
        { pineconeIndex: index }
      );

      logger.info(`Successfully processed ${filePath}`);
      return true;
    } catch (error) {
      logger.error(`Error processing PDF ${filePath}:`, error);
      throw error;
    }
  }

  async processAllPDFs() {
    try {
      await this.initialize();

      const pdfsDir = path.join(__dirname, '../../data/pdfs');
      const files = await fs.readdir(pdfsDir);

      for (const file of files) {
        if (file.endsWith('.pdf')) {
          const filePath = path.join(pdfsDir, file);
          await this.processPDF(filePath);
        }
      }

      logger.info('All PDFs processed successfully');
    } catch (error) {
      logger.error('Error processing PDFs:', error);
      throw error;
    }
  }
}

// If this file is run directly
if (require.main === module) {
  const processor = new PDFProcessor();
  processor.processAllPDFs()
    .then(() => process.exit(0))
    .catch((error) => {
      logger.error('Failed to process PDFs:', error);
      process.exit(1);
    });
}

module.exports = PDFProcessor;
