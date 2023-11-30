
import pytest
import os
from time import sleep

from dotenv import load_dotenv

from app.spreadsheet_service import SpreadsheetService
from web_app import create_app


load_dotenv()

# an example sheet that is being used for testing purposes:
GOOGLE_SHEETS_TEST_DOCUMENT_ID= os.getenv("GOOGLE_SHEETS_TEST_DOCUMENT_ID", default="1TZCr9x6CZmlccSKgpOkAIE6dCfRmS_83tSlb_GyALsw")
TEST_SLEEP = int(os.getenv("TEST_SLEEP", default="10"))

# it would be nice to reset the database for each test, but we are hitting rate limits
# we could consider using a single instance of the test database, but maybe that's worse than sleeping after each test?
@pytest.fixture() # scope="module"
def ss():
    """spreadsheet service to use when testing"""
    ss = SpreadsheetService(document_id=GOOGLE_SHEETS_TEST_DOCUMENT_ID)

    # setup / remove any records that may exist:
    ss.destroy_all("products")
    ss.destroy_all("orders")

    # seed default products:
    ss.seed_products()

    yield ss

    # clean up:
    #ss.destroy_all("products")
    #ss.destroy_all("orders")
    print("SLEEPING...")
    sleep(TEST_SLEEP)



@pytest.fixture()
def test_client(ss):
    app = create_app(spreadsheet_service=ss)
    app.config.update({"TESTING": True})
    return app.test_client()
