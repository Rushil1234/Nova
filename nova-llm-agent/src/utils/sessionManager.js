const { logger } = require('./logger');

class SessionManager {
  constructor() {
    this.sessions = new Map();
    this.MAX_ATTEMPTS = 3;
  }

  createSession(callSid) {
    const session = {
      callSid,
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
    return this.sessions.get(callSid);
  }

  incrementAttempts(callSid) {
    const session = this.getSession(callSid);
    if (session) {
      session.attempts++;
      session.lastUpdated = new Date();
      logger.info(`Incremented attempts for call ${callSid}. Current attempts: ${session.attempts}`);
    }
    return session;
  }

  resetAttempts(callSid) {
    const session = this.getSession(callSid);
    if (session) {
      session.attempts = 0;
      session.lastUpdated = new Date();
      logger.info(`Reset attempts for call ${callSid}`);
    }
    return session;
  }

  addToHistory(callSid, input, response) {
    const session = this.getSession(callSid);
    if (session) {
      session.conversationHistory.push({
        timestamp: new Date(),
        input,
        response
      });
      session.lastUpdated = new Date();
      logger.info(`Added to conversation history for call ${callSid}`);
    }
    return session;
  }

  shouldTransfer(callSid) {
    const session = this.getSession(callSid);
    return session && session.attempts >= this.MAX_ATTEMPTS;
  }

  cleanupSession(callSid) {
    this.sessions.delete(callSid);
    logger.info(`Cleaned up session for call ${callSid}`);
  }
}

module.exports = new SessionManager(); 