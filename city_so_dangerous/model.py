from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


class HazardType(str, Enum):
    FIRE = "FIRE"
    CRIME = "CRIME" 
    TRAFFIC = "TRAFFIC"
    WEATHER = "WEATHER"
    CONSTRUCTION = "CONSTRUCTION"
    FLOOD = "FLOOD"
    EARTHQUAKE = "EARTHQUAKE"
    OTHER = "OTHER"


class DegreeOfRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM" 
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HazardInfo(BaseModel):
    degree_of_risk: DegreeOfRisk
    description: str = Field(description="Description of the hazard")


class AnalysisResult(BaseModel):
    hazards: Dict[HazardType, HazardInfo] = Field(
        description="Dictionary mapping hazard types to their information"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        description="Overall confidence in the analysis (0.0-1.0)"
    )


class HazardAnalysisState(TypedDict):
    """State for the hazard analysis graph"""
    image_data: str  # Base64 encoded image
    messages: List[BaseMessage]  # For LLM conversation
    raw_analysis: Optional[Dict[str, Any]]  # Raw LLM output
    validated_result: Optional[AnalysisResult]  # Validated analysis result
    needs_retry: bool  # Flag for retry logic
    retry_count: int  # Number of retries attempted
    error: Optional[str]  # Error message if any


class GraphConfig(BaseModel):
    """Configuration for the analysis graph"""
    max_retries: int = Field(default=2, description="Maximum retry attempts")
    llm_model: str = Field(default="gpt-4o", description="LLM model to use")
    temperature: float = Field(default=0.1, description="LLM temperature")
    confidence_threshold: float = Field(
        default=0.7, 
        description="Minimum confidence score to accept result"
    )