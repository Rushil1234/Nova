const twilio = require('twilio');
const { logger } = require('../utils/logger');

const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const phoneNumber = process.env.TWILIO_PHONE_NUMBER;

if (!accountSid || !authToken || !phoneNumber) {
  logger.error('Missing required Twilio configuration');
  process.exit(1);
}

const client = twilio(accountSid, authToken);

module.exports = {
  client,
  phoneNumber,
}; 