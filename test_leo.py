import pytest
from datetime import datetime
from leo import Leo, ClinicalInput, ProgressNote
from config import Config, LLMConfig
from unittest.mock import Mock, patch

@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing"""
    mock = Mock()
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
    mock.process_clinical_image.return_value = {
        "vitals": ["BP: 120/80", "HR: 72"],
        "labs": ["WBC: 8.5"],
        "medications": ["Lisinopril 10mg"],
        "other_data": ["Whiteboard: Room 302"]
    }
    mock.compare_notes.return_value = {
        "new_findings": ["Improved breathing"],
        "resolved_issues": ["Fever resolved"],
        "trends": ["BP trending down"],
        "significant_changes": ["O2 sat improved to 98%"]
    }
    return mock

@pytest.fixture
def test_config():
    """Create test configuration"""
    return Config(
        llm=LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key="test_key",
            temperature=0.3
        )
    )

def test_leo_initialization(test_config, mock_llm):
    """Test Leo class initialization"""
    leo = Leo(test_config, llm=mock_llm)
    assert isinstance(leo.note_template, dict)
    assert "subjective" in leo.note_template
    assert "objective" in leo.note_template
    assert "assessment" in leo.note_template
    assert "plan" in leo.note_template

def test_process_input_empty(test_config, mock_llm):
    """Test processing empty input"""
    leo = Leo(test_config, llm=mock_llm)
    input_data = ClinicalInput()
    note = leo.process_input(input_data)
    
    assert isinstance(note, ProgressNote)
    assert note.date is not None
    assert note.subjective == ""
    assert isinstance(note.objective, dict)
    assert note.assessment == ""
    assert note.plan == ""
    assert note.changes_since_last_note == ""
    assert isinstance(note.action_items, list)
    assert isinstance(note.discrepancies, list)

def test_process_input_with_audio(test_config, mock_llm):
    """Test processing input with audio transcript"""
    leo = Leo(test_config, llm=mock_llm)
    input_data = ClinicalInput(
        transcribed_audio="Doctor: Patient reports improved breathing. BP 120/80, HR 72.",
        patient_info={"name": "John Doe", "mrn": "12345"}
    )
    note = leo.process_input(input_data)
    
    assert isinstance(note, ProgressNote)
    assert note.patient_name == "John Doe"
    assert note.mrn == "12345"
    assert "BP: 120/80" in note.objective["vitals"]
    assert "HR: 72" in note.objective["vitals"]
    assert "Lisinopril 10mg" in note.action_items[0]

def test_process_input_with_image(test_config, mock_llm):
    """Test processing input with image text"""
    leo = Leo(test_config, llm=mock_llm)
    input_data = ClinicalInput(
        extracted_text_from_images="BP: 120/80, HR: 72, WBC: 8.5",
        patient_info={"name": "John Doe", "mrn": "12345"}
    )
    note = leo.process_input(input_data)
    
    assert isinstance(note, ProgressNote)
    assert note.patient_name == "John Doe"
    assert note.mrn == "12345"
    assert "BP: 120/80" in note.objective["vitals"]
    assert "HR: 72" in note.objective["vitals"]
    assert "WBC: 8.5" in note.objective["labs"]
    assert "Whiteboard: Room 302" in note.objective["other_data"]

def test_compare_notes(test_config, mock_llm):
    """Test comparing notes"""
    leo = Leo(test_config, llm=mock_llm)
    input_data = ClinicalInput(
        transcribed_audio="Doctor: Patient reports improved breathing.",
        previous_note="Previous note content",
        patient_info={"name": "John Doe", "mrn": "12345"}
    )
    note = leo.process_input(input_data)
    
    assert isinstance(note, ProgressNote)
    assert "Improved breathing" in note.changes_since_last_note
    assert "Fever resolved" in note.changes_since_last_note
    assert "BP trending down" in note.changes_since_last_note
    assert "O2 sat improved to 98%" in note.changes_since_last_note

def test_format_note(test_config):
    """Test note formatting"""
    leo = Leo(test_config)
    note = ProgressNote(
        patient_name="John Doe",
        mrn="12345",
        date=datetime.now(),
        subjective="Patient reports improved breathing",
        objective={
            "vitals": ["BP: 120/80", "HR: 72"],
            "physical_exam": ["Lungs clear"],
            "labs": ["WBC: 8.5"],
            "other_data": []
        },
        assessment="Improving respiratory status",
        plan="Continue current treatment",
        changes_since_last_note="Breathing improved",
        action_items=["Follow up in 24 hours"],
        discrepancies=[]
    )
    
    formatted_note = leo.format_note(note)
    assert isinstance(formatted_note, str)
    assert "John Doe" in formatted_note
    assert "12345" in formatted_note
    assert "Subjective:" in formatted_note
    assert "Objective:" in formatted_note
    assert "Assessment:" in formatted_note
    assert "Plan:" in formatted_note
    assert "BP: 120/80" in formatted_note
    assert "HR: 72" in formatted_note
    assert "WBC: 8.5" in formatted_note
    assert "Follow up in 24 hours" in formatted_note 