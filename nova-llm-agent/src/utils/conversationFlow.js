const { logger } = require('./logger');
const RAGQueryHandler = require('./rag/queryHandler');
const { generateResponse } = require('../config/openaiClient');

const CONVERSATION_STATES = {
  GREETING: 'GREETING',
  DEMOGRAPHICS: 'DEMOGRAPHICS',
  IDENTITY_VERIFICATION: 'IDENTITY_VERIFICATION',
  INSURANCE_VERIFICATION: 'INSURANCE_VERIFICATION',
  COVERAGE_VALIDATION: 'COVERAGE_VALIDATION',
  APPOINTMENT_SCHEDULING: 'APPOINTMENT_SCHEDULING',
  WARM_HANDOFF: 'WARM_HANDOFF',
  GOODBYE: 'GOODBYE'
};

const DEMOGRAPHICS_FIELDS = [
  'fullName',
  'dateOfBirth',
  'address',
  'phoneNumber',
  'email',
  'preferredLanguage',
  'specialNeeds'
];

const SECURITY_QUESTIONS = [
  'What is your mother\'s maiden name?',
  'What was the name of your first pet?',
  'In which city were you born?'
];

// Only trigger RAG for very specific fallback phrases
const GENERIC_FALLBACKS = [
  "I don't have a specific answer for that",
  "I don't have enough information",
  "I cannot provide a specific answer"
];

class ConversationManager {
  constructor() {
    this.sessions = new Map();
    this.ragHandler = new RAGQueryHandler();
    logger.info('ConversationManager initialized with RAG handler');
  }

  createSession(callSid) {
    // Check if session already exists
    if (this.sessions.has(callSid)) {
      logger.info(`Session already exists for call ${callSid}`);
      return this.sessions.get(callSid);
    }

    const session = {
      state: CONVERSATION_STATES.GREETING,
      attempts: 0,
      lastInput: null,
      conversationHistory: [],
      createdAt: new Date(),
      lastUpdated: new Date()
    };
    this.sessions.set(callSid, session);
    logger.info(`Created new session for call ${callSid}`);
    return session;
  }

  getSession(callSid) {
    const session = this.sessions.get(callSid);
    if (!session) {
      logger.error(`No session found for call ${callSid}`);
      // Create a new session if one doesn't exist
      return this.createSession(callSid);
    }
    return session;
  }

  async getNextPrompt(callSid, userInput) {
    try {
      const session = this.getSession(callSid);
      
      // Update session with new input
      session.lastInput = userInput;
      session.lastUpdated = new Date();
      session.conversationHistory.push({
        role: 'user',
        content: userInput,
        timestamp: new Date()
      });

      logger.info('Processing user input:', {
        callSid,
        state: session.state,
        input: userInput,
        historyLength: session.conversationHistory.length
      });

      // Get conversation context
      const context = this.getConversationContext(session);
      
      // 1. Try direct LLM with context
      let llmResponse = await generateResponse(userInput, context);
      logger.info('Direct LLM response:', { 
        callSid, 
        response: llmResponse,
        contextLength: context.length,
        state: session.state
      });

      // 2. Only use RAG if the response is empty or contains specific fallback phrases
      if (!llmResponse || llmResponse.trim() === '' || 
          GENERIC_FALLBACKS.some(fb => llmResponse.toLowerCase().includes(fb.toLowerCase()))) {
        logger.info('Using RAG for better response', { 
          callSid,
          state: session.state,
          llmResponse: llmResponse
        });
        const ragResponse = await this.ragHandler.query(userInput, context);
        if (ragResponse && ragResponse.trim() !== '') {
          llmResponse = ragResponse;
          logger.info('RAG response used:', {
            callSid,
            response: llmResponse,
            state: session.state
          });
        }
      }

      // 3. If still empty, provide a more helpful response
      if (!llmResponse || llmResponse.trim() === '') {
        logger.warn('Empty response after LLM and RAG', { 
          callSid,
          state: session.state,
          userInput: userInput
        });
        llmResponse = `I heard you say "${userInput}". Let me help you with that. Could you please provide more details about what you need?`;
      }

      // Update session with AI response
      session.conversationHistory.push({
        role: 'assistant',
        content: llmResponse,
        timestamp: new Date()
      });

      // Update conversation state based on input and response
      this.updateConversationState(session, userInput, llmResponse);

      logger.info('Final response:', {
        callSid,
        responseLength: llmResponse.length,
        response: llmResponse,
        state: session.state
      });

      return llmResponse;
    } catch (error) {
      logger.error('Error in getNextPrompt:', {
        callSid,
        error: error.message,
        stack: error.stack,
        userInput: userInput
      });
      return `I heard you say "${userInput}". I'm here to help. Could you please tell me more about what you need?`;
    }
  }

  updateConversationState(session, userInput, aiResponse) {
    const input = userInput.toLowerCase();
    const response = aiResponse.toLowerCase();

    // Log state transition attempt
    logger.info('Attempting state transition:', {
      currentState: session.state,
      userInput: userInput,
      responseLength: aiResponse.length
    });

    // Update state based on keywords and context
    if (input.includes('hello') || input.includes('hi') || input.includes('hey')) {
      session.state = CONVERSATION_STATES.GREETING;
    } else if (input.includes('name') || input.includes('call me')) {
      session.state = CONVERSATION_STATES.DEMOGRAPHICS;
    } else if (input.includes('insurance') || input.includes('coverage')) {
      session.state = CONVERSATION_STATES.INSURANCE_VERIFICATION;
    } else if (input.includes('appointment') || input.includes('schedule')) {
      session.state = CONVERSATION_STATES.APPOINTMENT_SCHEDULING;
    } else if (input.includes('goodbye') || input.includes('bye') || input.includes('thank you')) {
      session.state = CONVERSATION_STATES.GOODBYE;
    }

    logger.info('State transition complete:', {
      previousState: session.state,
      newState: session.state,
      userInput: userInput
    });
  }

  getConversationContext(session) {
    // Get the last 5 exchanges for context
    const recentHistory = session.conversationHistory.slice(-10);
    const context = recentHistory.map(exchange => 
      `${exchange.role === 'user' ? 'Patient' : 'Nova'}: ${exchange.content}`
    ).join('\n');

    logger.info('Generated conversation context:', {
      historyLength: session.conversationHistory.length,
      contextLength: context.length,
      state: session.state
    });

    return context;
  }

  cleanupSession(callSid) {
    this.sessions.delete(callSid);
    logger.info(`Cleaned up session for call ${callSid}`);
  }
}

module.exports = {
  ConversationManager,
  CONVERSATION_STATES
}; 