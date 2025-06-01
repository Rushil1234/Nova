const { VoiceResponse } = require('twilio').twiml;
const { generateResponse } = require('../config/openaiClient');
const { logger } = require('../utils/logger');
const { ConversationManager } = require('../utils/conversationFlow');
const sessionManager = require('../utils/sessionManager');
const xmlEscape = require('xml-escape');

const conversationManager = new ConversationManager();

// Fallback responses for different scenarios
const FALLBACK_RESPONSES = {
  NO_INPUT: "I didn't hear anything. Please try again.",
  EMPTY_RESPONSE: "I'm having trouble understanding. Could you please rephrase that?",
  ERROR: "I'm experiencing some technical difficulties. Please try again.",
  MAX_ATTEMPTS: "I'm having trouble understanding your request. Would you like to speak with a human representative?",
  TRANSFER: "I'll transfer you to a human representative who can better assist you.",
  GOODBYE: "Thank you for calling. Have a great day!",
  SILENCE: "I'm still here. Please go ahead and speak, or press any key to continue.",
  TIMEOUT: "I didn't hear a response. Please try again or press any key to continue."
};

function createTwiMLResponse(message, options = {}) {
  const twiml = new VoiceResponse();
  const sayOptions = {
    voice: 'Polly.Amy',
    language: 'en-GB',
    rate: '1.2',
    ...options
  };

  // Ensure message is properly escaped for XML
  const escapedMessage = xmlEscape(message);
  twiml.say(sayOptions, escapedMessage);
  return twiml;
}

function createGatherResponse(message, options = {}) {
  const twiml = new VoiceResponse();
  const sayOptions = {
    voice: 'Polly.Amy',
    language: 'en-GB',
    rate: '1.2',
    ...options
  };

  // Ensure message is properly escaped for XML
  const escapedMessage = xmlEscape(message);

  const gather = twiml.gather({
    input: 'speech dtmf',
    action: '/gather',
    method: 'POST',
    speechTimeout: '3',
    speechEndThreshold: '1000',
    language: 'en-US',
    enhanced: true,
    speechModel: 'phone_call',
    timeout: '10',
    ...options
  });

  gather.say(sayOptions, escapedMessage);
  return twiml;
}

async function processGather(req, res) {
  // Set content type header first
  res.type('text/xml');

  const callSid = req.body.CallSid;
  let session = sessionManager.getSession(callSid);

  // Create session if it doesn't exist
  if (!session) {
    session = sessionManager.createSession(callSid);
  }

  try {
    // Log all incoming Twilio fields for debugging
    logger.info('Received gather request with full details:', {
      callSid,
      speechResult: req.body.SpeechResult,
      speechConfidence: req.body.SpeechConfidence,
      speechDuration: req.body.SpeechDuration,
      digits: req.body.Digits,
      callStatus: req.body.CallStatus,
      direction: req.body.Direction,
      gatherAttempts: req.body.GatherAttempts,
      gatherDuration: req.body.GatherDuration,
      attempts: session.attempts,
      reason: req.body.SpeechResult ? 'speech' : req.body.Digits ? 'dtmf' : 'timeout',
      rawBody: req.body
    });

    // Handle timeout or silence
    if (req.body.SpeechResult === '' || req.body.SpeechResult === undefined) {
      sessionManager.incrementAttempts(callSid);
      
      if (sessionManager.shouldTransfer(callSid)) {
        const twiml = createTwiMLResponse(FALLBACK_RESPONSES.MAX_ATTEMPTS);
        twiml.say({ voice: 'Polly.Amy', language: 'en-GB', rate: '1.2' }, xmlEscape(FALLBACK_RESPONSES.TRANSFER));
        twiml.hangup();
        res.send(twiml.toString());
        return;
      }

      // If we haven't reached max attempts, give another chance
      const twiml = createGatherResponse(
        session.attempts === 1 ? FALLBACK_RESPONSES.SILENCE : FALLBACK_RESPONSES.TIMEOUT,
        {
          action: '/gather',
          method: 'POST',
          speechTimeout: '5'
        }
      );
      res.send(twiml.toString());
      return;
    }

    // Extract user input (speech or DTMF)
    const userInput = req.body.SpeechResult || req.body.Digits;
    const inputType = req.body.SpeechResult ? 'speech' : 'dtmf';
    const confidence = req.body.SpeechConfidence || 'N/A';

    // Reset attempts on successful input
    sessionManager.resetAttempts(callSid);

    // Log the user input with detailed information
    logger.info('Processing user input with details:', {
      callSid,
      input: userInput,
      type: inputType,
      confidence: confidence,
      duration: req.body.SpeechDuration || 'N/A',
      gatherAttempts: req.body.GatherAttempts,
      gatherDuration: req.body.GatherDuration,
      timestamp: new Date().toISOString()
    });

    // Get AI response using new conversation flow (LLM first, then RAG if needed)
    let aiResponse;
    try {
      aiResponse = await conversationManager.getNextPrompt(callSid, userInput);
      logger.info('AI Response:', {
        callSid,
        response: aiResponse,
        length: aiResponse ? aiResponse.length : 0,
        inputType: inputType,
        confidence: confidence
      });
      if (!aiResponse || aiResponse.trim() === '') {
        logger.warn('Empty AI response received', { 
          callSid,
          userInput,
          response: aiResponse,
          inputType: inputType,
          confidence: confidence
        });
        aiResponse = FALLBACK_RESPONSES.EMPTY_RESPONSE;
      }
    } catch (error) {
      logger.error('Error getting AI response:', {
        callSid,
        error: error.message,
        stack: error.stack,
        userInput,
        inputType: inputType,
        confidence: confidence
      });
      aiResponse = `I heard you say "${xmlEscape(userInput)}". I'm having trouble processing that right now. Could you please try rephrasing your question?`;
    }

    // Add to conversation history with detailed information
    sessionManager.addToHistory(callSid, {
      input: userInput,
      type: inputType,
      confidence: confidence,
      duration: req.body.SpeechDuration || 'N/A',
      timestamp: new Date()
    }, aiResponse);

    // Create response with gather for next input
    const twiml = createGatherResponse(aiResponse, {
      action: '/gather',
      method: 'POST'
    });

    // Add a polite goodbye if no input is received
    twiml.say({
      voice: 'Polly.Amy',
      language: 'en-GB',
      rate: '1.2'
    }, xmlEscape(FALLBACK_RESPONSES.GOODBYE));
    twiml.hangup();

    const response = twiml.toString();
    logger.info('Generated TwiML response:', {
      callSid,
      response,
      userInput,
      inputType: inputType,
      confidence: confidence
    });

    res.send(response);

  } catch (error) {
    logger.error('Unexpected error in gather processor:', {
      callSid,
      error: error.message,
      stack: error.stack,
      body: req.body
    });

    // Send a basic error response
    const twiml = createTwiMLResponse(FALLBACK_RESPONSES.ERROR);
    res.send(twiml.toString());
  }
}

module.exports = {
  processGather,
}; 