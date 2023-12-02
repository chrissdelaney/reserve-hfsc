
# adapted from:
# ... https://developers.google.com/sheets/api/guides/authorizing
# ... https://gspread.readthedocs.io/en/latest/oauth2.html
# ... https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
# ... https://github.com/s2t2/birthday-wishes-py/blob/master/app/sheets.py
# ... https://raw.githubusercontent.com/prof-rossetti/flask-sheets-template-2020/master/web_app/spreadsheet_service.py

import os
from datetime import datetime, timezone
from pprint import pprint
import json

from dotenv import load_dotenv
import gspread
from gspread.exceptions import SpreadsheetNotFound


load_dotenv()

DEFAULT_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "google-credentials.json")
GOOGLE_CREDENTIALS_FILEPATH = os.getenv("GOOGLE_CREDENTIALS_FILEPATH", default=DEFAULT_FILEPATH)

GOOGLE_SHEETS_DOCUMENT_ID = os.getenv("GOOGLE_SHEETS_DOCUMENT_ID", default="OOPS Please get the spreadsheet identifier from its URL, and set the 'GOOGLE_SHEETS_DOCUMENT_ID' environment variable accordingly...")


class SpreadsheetService:

    def __init__(self, credentials_filepath=GOOGLE_CREDENTIALS_FILEPATH, document_id=GOOGLE_SHEETS_DOCUMENT_ID):
        print("INITIALIZING NEW SPREADSHEET SERVICE...")

        self.client = gspread.service_account(filename=credentials_filepath)

        self.document_id = document_id


    @staticmethod
    def generate_timestamp():
        return datetime.now(tz=timezone.utc)

    @staticmethod
    def parse_timestamp(ts:str):
        """
            ts (str) : a timestamp string like '2023-03-08 19:59:16.471152+00:00'
        """
        date_format = "%Y-%m-%d %H:%M:%S.%f%z"
        return datetime.strptime(ts, date_format)

    # READING DATA
    # ... TODO: consider passing the sheet or the sheet name, and getting the sheet only if necessary

    @property
    def doc(self):
        """note: this will make an API call each time, to get the new data"""
        return self.client.open_by_key(self.document_id) #> <class 'gspread.models.Spreadsheet'>

    def get_sheet(self, sheet_name):
        return self.doc.worksheet(sheet_name)

    def get_row_data_by_date(self, date_str):
        """
           gets row data from sheet given a certain date 
        """
        sheet = self.get_sheet("table")
        dates = sheet.col_values(1)
        
        if date_str in dates:
            row_number = dates.index(str) + 1
            row_data = sheet.row_values(row_number)

            # Parse JSON data in each cell (excluding the date cell)
            parsed_row_data = [json.loads(cell) if i > 0 else cell for i, cell in enumerate(row_data)]
            return parsed_row_data
        else:
            # TODO: implement adding a row in the sheet...
            return
        
    def get_reservations(self, student_email):
        sheet = self.get_sheet("reservations")  # Assuming the sheet name is "reservations"
        all_records = sheet.get_all_records()  # Get all the data from the sheet

        student_reservations = []
        for record in all_records: # ... TODO: some optimization, looping through each reservation may not be efficient. but this is fine for now
            if record['student_email'] == student_email:
                reservation = {
                    'date': record['res_date'],
                    'time': record['res_time'],
                    'room': record['res_room']
                }
                student_reservations.append(reservation)

        return student_reservations


    # WRITING DATA

    def add_reservation_to_table(self, student_name, student_email, res_date, res_time, res_room):
        sheet = self.get_sheet("table")

        dates = sheet.col_values(1)
        if res_date in dates:
            res_row = dates.index(res_date) + 1
        else:
            # TODO: implement logic to add row to sheet; will make the code self-sustaining
            pass
        
        res_cell = sheet.cell(res_row, res_room + 1)
        res_cell_data = json.loads(res_cell.value) #gets dictionary object of times and emails for that date and room number

        if res_cell_data[res_time] != "":
            raise ReservatonTakenException(res_date, res_time, res_room)
        else:
            res_cell_data[res_time] = student_email
        
        sheet.update_cell(res_row, res_room + 1, json.dumps(res_cell_data))

        print(f"SUCCESSFULLY UPDATED CELL - {res_room} on {res_date} at {res_time}")

        self.add_reservation_record(student_name, student_email, res_date, res_time, res_room)



    def add_reservation_record(self, student_name, student_email, res_date, res_time, res_room):
        sheet = self.get_sheet("reservations")

        new_row = [self.generate_timestamp(), student_name, student_email, res_date, res_time, res_room]

        sheet.append_row(new_row)

        print(f"Sucessfully generated reservation record: {student_name} in Room {res_room} on {res_date} at {res_time}")

class ReservatonTakenException(Exception):
    """
        This exception class is for when a user tries to reserve a slot that is already taken
        Should never be called (prevented on the frontend), but a good catch
    """
    def __init__(self, date, time, room_number):
        self.message = f"The reservation for room {room_number} on {date} at {time} is already taken!"

        super().__init__(self.message)



if __name__ == "__main__":

    ss = SpreadsheetService()

    ss.seed_products()

    sheet, records = ss.get_records("products")

    for record in records:
        print("-----")
        pprint(record)
