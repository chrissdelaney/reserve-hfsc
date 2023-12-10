
import pytest
import os
from time import sleep

from dotenv import load_dotenv

from app.spreadsheet_service import SpreadsheetService
from web_app import create_app


load_dotenv()

# an example sheet that is being used for testing purposes:
GOOGLE_SHEETS_TEST_CREDENTIALS = os.path.join(os.path.dirname(__file__), "google-credentials-test.json")
GOOGLE_SHEETS_TEST_DOCUMENT_ID= os.getenv("GOOGLE_SHEETS_TEST_DOCUMENT_ID")
TEST_SLEEP = int(os.getenv("TEST_SLEEP", default="10"))

@pytest.fixture() # scope="module"
def ss():
    """spreadsheet service to use when testing"""
    ss = SpreadsheetService(credentials_filepath=GOOGLE_SHEETS_TEST_CREDENTIALS, document_id=GOOGLE_SHEETS_TEST_DOCUMENT_ID)


    yield ss

    # clean up:
    #ss.destroy_all("products")
    #ss.destroy_all("orders")
    #print("SLEEPING...")
    #sleep(TEST_SLEEP)



@pytest.fixture()
def test_client(ss):
    app = create_app(spreadsheet_service=ss)
    app.config.update({"TESTING": True})
    return app.test_client()

