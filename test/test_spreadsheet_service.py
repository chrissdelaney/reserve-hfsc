import os
import json
from datetime import datetime, timezone

from gspread import Spreadsheet as Document, Worksheet
from dotenv import load_dotenv
import pytest

from app.spreadsheet_service import SpreadsheetService
from conftest import ss

load_dotenv()

CI_ENV = (os.getenv("CI", default="false") == "true")
CI_SKIP_MESSAGE = "taking a lighter touch to testing on the CI server, to reduce API usage and prevent rate limits"


STUDENT_NAME = "Louisa Baxter"
STUDENT_EMAIL = "lab357@georgetown.edu"
RES_DATE = "12/15/2023"
RES_TIME = "4:00pm"
RES_ROOM = 1


def test_add_reservation_record(ss):

    # Test add_reservation_to_table function
    ss.add_reservation_to_table(STUDENT_NAME, STUDENT_EMAIL, RES_DATE, RES_TIME, RES_ROOM)
    
    # Check if the reservation information is correctly added to the "table" sheet
    sheet_table = ss.get_sheet("table")
    row_index = sheet_table.col_values(1).index(RES_DATE) + 1
    cell_data_str = sheet_table.cell(row_index, RES_ROOM + 1).value  # Assuming the header is in row 1
    cell_data = json.loads(cell_data_str)

    assert cell_data[RES_TIME] == STUDENT_EMAIL


def test_remove_reservation_table(ss):
    # Test remove_reservation_from_table function
    ss.remove_reservation_from_table(STUDENT_NAME, STUDENT_EMAIL, RES_DATE, RES_TIME, RES_ROOM)

    # Check if the reservation information is correctly removed from the "table" sheet
    sheet_table = ss.get_sheet("table")
    row_index = sheet_table.col_values(1).index(RES_DATE) + 1
    cell_data_str = sheet_table.cell(row_index, RES_ROOM + 1).value  # Assuming the header is in row 1
    cell_data = json.loads(cell_data_str)

    assert cell_data[RES_TIME] == ""