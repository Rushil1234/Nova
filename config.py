from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    """Configuration for LLM settings"""
    provider: str = "openai"  # Can be "openai", "anthropic", "google", etc.
    model: str = "gpt-4"
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    temperature: float = 0.3
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class ClinicalNoteConfig(BaseModel):
    """Configuration for clinical note generation"""
    default_format: str = "SOAP"  # Can be "SOAP" or "SBAR"
    include_vitals: bool = True
    include_labs: bool = True
    include_medications: bool = True
    highlight_abnormal: bool = True
    max_note_length: int = 4000

class Config(BaseModel):
    """Main configuration class"""
    llm: LLMConfig = LLMConfig()
    clinical_note: ClinicalNoteConfig = ClinicalNoteConfig()
    
    model_config = {
        "env_prefix": "LEO_"
    } 