import os
import json
from datetime import datetime, timezone

from gspread import Spreadsheet as Document, Worksheet
from dotenv import load_dotenv
import pytest

from app.spreadsheet_service import SpreadsheetService
from app.spreadsheet_service import ReservatonTakenException, ReservatonEmptyException, InvalidDateException
from conftest import ss

load_dotenv()


#TESTING STATIC METHODS
def test_timestamp(ss):
    assert isinstance(ss.generate_timestamp(), str)

def test_timestamp_parse(ss):
    time_str = ss.generate_timestamp()
    assert isinstance(ss.parse_timestamp(time_str), datetime)

def test_get_next_week_dates(ss):
    dates_list = ss.get_next_week_dates()

    assert isinstance(dates_list, list)
    assert len(dates_list) == 7
    assert all(isinstance(date, str) for date in dates_list)


# TESTING SPREADSHEET METHODS
STUDENT_NAME = "Louisa Baxter"
STUDENT_EMAIL = "lab357@georgetown.edu"
RES_DATE = "12/15/2023"
RES_TIME = "4:00pm"
RES_ROOM = 1

def test_get_sheet(ss):
    assert isinstance(ss.get_sheet("table"), Worksheet)

def test_get_student_reservations(ss):
    assert isinstance(ss.get_student_reservations(STUDENT_EMAIL), list)

def test_add_reservation_record(ss):
    ss.add_reservation_to_table(STUDENT_NAME, STUDENT_EMAIL, RES_DATE, RES_TIME, RES_ROOM)
    
    #check if the reservation information is correctly added to the "table" sheet
    sheet_table = ss.get_sheet("table")
    row_index = sheet_table.col_values(1).index(RES_DATE) + 1
    cell_data_str = sheet_table.cell(row_index, RES_ROOM + 1).value  # Assuming the header is in row 1
    cell_data = json.loads(cell_data_str)

    assert cell_data[RES_TIME] == STUDENT_EMAIL

def test_add_reservation_error(ss):
    #checks to see if reservation taken exception is thrown, as we are trying to make it with the same date/time/room combo
    with pytest.raises(ReservatonTakenException): 
        ss.add_reservation_to_table(STUDENT_NAME, STUDENT_EMAIL, RES_DATE, RES_TIME, RES_ROOM)


def test_get_schedule_by_date(ss):
    schedule = ss.get_schedule_by_date("12/15/2023")

    assert isinstance(schedule, dict)
    assert len(schedule["data"]) == 12

def test_get_schedule_error(ss):
    with pytest.raises(InvalidDateException):
        ss.get_schedule_by_date("12/31/9999")


def test_remove_reservation_table(ss):
    ss.remove_reservation_from_table(STUDENT_NAME, STUDENT_EMAIL, RES_DATE, RES_TIME, RES_ROOM)

    #check if the reservation information is correctly removed from the "table" sheet
    sheet_table = ss.get_sheet("table")
    row_index = sheet_table.col_values(1).index(RES_DATE) + 1
    cell_data_str = sheet_table.cell(row_index, RES_ROOM + 1).value  # Assuming the header is in row 1
    cell_data = json.loads(cell_data_str)

    assert cell_data[RES_TIME] == ""

def test_remove_reservation_error(ss):
    #checks to see if reservation empty exception is thrown, as we are trying to make it with the same date/time/room combo
    with pytest.raises(ReservatonEmptyException):
        ss.remove_reservation_from_table(STUDENT_NAME, STUDENT_EMAIL, RES_DATE, RES_TIME, RES_ROOM)
   