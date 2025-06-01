const { VoiceResponse } = require('twilio').twiml;
const { generateResponse } = require('../config/openaiClient');
const { logger } = require('../utils/logger');
const { ConversationManager } = require('../utils/conversationFlow');
const xmlEscape = require('xml-escape');

const conversationManager = new ConversationManager();

async function handleIncomingCall(req, res) {
  // Set content type header first
  res.type('text/xml');

  try {
    logger.info('Received incoming call request');
    const callSid = req.body.CallSid;
    
    // Get or create session
    const session = conversationManager.getSession(callSid);
    logger.info(`Session ready for call ${callSid}`);
    
    const twiml = new VoiceResponse();
    
    // Get the initial greeting
    const greeting = "Hello! I'm Nova, your virtual healthcare assistant. How can I help you today?";
    
    // Add the greeting to the TwiML with proper escaping
    twiml.say({
      voice: 'Polly.Amy',
      language: 'en-GB',
      rate: '1.2'
    }, xmlEscape(greeting));
    
    // Add Gather verb to collect user input
    const gather = twiml.gather({
      input: 'speech dtmf',
      action: '/gather',
      method: 'POST',
      speechTimeout: '3',
      speechEndThreshold: '1000',
      language: 'en-US',
      enhanced: true,
      speechModel: 'phone_call',
      timeout: '10'
    });
    
    // If no input is received, repeat the greeting
    twiml.redirect('/voice');

    const response = twiml.toString();
    logger.info('Generated TwiML response:', {
      callSid,
      response
    });
    
    res.send(response);
  } catch (error) {
    logger.error('Error handling incoming call:', {
      error: error.message,
      stack: error.stack
    });
    
    // Send a basic TwiML response even in case of error
    const twiml = new VoiceResponse();
    twiml.say({
      voice: 'Polly.Amy',
      language: 'en-GB',
      rate: '1.2'
    }, xmlEscape('We are experiencing technical difficulties. Please try again later.'));
    res.send(twiml.toString());
  }
}

module.exports = {
  handleIncomingCall,
}; 