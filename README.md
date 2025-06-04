# Leo - Clinical Documentation AI Assistant

Leo is an expert clinical documentation AI assistant designed for hospital in-patient rounds. It processes transcribed conversations and extracted text from images to generate concise, accurate, and well-structured progress notes for electronic health records (EHR).

## Features

- Processes transcribed audio conversations from healthcare providers
- Extracts information from images (whiteboards, charts, handwritten notes)
- Generates structured progress notes in SOAP/SBAR format
- Tracks changes between notes
- Identifies discrepancies in clinical data
- Maintains professional medical terminology and tone
- Powered by GPT-4 for accurate medical documentation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/leo.git
cd leo
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here

# LLM Configuration
LEO_LLM_PROVIDER=openai
LEO_LLM_MODEL=gpt-4
LEO_LLM_TEMPERATURE=0.3
LEO_LLM_MAX_TOKENS=2000
LEO_LLM_TOP_P=1.0
LEO_LLM_FREQUENCY_PENALTY=0.0
LEO_LLM_PRESENCE_PENALTY=0.0

# Clinical Note Configuration
LEO_CLINICAL_NOTE_DEFAULT_FORMAT=SOAP
LEO_CLINICAL_NOTE_INCLUDE_VITALS=true
LEO_CLINICAL_NOTE_INCLUDE_LABS=true
LEO_CLINICAL_NOTE_INCLUDE_MEDICATIONS=true
LEO_CLINICAL_NOTE_HIGHLIGHT_ABNORMAL=true
LEO_CLINICAL_NOTE_MAX_LENGTH=4000
```

## Usage

1. Start the server:
```bash
uvicorn server:app --reload
```

2. The API will be available at `http://localhost:8000`

3. API Endpoints:
   - POST `/generate-note`: Generate a progress note from clinical input
   - POST `/upload-audio`: Upload and process audio file
   - POST `/upload-image`: Upload and process image file
   - GET `/health`: Health check endpoint

4. Example API request:
```python
import requests

# Generate note from text input
response = requests.post(
    "http://localhost:8000/generate-note",
    json={
        "transcribed_audio": "Doctor: Patient reports improved breathing...",
        "extracted_text_from_images": "BP: 120/80, HR: 72...",
        "previous_note": "Previous progress note content...",
        "patient_info": {
            "name": "John Doe",
            "mrn": "12345"
        }
    }
)

# Upload audio file
with open("rounds_audio.mp3", "rb") as audio_file:
    response = requests.post(
        "http://localhost:8000/upload-audio",
        files={"file": audio_file},
        data={"patient_info": json.dumps({"name": "John Doe", "mrn": "12345"})}
    )

# Upload image file
with open("whiteboard.jpg", "rb") as image_file:
    response = requests.post(
        "http://localhost:8000/upload-image",
        files={"file": image_file},
        data={"patient_info": json.dumps({"name": "John Doe", "mrn": "12345"})}
    )
```

## Note Format

The generated notes follow this structure:

```
---
[Patient Name / MRN / Date]

Subjective:
[Patient complaints, reported symptoms]

Objective:
- Vitals: [List of vital signs]
- Physical Exam Findings: [Key findings]
- Labs: [Lab results, highlighting abnormal values]
- Other Data (images): [Relevant information from images]

Assessment:
[Clinical impression and diagnosis]

Plan:
[Treatment plan and next steps]

Changes Since Last Note:
[New findings, resolved issues, trends]

Action Items / To-Do:
[List of pending tasks]

Discrepancies/Conflicts:
[Any conflicting data between sources]
---
```

## LLM Configuration

Leo uses GPT-4 by default but is designed to be easily configurable for different LLM providers. The current implementation includes:

1. OpenAI GPT-4 integration with:
   - Configurable temperature and token limits
   - Structured prompts for different tasks
   - Error handling and retry logic

2. Extensible architecture for adding new LLM providers:
   - Abstract `LLMInterface` class
   - Provider-specific implementations
   - Configuration-based provider selection

To add a new LLM provider:
1. Create a new class implementing `LLMInterface`
2. Add the provider to the configuration options
3. Update the `_initialize_llm` method in `Leo` class

## Development

The project structure:
- `leo.py`: Core functionality for processing clinical documentation
- `server.py`: FastAPI server implementation
- `config.py`: Configuration management
- `llm_interface.py`: LLM provider interface and implementations
- `requirements.txt`: Project dependencies
- `tests/`: Unit tests

## Testing

Run the test suite:
```bash
pytest
```

The test suite includes:
- Unit tests for core functionality
- Mock tests for LLM integration
- API endpoint tests
- Input validation tests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 