import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, Float, DateTime
from app.database import Base

class DoubtResolution(Base):
    __tablename__ = "doubt_resolutions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    student_query = Column(Text, nullable=False)
    
    # Store specialized outputs from the sequential agents
    intent_output = Column(JSON, nullable=True)         # JSON profiling (topic, skill, etc.)
    explanation_output = Column(Text, nullable=True)      # Deep academic text
    simplification_output = Column(Text, nullable=True)   # Analogy & simplified plain text
    example_output = Column(Text, nullable=True)          # Real-world concrete scenario
    validation_output = Column(JSON, nullable=True)       # Quality evaluation report details
    
    # Diff outputs and metadata
    diff_output = Column(JSON, nullable=True)             # Word-level/line-level diff results
    
    # Metrics
    token_counts = Column(JSON, nullable=True)            # Prompt & response token tracking
    execution_latency_ms = Column(Float, default=0.0)    # Latency tracking
    
    # Audit log
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        """Converts model data to standard dictionary for serialization."""
        return {
            "id": self.id,
            "student_query": self.student_query,
            "intent_output": self.intent_output,
            "explanation_output": self.explanation_output,
            "simplification_output": self.simplification_output,
            "example_output": self.example_output,
            "validation_output": self.validation_output,
            "diff_output": self.diff_output,
            "token_counts": self.token_counts,
            "execution_latency_ms": self.execution_latency_ms,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
