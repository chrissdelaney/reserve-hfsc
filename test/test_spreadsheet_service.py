import os
import json
from datetime import datetime, timezone

from gspread import Spreadsheet as Document, Worksheet
from dotenv import load_dotenv
import pytest

from app.spreadsheet_service import SpreadsheetService
from conftest import ss as spreadsheet_service

load_dotenv()

CI_ENV = (os.getenv("CI", default="false") == "true")
CI_SKIP_MESSAGE = "taking a lighter touch to testing on the CI server, to reduce API usage and prevent rate limits"



def test_reservations(ss):
    student_name = "Louisa Baxter"
    student_email = "lab357@georgetown.edu"
    res_date = "12/15/2023"
    res_time = "3:00pm"
    res_room = 1

    #print(ss.client.auth.service_account_email)
    # Test add_reservation_to_table function
    ss.add_reservation_to_table(student_name, student_email, res_date, res_time, res_room, sheet_name = "test_table")
    
     # Check if the reservation information is correctly added to the "table" sheet
    sheet_table = ss.get_sheet("test_table")
    cell_value = sheet_table.cell(1, res_room + 1).value  # Assuming the header is in row 1
    cell_data = json.loads(cell_value)
    assert cell_data[res_time] == student_email

    # Test add_reservation_record function
    ss.add_reservation_record(student_name, student_email, res_date, res_time, res_room, sheet_name="test_reservations")

    # Check if the reservation information is correctly added to the "test_reservations" sheet
    sheet_reservations = ss.get_sheet("test_reservations")
    last_row = sheet_reservations.row_values(sheet_reservations.row_count)
    assert last_row[1:] == [student_name, student_email, res_date, res_time, str(res_room)]


def test_remove_reservation_table(ss):
    student_name = "John Doe"
    student_email = "xyz123@georgetown.edu"
    res_date = "12/16/2023"
    res_time = "4:00pm"
    res_room = 2

    # Test add_reservation_to_table function
    ss.add_reservation_to_table(student_name, student_email, res_date, res_time, res_room, sheet_name="test_table")

    # Check if the reservation information is correctly added to the test sheet
    sheet_table = ss.get_sheet("test_table")
    cell_value_before_removal = sheet_table.cell(1, res_room + 1).value  #the header is in row 1
    cell_data_before_removal = json.loads(cell_value_before_removal)
    assert cell_data_before_removal[res_time] == student_email

    # Test remove_reservation_from_table function
    ss.remove_reservation_from_table(student_name, student_email, res_date, res_time, res_room, sheet_name="test_table")

    # Check if the reservation information is correctly removed from the test sheet
    cell_value_after_removal = sheet_table.cell(1, res_room + 1).value
    cell_data_after_removal = json.loads(cell_value_after_removal)
    assert cell_data_after_removal[res_time] == ""

def test_remove_reservation_record(ss):
    student_name = "John Doe"
    student_email = "xyz123@georgetown.edu"
    res_date = "12/16/2023"
    res_time = "4:00pm"
    res_room = 2

    # Add the reservation for testing purposes
    ss.add_reservation_record(student_name, student_email, res_date, res_time, res_room, sheet_name="test_reservations")

    # Test remove_reservation_from_record function
    ss.remove_reservation_from_record(student_name, student_email, res_date, res_time, res_room, sheet_name="test_reservations")

    # Check if the reservation information is correctly removed from the test_reservations sheet
    student_reservations = ss.get_student_reservations(student_email, sheet_name="test_reservations")
    assert not any(reservation['date'] == res_date and reservation['time'] == res_time and reservation['room'] == res_room for reservation in student_reservations)