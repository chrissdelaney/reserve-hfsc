

import os
from dotenv import load_dotenv

from flask import Flask
from authlib.integrations.flask_client import OAuth

from app import APP_ENV, APP_VERSION
from app.spreadsheet_service import SpreadsheetService

from web_app.routes.home_routes import home_routes
from web_app.routes.auth_routes import auth_routes
from web_app.routes.user_routes import user_routes

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", default="super secret") # IMPORTANT: override in production

# https://icons.getbootstrap.com/
NAV_ICON_CLASS = "bi-globe"

# https://getbootstrap.com/docs/5.1/components/navbar/#color-schemes
# https://getbootstrap.com/docs/5.1/customize/color/#theme-colors
NAV_COLOR_CLASS = "navbar-dark bg-primary"

# for google oauth login:
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


def create_app(spreadsheet_service=None):

    if not spreadsheet_service:
        spreadsheet_service = SpreadsheetService()

    #
    # INIT
    #

    app = Flask(__name__)

    #
    # CONFIG
    #

    # for flask flash messaging:
    app.config["SECRET_KEY"] = SECRET_KEY

    # for front-end (maybe doesn't belong here but its ok):
    app.config["APP_TITLE"] = "Reserve HFSC"
    app.config["NAV_ICON_CLASS"] = NAV_ICON_CLASS
    app.config["NAV_COLOR_CLASS"] = NAV_COLOR_CLASS


    #
    # AUTH
    #

    oauth = OAuth(app)
    oauth.register(
        name="google",
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        #authorize_params={"access_type": "offline"} # give us the refresh token! see: https://stackoverflow.com/questions/62293888/obtaining-and-storing-refresh-token-using-authlib-with-flask
    )
    app.config["OAUTH"] = oauth

    #
    # SERVICES
    #

    app.config["SPREADSHEET_SERVICE"] = spreadsheet_service

    #
    # ROUTES
    #

    app.register_blueprint(home_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(user_routes)

    return app



if __name__ == "__main__":
    my_app = create_app()
    my_app.run(debug=True)
