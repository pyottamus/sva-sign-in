----------- SETUP ----------------
Because this application hooks up to Google Spreadsheets, you will first need to modify it to use your API and spreadsheet.

1. Go to https://console.developers.google.com/apis/credentials
2. Click the "Create credentials" dropdown and click OAuth client ID
3. Choose "Other", give it a name, and press Create
4. Find the newly created credentials in the list under "OAuth 2.0 client IDs"
5. Press the download button for it on the right hand side of the screen to download the JSON file.
6. Rename this "client_secret.json" and place it in the main application directory
7. Open the spreadsheet you wish to use to for the log in a web browser
8. Find the long string of characters (the sheet ID) in the middle of the URL (e.g. "1OsN-XN1tVNAyjf7WQ0eikhpjfLxxzEqtGfZOGDefulY")
9. In SVA_Sign_In.py paste this string into the variable "SPREADSHEET_ID"