# Nova - AI-Powered Healthcare Assistant

Nova is an intelligent healthcare assistant that uses AI to provide personalized healthcare support through voice interactions. The system integrates with Twilio for voice communication and uses advanced language models for natural conversation.

## Features

- Voice-based interaction using Twilio
- AI-powered conversation management
- RAG (Retrieval-Augmented Generation) for accurate healthcare information
- Secure patient data handling
- Multi-language support
- Appointment scheduling capabilities

## Prerequisites

- Node.js (v14 or higher)
- Python 3.8 or higher
- Twilio account
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nova.git
cd nova
```

2. Install Node.js dependencies:
```bash
cd nova-llm-agent
npm install
```

3. Set up Python environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the root directory with the following variables:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
OPENAI_API_KEY=your_openai_api_key
```

## Usage

1. Start the server:
```bash
npm start
```

2. Configure your Twilio phone number to point to your server's `/voice` endpoint.

## Project Structure

- `nova-llm-agent/` - Main application directory
  - `src/` - Source code
    - `controllers/` - Request handlers
    - `utils/` - Utility functions
    - `config/` - Configuration files
    - `rag/` - RAG system implementation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Twilio for voice communication infrastructure
- OpenAI for language model capabilities
- All contributors who have helped shape this project 