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
- Keep responses concise and to the point
- Always acknowledge what you heard before responding
- If you're unsure, ask for clarification

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
      promptLength: prompt.length,
      question: question
    });

    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4',
      messages: [
        { 
          role: 'system', 
          content: `You are Nova, a helpful healthcare assistant. Always:
1. Acknowledge what you heard
2. Be clear and direct
3. Keep responses under 2-3 sentences
4. Ask for clarification if needed
5. Use simple, conversational language`
        },
        { role: 'user', content: prompt }
      ],
      temperature: 0.7,
      max_tokens: 150,
      presence_penalty: 0.6,
      frequency_penalty: 0.3
    });

    const response = completion.choices[0].message.content;
    
    // Log the full response details
    logger.info('OpenAI response generated:', {
      responseLength: response.length,
      response: response,
      question: question,
      contextLength: context.length
    });

    // Validate response
    if (!response || response.trim() === '') {
      logger.warn('Empty response from OpenAI', {
        question: question,
        context: context
      });
      return "I heard your question, but I'm having trouble formulating a response. Could you please rephrase that?";
    }

    return response;
  } catch (error) {
    logger.error('Error generating OpenAI response:', {
      error: error.message,
      stack: error.stack,
      question: question,
      contextLength: context.length
    });
    throw error;
  }
}

module.exports = {
  generateResponse,
}; 