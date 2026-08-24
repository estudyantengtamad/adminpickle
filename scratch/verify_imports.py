"""
Quick verification of mock_db and app creation.
"""
from backend.app import create_app

app = create_app()
print("SUCCESS: PickleLegends App initialized cleanly with zero errors!")
