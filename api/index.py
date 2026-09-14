import os
import sys

# Ensure root directory is on Python path so backend imports resolve seamlessly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app

# Vercel serverless entry point
app = create_app()
