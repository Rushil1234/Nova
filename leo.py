from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json
from config import Config
from llm_interface import LLMInterface, OpenAILLM

class ClinicalInput(BaseModel):
    """Model for clinical input data"""
    transcribed_audio: Optional[str] = None
    extracted_text_from_images: Optional[str] = None
    previous_note: Optional[str] = None
    patient_info: Optional[Dict[str, Any]] = None

class ProgressNote(BaseModel):
    """Model for structured progress note"""
    patient_name: Optional[str] = None
    mrn: Optional[str] = None
    date: datetime
    subjective: str
    objective: Dict[str, Any]
    assessment: str
    plan: str
    changes_since_last_note: str
    action_items: List[str]
    discrepancies: List[str]

class Leo:
    """Clinical Documentation AI Assistant"""
    
    def __init__(self, config: Optional[Config] = None, llm: Optional[LLMInterface] = None):
        self.config = config or Config()
        self.llm = llm or self._initialize_llm()
        self.note_template = {
            "subjective": "",
            "objective": {
                "vitals": [],
                "physical_exam": [],
                "labs": [],
                "other_data": []
            },
            "assessment": "",
            "plan": "",
            "changes_since_last_note": "",
            "action_items": [],
            "discrepancies": []
        }

    def _initialize_llm(self) -> LLMInterface:
        """Initialize the appropriate LLM based on configuration"""
        if self.config.llm.provider == "openai":
            return OpenAILLM(self.config.llm)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm.provider}")

    def process_input(self, input_data: ClinicalInput) -> ProgressNote:
        """
        Process clinical input data and generate a structured progress note
        """
        # Initialize note with basic structure
        note = self.note_template.copy()
        
        # Process transcribed audio
        if input_data.transcribed_audio:
            self._process_audio_transcript(input_data.transcribed_audio, note)
        
        # Process extracted text from images
        if input_data.extracted_text_from_images:
            self._process_image_text(input_data.extracted_text_from_images, note)
        
        # Compare with previous note if available
        if input_data.previous_note:
            self._compare_with_previous_note(input_data.previous_note, note)
        
        # Create final progress note
        return ProgressNote(
            patient_name=input_data.patient_info.get("name") if input_data.patient_info else None,
            mrn=input_data.patient_info.get("mrn") if input_data.patient_info else None,
            date=datetime.now(),
            subjective=note["subjective"],
            objective=note["objective"],
            assessment=note["assessment"],
            plan=note["plan"],
            changes_since_last_note=note["changes_since_last_note"],
            action_items=note["action_items"],
            discrepancies=note["discrepancies"]
        )

    def _process_audio_transcript(self, transcript: str, note: Dict[str, Any]) -> None:
        """
        Process transcribed audio and extract relevant clinical information
        """
        try:
            # Process transcript using LLM
            result = self.llm.process_clinical_conversation(transcript)
            
            # Update note with extracted information
            note["subjective"] = result.get("subjective", "")
            note["objective"]["vitals"] = result.get("vitals", [])
            note["objective"]["labs"] = result.get("labs", [])
            note["assessment"] = result.get("assessment", "")
            note["plan"] = result.get("plan", "")
            
            # Add any medications to action items
            for med in result.get("medications", []):
                note["action_items"].append(f"Review medication: {med}")
                
        except Exception as e:
            note["discrepancies"].append(f"Error processing audio transcript: {str(e)}")

    def _process_image_text(self, image_text: str, note: Dict[str, Any]) -> None:
        """
        Process extracted text from images and extract relevant clinical information
        """
        try:
            # Process image text using LLM
            result = self.llm.process_clinical_image(image_text)
            
            # Update note with extracted information
            note["objective"]["vitals"] = result.get("vitals", [])
            note["objective"]["labs"] = result.get("labs", [])
            note["objective"]["other_data"] = result.get("other_data", [])
            
            # Add any medications to action items
            for med in result.get("medications", []):
                note["action_items"].append(f"Review medication: {med}")
                
        except Exception as e:
            note["discrepancies"].append(f"Error processing image text: {str(e)}")

    def _compare_with_previous_note(self, previous_note: str, current_note: Dict[str, Any]) -> None:
        """
        Compare current note with previous note to identify changes
        """
        try:
            # Convert current note to string for comparison
            current_note_str = self.format_note(ProgressNote(
                date=datetime.now(),
                subjective=current_note["subjective"],
                objective=current_note["objective"],
                assessment=current_note["assessment"],
                plan=current_note["plan"],
                changes_since_last_note="",
                action_items=current_note["action_items"],
                discrepancies=current_note["discrepancies"]
            ))
            
            # Compare notes using LLM
            result = self.llm.compare_notes(previous_note, current_note_str)
            
            # Update note with comparison results
            changes = []
            if result.get("new_findings"):
                changes.append("New findings: " + ", ".join(result["new_findings"]))
            if result.get("resolved_issues"):
                changes.append("Resolved issues: " + ", ".join(result["resolved_issues"]))
            if result.get("trends"):
                changes.append("Trends: " + ", ".join(result["trends"]))
            if result.get("significant_changes"):
                changes.append("Significant changes: " + ", ".join(result["significant_changes"]))
            
            current_note["changes_since_last_note"] = "\n".join(changes)
            
        except Exception as e:
            current_note["discrepancies"].append(f"Error comparing notes: {str(e)}")

    def format_note(self, note: ProgressNote) -> str:
        """
        Format the progress note according to the specified template
        """
        header = f"---\n"
        if note.patient_name or note.mrn:
            header += f"**{note.patient_name or 'Unknown'} / {note.mrn or 'N/A'} / {note.date.strftime('%Y-%m-%d')}**\n\n"
        
        formatted_note = header
        formatted_note += f"**Subjective:**\n{note.subjective}\n\n"
        
        formatted_note += "**Objective:**\n"
        formatted_note += f"- **Vitals:** {', '.join(note.objective['vitals'])}\n"
        formatted_note += f"- **Physical Exam Findings:** {', '.join(note.objective['physical_exam'])}\n"
        formatted_note += f"- **Labs:** {', '.join(note.objective['labs'])}\n"
        formatted_note += f"- **Other Data (images):** {', '.join(note.objective['other_data'])}\n\n"
        
        formatted_note += f"**Assessment:**\n{note.assessment}\n\n"
        formatted_note += f"**Plan:**\n{note.plan}\n\n"
        formatted_note += f"**Changes Since Last Note:**\n{note.changes_since_last_note}\n\n"
        
        if note.action_items:
            formatted_note += "**Action Items / To-Do:**\n"
            for item in note.action_items:
                formatted_note += f"- {item}\n"
            formatted_note += "\n"
        
        if note.discrepancies:
            formatted_note += "**Discrepancies/Conflicts:**\n"
            for discrepancy in note.discrepancies:
                formatted_note += f"- {discrepancy}\n"
            formatted_note += "\n"
        
        formatted_note += "---"
        return formatted_note 