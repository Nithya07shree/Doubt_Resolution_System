from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DoubtRequest(BaseModel):
    student_query: str = Field(
        ..., 
        min_length=10, 
        max_length=4000, 
        description="The student's complex query or academic doubt."
    )

class IntentOutput(BaseModel):
    topic: str = Field(..., description="Core subject area or topic identified.")
    skill_level: str = Field(..., description="Student skill level: Beginner, Intermediate, or Advanced.")
    intent_type: str = Field(..., description="Primary student intent: Conceptual, Practical/Troubleshooting, or Academic.")
    key_terms: List[str] = Field(default=[], description="List of key technical concepts/terms extracted.")

class ValidationOutput(BaseModel):
    valid: bool = Field(..., description="Whether the payload met all quality metrics and structural standards.")
    feedback: List[str] = Field(default=[], description="Detailed critique or corrective points.")
    score: int = Field(..., description="Rating score from 0 to 100 on structure and quality.")

class DoubtResponse(BaseModel):
    id: str
    student_query: str
    intent_output: Optional[Dict[str, Any]] = None
    explanation_output: Optional[str] = None
    simplification_output: Optional[str] = None
    example_output: Optional[str] = None
    validation_output: Optional[Dict[str, Any]] = None
    diff_output: Optional[Dict[str, Any]] = None
    token_counts: Optional[Dict[str, Any]] = None
    execution_latency_ms: float
    timestamp: datetime

    class Config:
        from_attributes = True

class HistoryResponseItem(BaseModel):
    id: str
    student_query: str
    topic: Optional[str] = None
    skill_level: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
