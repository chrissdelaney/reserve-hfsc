import pytest
import os
import json

from dotenv import load_dotenv

from app.spreadsheet_service import SpreadsheetService
from web_app import create_app

# Load environment variables from .env file, if present
load_dotenv()

# Get the document ID from environment variables
GOOGLE_SHEETS_TEST_DOCUMENT_ID = os.getenv("GOOGLE_SHEETS_TEST_DOCUMENT_ID")
TEST_SLEEP = int(os.getenv("TEST_SLEEP", default="10"))

def get_google_credentials():
    # Check for the file path of the credentials in an environment variable
    credentials_file_path = os.getenv('GOOGLE_CREDENTIALS_FILEPATH')
    if credentials_file_path:
        # Use the credentials file created by the GitHub Action
        with open(credentials_file_path) as f:
            return json.load(f)
    else:
        # Locally, use the 'google-credentials-test.json' file
        credentials_filepath = os.path.join(os.path.dirname(__file__), "google-credentials-test.json")
        with open(credentials_filepath) as f:
            return json.load(f)

@pytest.fixture()  # scope="module"
def ss():
    """spreadsheet service to use when testing"""
    credentials = get_google_credentials()
    ss = SpreadsheetService(credentials=credentials, document_id=GOOGLE_SHEETS_TEST_DOCUMENT_ID)
    yield ss

@pytest.fixture()
def test_client(ss):
    """A test client for the Flask web app"""
    app = create_app(spreadsheet_service=ss)
    app.config.update({"TESTING": True})
    return app.test_client()
