# flask-sheets-template-2023

A web application starter template, created in Python with the Flask framework. Allows users to login with their Google accounts (via OAuth). Interfaces with a Google Sheets database.

![](https://user-images.githubusercontent.com/1328807/160312385-7ffbbada-4363-4b48-873d-9eca868afef0.png)

## Prerequisites

This application requires a Python development environment:

  + Git
  + Anaconda, Python, Pip

For beginners, here are some instructions for how to install Anaconda, and [set up your local Python development environment](https://github.com/prof-rossetti/intro-to-python/blob/main/exercises/local-dev-setup/README.md#anaconda-python-and-pip).

## Repo Setup

Make a copy of this template repo (as necessary). Clone your copy of the repo onto your local machine. Navigate there from the command-line.

Setup and activate a new Anaconda virtual environment:

```sh
conda create -n flask-sheets-env-2023 python=3.10
conda activate flask-sheets-env-2023
```

Install package dependencies:

```sh
pip install -r requirements.txt
```

## Services Setup

This app requires a few services, for user authentication and data storage. Follow the instructions below to setup these services.

### Google Cloud Project

Visit the [Google Cloud Console](https://console.cloud.google.com). Create a new project, and name it. After it is created, select it from the project selection dropdown menu.

### Google OAuth Client

Visit the [API Credentials](https://console.cloud.google.com/apis/credentials) page for your Google Cloud project. Click the button with the plus icon to "Create Credentials", and choose "Create OAuth Client Id".

Click to "Configure Consent Screen". Leave the domain info blank, and leave the defaults / skip lots of the setup for now. If/when you deploy your app to a production server, you can return to populating this info (or you will be using a different project).

Return to actually creating the "OAuth Client Id". Choose a "Web application" type, give it a name, and set the following "Authorized Redirect URIs" (for now, while the project is still in development):

  + http://localhost:5000/auth/google/callback

After the client is created, note the `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`, and set them as environment variables (see configuration section below).

### Google Cloud Service Account Credentials

To fetch data from the Google Sheets database (and use other Google APIs), the app will need access to a local "service account" credentials file.

From the [Google API Credentials](https://console.cloud.google.com/apis/credentials) page, create a new service account as necessary.

For the chosen service account, create new JSON credentials file as necessary from the "Keys" menu, then download the resulting JSON file into the root directory of this repo, specifically named "google-credentials.json".


### Google Sheets Database Setup

See the [Google Sheets Database Setup](/admin/SHEETS_DB.md) guide.

### Google Analytics Setup

If you would like to configure Google Analytics, consult the [Google Analytics Setup](/admin/GA.md) guide.



## Configuration

### Environment Variables

Create a file called ".env" in the root directory of this repository, and populate it with environment variables to specify your own credentials, as obtained in the "Setup" section above:

```sh
FLASK_APP="web_app"

#
# GOOGLE OAUTH
#
GOOGLE_CLIENT_ID="____________"
GOOGLE_CLIENT_SECRET="____________"

#
# GOOGLE SHEETS DATABASE
#
GOOGLE_SHEETS_DOCUMENT_ID="____________"

#
# GOOGLE ANALYTICS
#
GA_TRACKER_ID="UA-XXXXXXX-1"
```




## Usage

### Sheets Service

After configuring the Google Sheet database and populating it with products, you should be able to test out the app's ability to fetch products (and generate new orders):

```sh
python -m app.sheets_service
```

### Web Application

Run the local web server (then visit localhost:5000 in a browser):

```sh
FLASK_APP=web_app flask run
```

## Testing

Run tests:

```sh
pytest
```

> NOTE: we are using a live sheet for testing, so to avoid API rate limits, we are waiting / sleeping between each test, which makes the tests a bit slow for now


## CI

See more information about the [CI](/admin/CI.md) build process.

## Deploying

See the [Deployer's Guide](/admin/RENDER.md) for instructions on deploying to a production server hosted by Render.



## [License](/LICENSE.md)
