import os
import sys

# Dynamic path injection to guarantee Vercel's serverless runtime 
# can locate the 'app' package regardless of execution context.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app.main import app

# Expose the FastAPI app instance for the Vercel ASGI gateway
# Vercel's Python builder automatically detects and binds to this 'app' object.
