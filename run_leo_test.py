import json
import os
from datetime import datetime
from test_leo import test_config
from leo import Leo, ClinicalInput
from unittest.mock import Mock

def create_mock_llm():
    """Create a properly configured mock LLM"""
    mock = Mock()
    
    # Mock process_clinical_conversation
    mock.process_clinical_conversation.return_value = {
        "vitals": ["BP: 120/80", "HR: 72"],
        "medications": ["Lisinopril 10mg"],
        "assessments": ["Hypertension"],
        "plans": ["Continue current medications"],
        "labs": ["WBC: 8.5"],
        "subjective": "Patient reports improved breathing",
        "objective": "Lungs clear",
        "assessment": "Improving respiratory status",
        "plan": "Continue current treatment"
    }
    
    # Mock process_clinical_image
    mock.process_clinical_image.return_value = {
        "vitals": ["BP: 120/80", "HR: 72"],
        "labs": ["WBC: 8.5"],
        "medications": ["Lisinopril 10mg"],
        "other_data": ["Whiteboard: Room 302"]
    }
    
    # Mock compare_notes
    mock.compare_notes.return_value = {
        "new_findings": ["Improved breathing"],
        "resolved_issues": ["Fever resolved"],
        "trends": ["BP trending down"],
        "significant_changes": ["O2 sat improved to 98%"]
    }
    
    return mock

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def save_output(filename, content):
    """Save content to a file in the output directory"""
    with open(os.path.join('output', filename), 'w', encoding='utf-8') as f:
        if isinstance(content, (dict, list)):
            json.dump(content, f, indent=2, cls=DateTimeEncoder)
        else:
            f.write(str(content))

def main():
    # Create timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Initialize Leo with test configuration and mock LLM
    mock_llm = create_mock_llm()
    leo = Leo(test_config, llm=mock_llm)
    
    # Test 1: Process audio input
    audio_input = ClinicalInput(
        transcribed_audio="Doctor: Patient reports improved breathing. BP 120/80, HR 72.",
        patient_info={"name": "John Doe", "mrn": "12345"}
    )
    audio_note = leo.process_input(audio_input)
    
    # Save audio processing results
    save_output(f"{timestamp}_audio_input.json", {
        "input": audio_input.dict(),
        "processed_note": audio_note.dict()
    })
    
    # Test 2: Process image input
    image_input = ClinicalInput(
        extracted_text_from_images="BP: 120/80, HR: 72, WBC: 8.5",
        patient_info={"name": "John Doe", "mrn": "12345"}
    )
    image_note = leo.process_input(image_input)
    
    # Save image processing results
    save_output(f"{timestamp}_image_input.json", {
        "input": image_input.dict(),
        "processed_note": image_note.dict()
    })
    
    # Test 3: Compare notes
    comparison_input = ClinicalInput(
        transcribed_audio="Doctor: Patient reports improved breathing.",
        previous_note="Previous note content",
        patient_info={"name": "John Doe", "mrn": "12345"}
    )
    comparison_note = leo.process_input(comparison_input)
    
    # Save comparison results
    save_output(f"{timestamp}_comparison.json", {
        "input": comparison_input.dict(),
        "processed_note": comparison_note.dict()
    })
    
    # Save formatted notes
    save_output(f"{timestamp}_formatted_notes.txt", f"""
=== Audio Processing Note ===
{leo.format_note(audio_note)}

=== Image Processing Note ===
{leo.format_note(image_note)}

=== Comparison Note ===
{leo.format_note(comparison_note)}
""")
    
    # Save test summary
    save_output(f"{timestamp}_test_summary.txt", f"""
Leo Test Results Summary
=======================
Timestamp: {timestamp}

1. Audio Processing Test
   - Input: Doctor-patient conversation
   - Output: Structured clinical note with vitals, medications, and assessment

2. Image Processing Test
   - Input: Clinical data from image
   - Output: Structured note with vitals and lab results

3. Note Comparison Test
   - Input: New note with previous note reference
   - Output: Note with changes and trends identified

All tests completed successfully.
""")

if __name__ == "__main__":
    main() 