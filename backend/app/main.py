import time
import re
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# App imports
from app.config import settings
from app.database import engine, Base, get_db
from app.logger import get_logger
from app.models import DoubtResolution
from app.schemas import DoubtRequest, DoubtResponse, HistoryResponseItem
from app.utils.diff_engine import compute_diff

# Agents imports
from app.agents.intent_agent import IntentAgent
from app.agents.explanation_agent import ExplanationAgent
from app.agents.simplification_agent import SimplificationAgent
from app.agents.example_agent import ExampleAgent
from app.agents.validation_agent import ValidationAgent

# Initialize structured logger
logger = get_logger("main")

# Auto-create database tables on application start
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Successfully synchronized database schema with SQLite metadata.")
except Exception as e:
    logger.critical(f"Failed to synchronize database schemas: {e}", exc_info=True)

# Create FastAPI app instance
app = FastAPI(
    title="Multi-Agent AI Doubt Resolution System",
    description="Sleek sequential pipeline architecture powered by FastAPI and OpenAI.",
    version="1.0.0"
)

# Robust CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sanitize_query(query: str) -> str:
    """
    Cleans incoming queries of hazardous characters and scripts to mitigate
    prompt injection vulnerabilities and cross-site scripting (XSS).
    """
    # Remove HTML and raw script elements
    clean = re.sub(r'<[^>]*>', '', query)

    # Detect common prompt override patterns and convert them into safe text
    injection_patterns = [
        r"(?i)\bignore\b.*\bprevious\b",
        r"(?i)\bignore\b.*\binstructions\b",
        r"(?i)\bsystem\b.*\bprompt\b",
        r"(?i)\byou\b.*\bare\b.*\ban\b.*\bai\b",
        r"(?i)\bnew\b.*\binstructions\b",
        r"(?i)\bdelete\b.*\bdatabase\b",
        r"(?i)\bdrop\b.*\btable\b"
    ]

    for pattern in injection_patterns:
        if re.search(pattern, clean):
            logger.warning(f"Potential prompt injection pattern detected: '{pattern}'")
            clean = re.sub(pattern, "[CLEANED SECURE BLOCK]", clean)

    return clean.strip()

