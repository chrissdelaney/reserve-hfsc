
## Google Sheets API Setup

From the Google APIs project console, enable the Google Sheets APIs.

Ensure the Google API Credentials file for this project is stored locally as "google-credentials.json" (from previous README step).

### Google Sheets Database Setup

Create a new Google Sheet document.

Modify the document's sharing settings to grant "edit" privileges to the "client email" address specified in the Google API credentials file.

**Products Sheet**

Create a new sheet called "products", and add an initial row of column headers:
  + `id`
  + `name`
  + `description`
  + `price`
  + `url`
  + `created_at`

**Orders Sheet**

Create a new sheet called "orders", and add an initial row of column headers:

  + `id`
  + `product_id`
  + `user_email`
  + `created_at`


**Seeding the Database**

Seed the database to automatically populate it with example product records:


```sh
python -m app.sheets_service
```

name | description | price | url
--- | --- | --- | ---
Strawberries | Juicy organic strawberries. | 4.99 | https://picsum.photos/id/1080/360/200
Cup of Tea | An individually-prepared tea or coffee of choice. | 3.49 | https://picsum.photos/id/225/360/200
Textbook | It has all the answers. | 129.99 | https://picsum.photos/id/24/360/200
