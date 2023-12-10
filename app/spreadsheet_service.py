
# adapted from:
# ... https://developers.google.com/sheets/api/guides/authorizing
# ... https://gspread.readthedocs.io/en/latest/oauth2.html
# ... https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html
# ... https://github.com/s2t2/birthday-wishes-py/blob/master/app/sheets.py
# ... https://raw.githubusercontent.com/prof-rossetti/flask-sheets-template-2020/master/web_app/spreadsheet_service.py

import os
from datetime import datetime, timedelta, timezone
from pprint import pprint
import json

from dotenv import load_dotenv
import gspread
from gspread.exceptions import SpreadsheetNotFound


load_dotenv()

DEFAULT_FILEPATH = os.path.join(os.path.dirname(__file__), "..", "google-credentials.json")
GOOGLE_CREDENTIALS_FILEPATH = os.getenv("GOOGLE_CREDENTIALS_FILEPATH", default=DEFAULT_FILEPATH)

GOOGLE_SHEETS_DOCUMENT_ID = os.getenv("GOOGLE_SHEETS_DOCUMENT_ID", default="OOPS Please get the spreadsheet identifier from its URL, and set the 'GOOGLE_SHEETS_DOCUMENT_ID' environment variable accordingly...")

DEFAULT_CELL_VALUE = repr({"8:00am": "", "10:00am": "", "12:00pm": "", "2:00pm": "", "4:00pm": "", "6:00pm": "", "8:00pm": "", "10:00pm": ""})


class SpreadsheetService:

    def __init__(self, credentials_filepath=GOOGLE_CREDENTIALS_FILEPATH, document_id=GOOGLE_SHEETS_DOCUMENT_ID):
        print("INITIALIZING NEW SPREADSHEET SERVICE...")

        self.client = gspread.service_account(filename=credentials_filepath)

        self.document_id = document_id


    @staticmethod
    def generate_timestamp():
        return datetime.now(tz=timezone.utc).strftime("%m/%d/%Y %H:%M:%S")

    @staticmethod
    def parse_timestamp(ts: str):
        """
        ts (str): a timestamp string like '03/08/2023 19:59:16'
        """
        date_format = "%m/%d/%Y %H:%M:%S"
        return datetime.strptime(ts, date_format)
    
    @staticmethod
    def get_next_week_dates():
        today = datetime.now()
        next_7_days = [today + timedelta(days=i) for i in range(7)]
        formatted_dates = [date.strftime("%m/%d/%Y") for date in next_7_days]
        return formatted_dates

    # READING DATA
    # ... TODO: consider passing the sheet or the sheet name, and getting the sheet only if necessary

    @property
    def doc(self):
        """note: this will make an API call each time, to get the new data"""
        return self.client.open_by_key(self.document_id) #> <class 'gspread.models.Spreadsheet'>

    def get_sheet(self, sheet_name):
        return self.doc.worksheet(sheet_name)
        
    def get_student_reservations(self, student_email):
        sheet = self.get_sheet("logs")  
        all_records = sheet.get_all_records()  # Get all the data from the sheet

        student_reservations = []
        for record in all_records: # ... TODO: some optimization, looping through each reservation may not be efficient. but this is fine for now
            if record['student_email'] == student_email and record['status'] != "canceled":
                reservation = {
                    'date': record['res_date'],
                    'time': record['res_time'],
                    'room': record['res_room']
                }
                student_reservations.append(reservation)

        return student_reservations
    
    def get_schedule_by_date(self, date_str):

        sheet = self.get_sheet("table")
        dates = sheet.col_values(1)

        try: #index logic from ChatGPT
            start_index = dates.index(date_str) + 1
        except ValueError:
            return "Date not found in sheet."
        
        upcoming_week_data = sheet.row_values(start_index)

        formatted_data = {
                "date": upcoming_week_data[0],
                "data": [json.loads(rd) for rd in upcoming_week_data[1:len(upcoming_week_data)]]
            }

        return formatted_data
    
    


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

        self.__add_reservation_record(student_name, student_email, res_date, res_time, res_room)

        return json.dumps({
            "statusCode": 200,
            "message": "Successfully added reservation!"
        })


    #PRIVATE METHOD: function only to be called by the add_reservation_to_table method...
    def __add_reservation_record(self, student_name, student_email, res_date, res_time, res_room):
        sheet = self.get_sheet("logs")

        new_row = [self.generate_timestamp(), student_name, student_email, res_date, res_time, res_room, "reserved"]

        sheet.append_row(new_row)

        print(f"Sucessfully generated reservation record: {student_name} in Room {res_room} on {res_date} at {res_time}")

    def remove_reservation_from_table(self, student_name, student_email, res_date, res_time, res_room):
        sheet = self.get_sheet("table")

        dates = sheet.col_values(1)
        if res_date in dates:
            res_row = dates.index(res_date) + 1
        else:
            raise Exception(f"Reservation on {res_date} not found!")

        res_cell = sheet.cell(res_row, res_room + 1)
        res_cell_data = json.loads(res_cell.value)

        if res_cell_data[res_time] == "":
            raise ReservatonEmptyException(res_date, res_time, res_room)
        else:
            # Cancel the reservation by setting the email to an empty string
            res_cell_data[res_time] = ""

        sheet.update_cell(res_row, res_room + 1, json.dumps(res_cell_data))

        print(f"SUCCESSFULLY CANCELED RESERVATION - {res_room} on {res_date} at {res_time}")

        self.__remove_reservation_record(student_name, student_email, res_date, res_time, res_room)


    def __remove_reservation_record(self, student_name, student_email, res_date, res_time, res_room):
        sheet = self.get_sheet("logs")

        all_records = sheet.get_all_records()


        # Assume that there can be multiple matching records (edge case)
        record_found = False
        row_number = 2
        for record in all_records:
            if record['student_name'] == student_name and record['student_email'] == student_email and record['res_date'] == res_date and record['res_time'] == res_time and record['res_room'] == res_room and record['status'] == "reserved":
                sheet.update_cell(row_number, 7, "canceled")
                record_found = True
            row_number += 1
        
        if not record_found:
            raise Exception(f"No matching reservation found for {student_name} with {student_email} on {res_date} at {res_time} in Room {res_room}")


        print(f"Successfully removed reservation for {student_name} ({student_email}) on {res_date} at {res_time} in Room {res_room}")



#CLASSES FOR EXCEPTIONS
class ReservatonTakenException(Exception):
    """
        This exception class is for when a user tries to reserve a slot that is already taken
        Should never be called (prevented on the frontend), but a good catch
    """
    def __init__(self, date, time, room_number):
        self.message = f"The reservation for room {room_number} on {date} at {time} is already taken!"

        super().__init__(self.message)

class ReservatonEmptyException(Exception):
    """
        This exception class is for when a user tries to reserve a slot that is already taken
        Should never be called (prevented on the frontend), but a good catch
    """
    def __init__(self, date, time, room_number):
        self.message = f"The reservation for room {room_number} on {date} at {time} does not exist, so you cannot cancel it!"

        super().__init__(self.message)





if __name__ == "__main__":

    ss = SpreadsheetService()

    data = ss.get_upcoming_week_reservations()
    print(data[0])
