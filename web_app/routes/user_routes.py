
from flask import Blueprint, render_template, flash, redirect, current_app, url_for, session, request #, jsonify

from web_app.routes.wrappers import authenticated_route

from datetime import datetime

user_routes = Blueprint("user_routes", __name__)

#
# USER ORDERS
#

@user_routes.route("/user/reservations")
@authenticated_route
def reservations():
    print("USER RESERVATIONS...")
    current_user = session.get("current_user")
    service = current_app.config["SPREADSHEET_SERVICE"]
    reservations = service.get_student_reservations(current_user["email"])
    return render_template("reservations.html", reservations=reservations)


@user_routes.route("/user/reserve")
@authenticated_route
def reserve():
    print("RESERVE A ROOM...")
    date_str = request.args.get('date', datetime.now().strftime("%m/%d/%Y")) #attribute to gpt; if theres a param, then use that date. if not, then get the current date
    service = current_app.config["SPREADSHEET_SERVICE"]
    schedule = service.get_schedule_by_date(date_str)
    next_week_dates = service.get_next_week_dates()


    return render_template("reserve.html", schedule=schedule, dates=next_week_dates, selected_date=date_str)

@user_routes.route("/user/api/reserve-room")
@authenticated_route
def make_reservation():
    print("MAKING A RESERVATION...")
    service = current_app.config["SPREADSHEET_SERVICE"]
    args = request.args
    current_user = session.get("current_user")

    user_name = current_user["name"]
    user_email = current_user["email"]
    date = args.get("date")
    time = args.get("time")
    room = int(args.get("room"))

    response = service.add_reservation_to_table(user_name, user_email, date, time, room)

#
# USER PROFILE
#

@user_routes.route("/user/profile")
@authenticated_route
def profile():
    print("USER PROFILE...")
    current_user = session.get("current_user")
    #user = fetch_user(email=current_user["email"])
    return render_template("user_profile.html", user=current_user) # user=user