@app.post("/api/resolve", response_model=DoubtResponse, status_code=status.HTTP_201_CREATED)
def resolve_doubt(request: DoubtRequest, db: Session = Depends(get_db)):
    """
    Ingests student doubt and processes it sequentially through the multi-agent framework.
    Includes input sanitization, exactly one quality validation retry, word diffing, and database logging.
    """
    start_time = time.time()
    raw_query = request.student_query
    
    logger.info(f"Received resolve doubt request. Query length: {len(raw_query)}")
    
    # 1. Clean query
    clean_query = sanitize_query(raw_query)
    
    # Instantiate agents
    intent_agent = IntentAgent()
    explanation_agent = ExplanationAgent()
    simplification_agent = SimplificationAgent()
    example_agent = ExampleAgent()
    validation_agent = ValidationAgent()
    
    token_usage = {
        "intent_agent": {"prompt": 0, "completion": 0},
        "explanation_agent": {"prompt": 0, "completion": 0},
        "simplification_agent": {"prompt": 0, "completion": 0},
        "example_agent": {"prompt": 0, "completion": 0},
        "validation_agent": {"prompt": 0, "completion": 0},
        "total": {"prompt": 0, "completion": 0}
    }

    # Helper function to accumulate tokens
    def record_tokens(agent_name: str, p_tok: int, c_tok: int):
        token_usage[agent_name]["prompt"] += p_tok
        token_usage[agent_name]["completion"] += c_tok
        token_usage["total"]["prompt"] += p_tok
        token_usage["total"]["completion"] += c_tok

    try:
        # A. Intent Agent
        intent_output, p_tok, c_tok = intent_agent.run(clean_query)
        record_tokens("intent_agent", p_tok, c_tok)
        
        # B. Explanation Agent
        explanation, p_tok, c_tok = explanation_agent.run(clean_query, intent_output)
        record_tokens("explanation_agent", p_tok, c_tok)
        
        # C. Simplification Agent
        simplification, p_tok, c_tok = simplification_agent.run(clean_query, explanation, intent_output)
        record_tokens("simplification_agent", p_tok, c_tok)
        
        # D. Example Agent
        example, p_tok, c_tok = example_agent.run(clean_query, simplification, intent_output)
        record_tokens("example_agent", p_tok, c_tok)
        
        # E. Validation Agent
        val_report, p_tok, c_tok = validation_agent.run(clean_query, explanation, simplification, example)
        record_tokens("validation_agent", p_tok, c_tok)
        
        # --- Internal Retry Loop (Exactly One Attempt) ---
        if not val_report.get("valid", True):
            feedback_str = "\n".join([f"- {f}" for f in val_report.get("feedback", [])])
            logger.warning(
                f"Validation failed (Score: {val_report.get('score')}). "
                f"Initiating single automatic internal correction loop with feedback:\n{feedback_str}"
            )
            
            # Re-run Pipeline with feedback
            explanation, p_tok, c_tok = explanation_agent.run(
                clean_query, intent_output, validation_feedback=feedback_str
            )
            record_tokens("explanation_agent", p_tok, c_tok)
            
            simplification, p_tok, c_tok = simplification_agent.run(
                clean_query, explanation, intent_output, validation_feedback=feedback_str
            )
            record_tokens("simplification_agent", p_tok, c_tok)
            
            example, p_tok, c_tok = example_agent.run(
                clean_query, simplification, intent_output, validation_feedback=feedback_str
            )
            record_tokens("example_agent", p_tok, c_tok)
            
            # Re-validate
            val_report, p_tok, c_tok = validation_agent.run(clean_query, explanation, simplification, example)
            record_tokens("validation_agent", p_tok, c_tok)
            logger.info(f"Post-retry validation outcome: valid={val_report.get('valid')}, score={val_report.get('score')}")

        # F. Compute Diff between academic explanation and analogy simplification
        diff_report = compute_diff(explanation, simplification)
        
        # Record execution duration
        latency_ms = (time.time() - start_time) * 1000.0
        
        # Save to database
        db_resolution = DoubtResolution(
            student_query=raw_query,
            intent_output=intent_output,
            explanation_output=explanation,
            simplification_output=simplification,
            example_output=example,
            validation_output=val_report,
            diff_output=diff_report,
            token_counts=token_usage,
            execution_latency_ms=latency_ms
        )
        
        db.add(db_resolution)
        db.commit()
        db.refresh(db_resolution)
        
        logger.info(f"Resolution transaction committed successfully. Record ID: {db_resolution.id}")
        return db_resolution

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to execute complete agent doubt resolution workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during agent execution: {str(e)}"
        )

@app.get("/api/resolutions", response_model=List[HistoryResponseItem])
def get_resolutions_history(db: Session = Depends(get_db)):
    """
    Fetches the historical list of resolved doubts, sorted by recent submissions.
    """
    try:
        resolutions = db.query(DoubtResolution).order_by(DoubtResolution.timestamp.desc()).all()
        history = []
        for r in resolutions:
            topic = r.intent_output.get("topic") if r.intent_output else "General"
            skill_level = r.intent_output.get("skill_level") if r.intent_output else "Intermediate"
            history.append(
                HistoryResponseItem(
                    id=r.id,
                    student_query=r.student_query,
                    topic=topic,
                    skill_level=skill_level,
                    timestamp=r.timestamp
                )
            )
        return history
    except Exception as e:
        logger.error(f"Error querying history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading resolutions database records."
        )

@app.get("/api/resolutions/{resolution_id}", response_model=DoubtResponse)
def get_resolution_details(resolution_id: str, db: Session = Depends(get_db)):
    """
    Fetches a specific doubt resolution payload in full detail by its unique ID.
    """
    resolution = db.query(DoubtResolution).filter(DoubtResolution.id == resolution_id).first()
    if not resolution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resolution record with ID {resolution_id} not found."
        )
    return resolution
