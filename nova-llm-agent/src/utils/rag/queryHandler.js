const { OpenAIEmbeddings } = require('@langchain/openai');
const { Pinecone } = require('@pinecone-database/pinecone');
const { ChatOpenAI } = require('@langchain/openai');
const { logger } = require('../logger');

class RAGQueryHandler {
  constructor() {
    // Check for required environment variables
    if (!process.env.OPENAI_API_KEY) {
      throw new Error('OPENAI_API_KEY is not set in environment variables');
    }
    if (!process.env.PINECONE_API_KEY) {
      throw new Error('PINECONE_API_KEY is not set in environment variables');
    }
    if (!process.env.PINECONE_INDEX) {
      throw new Error('PINECONE_INDEX is not set in environment variables');
    }

    try {
      this.embeddings = new OpenAIEmbeddings({
        openAIApiKey: process.env.OPENAI_API_KEY,
      });
      logger.info('OpenAI Embeddings initialized successfully');
      
      this.pineconeClient = new Pinecone({
        apiKey: process.env.PINECONE_API_KEY,
      });
      logger.info('Pinecone client initialized successfully');
      
      this.model = new ChatOpenAI({
        openAIApiKey: process.env.OPENAI_API_KEY,
        temperature: 0.7,
        modelName: 'gpt-4',
      });
      logger.info('OpenAI Chat model initialized successfully');
    } catch (error) {
      logger.error('Error initializing RAG components:', {
        error: error.message,
        stack: error.stack
      });
      throw error;
    }
  }

  async query(question, context = '') {
    try {
      logger.info('Processing RAG query:', { 
        question, 
        contextLength: context.length,
        hasOpenAIKey: !!process.env.OPENAI_API_KEY,
        hasPineconeKey: !!process.env.PINECONE_API_KEY,
        hasPineconeIndex: !!process.env.PINECONE_INDEX
      });
      
      // Get the Pinecone index
      const index = this.pineconeClient.Index(process.env.PINECONE_INDEX);
      
      // Generate embeddings
      const embedding = await this.embeddings.embedQuery(question);
      logger.info('Generated embeddings successfully', {
        embeddingLength: embedding.length
      });
      
      // Query the index
      const queryResponse = await index.query({
        vector: embedding,
        topK: 3,
        includeMetadata: true
      });

      // Extract relevant documents
      const relevantDocs = queryResponse.matches
        .map(match => match.metadata?.text || '')
        .filter(text => text)
        .join('\n\n');

      logger.info('Retrieved relevant documents:', { 
        count: queryResponse.matches.length,
        hasContent: !!relevantDocs,
        matchScores: queryResponse.matches.map(m => m.score)
      });

      // Create prompt with context
      const prompt = `\nContext: ${context}\n\nRelevant Information from Documents:\n${relevantDocs}\n\nQuestion: ${question}\n\nPlease provide a helpful response based on the context and relevant information above. If the information is not available in the documents, please say so.\n`;

      // Generate response using ChatOpenAI
      const response = await this.model.call([
        { role: 'system', content: 'You are a helpful assistant for healthcare calls.' },
        { role: 'user', content: prompt }
      ]);
      const trimmedResponse = response.trim ? response.trim() : response;
      
      logger.info('Generated response:', { 
        responseLength: trimmedResponse.length,
        hasResponse: !!trimmedResponse,
        promptLength: prompt.length
      });

      return trimmedResponse;
    } catch (error) {
      logger.error('Error in RAG query:', {
        error: error.message,
        stack: error.stack,
        errorType: error.constructor.name
      });
      throw error;
    }
  }
}

module.exports = RAGQueryHandler; 