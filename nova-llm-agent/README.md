# Nova LLM Agent

A Twilio-based LLM agent for handling phone calls using OpenAI's GPT models.

## Features

- Voice call handling using Twilio
- Natural language processing with OpenAI's GPT models
- Speech-to-text and text-to-speech conversion
- Error handling and logging

## Prerequisites

- Node.js (v14 or higher)
- Twilio account with a phone number
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd nova-llm-agent
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Update the `.env` file with your credentials:
- `OPENAI_API_KEY`: Your OpenAI API key
- `TWILIO_ACCOUNT_SID`: Your Twilio account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio auth token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number

## Usage

1. Start the development server:
```bash
npm run dev
```

2. Configure your Twilio phone number's voice webhook to point to your server's `/voice` endpoint.

3. Make a call to your Twilio phone number to interact with the AI assistant.

## Development

- `npm run dev`: Start the development server with hot reload
- `npm start`: Start the production server
- `npm test`: Run tests

## License

MIT 