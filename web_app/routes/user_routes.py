
from flask import Blueprint, render_template, flash, redirect, current_app, url_for, session, request #, jsonify

from web_app.routes.wrappers import authenticated_route

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
    service = current_app.config["SPREADSHEET_SERVICE"]
    schedule = service.get_upcoming_week_reservations()
    return render_template("reserve.html", schedule=schedule)

@user_routes.route("/user/reserve")
@authenticated_route
def reserve_room():
    print("MAKING RESERVATION...")
    service = current_app.config["SPREADSHEET_SERVICE"]
    schedule = service.get_upcoming_week_reservations()

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
