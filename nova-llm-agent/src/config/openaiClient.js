const OpenAI = require('openai');
const { logger } = require('../utils/logger');

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const NOVA_PROMPT = `You are Nova, a highly capable, always-available virtual medical receptionist and patient intake assistant. You greet patients, collect demographic and insurance details, confirm coverage, and help them with scheduling and general information.

Your primary goal is to help patients with their healthcare needs. You should:
- Be friendly, professional, and empathetic
- Provide clear, accurate information
- Ask for clarification when needed
- Offer to connect with specialists when appropriate
- Use simple, clear language
- Maintain a helpful and positive tone

Previous conversation:
{context}

Patient's Question: {question}

Please provide a helpful, direct response. If you need more information, ask a specific follow-up question.`;

async function generateResponse(question, context = '') {
  try {
    const prompt = NOVA_PROMPT
      .replace('{context}', context)
      .replace('{question}', question);

    logger.info('Generating OpenAI response:', {
      questionLength: question.length,
      contextLength: context.length,
      promptLength: prompt.length
    });

    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4',
      messages: [
        { 
          role: 'system', 
          content: 'You are Nova, a helpful healthcare assistant. Always be clear, direct, and helpful.' 
        },
        { role: 'user', content: prompt }
      ],
      temperature: 0.7,
      max_tokens: 150
    });

    const response = completion.choices[0].message.content;
    logger.info('OpenAI response generated:', {
      responseLength: response.length,
      response: response
    });

    return response;
  } catch (error) {
    logger.error('Error generating OpenAI response:', {
      error: error.message,
      stack: error.stack
    });
    throw error;
  }
}

module.exports = {
  generateResponse,
}; 