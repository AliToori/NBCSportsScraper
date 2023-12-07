# NBCBot: NBC Sports Headlines Scraper

NBCBot is a custom scraper-bot for retrieving headlines from www.nbcsports.com, updating it and uploading to a Google Sheet to be easily accessible.

*******************************************************************************************

Author: Ali Toori, Full-Stack Python Developer, Bot-Builder.

Founder: https://boteaz.com

YouTube: https://youtube.com/@AliToori

Telegram: https://t.me/@AliToori
*******************************************************************************************

# Usage
Install the required packages by running the following command.
    
    pip install -r requirements.txt

Run the following command in terminal opened at the main folder.
    
    python NBCBot.py

<b>Extract the NBCBot</b>

1. Navigate to the NBCBot => NBCRes directory.
2. Put your Google sheet URL and sheet name under SheetURL and SheetName respectively. 
3. Finally, Launch the bot by double clicking the NBCBot-v0.0.1.exe file in main NBCBot directory.

Input Parameters
-
<b>AccountNo</b>: A serial number used by the Bot

<b>SheetURL</b>: Google Sheet's URL which the data to be uploaded to.

<b>SheetName</b>: Google Sheet's name which the data to be uploaded to.

<b>StartDate</b>: The date which posts to be retrieved from. 

<b>EndDate</b>: The date which posts to be retrieved to.

<b>NOTE</b>: DO NOT DELETE THE "client-secret_nbcbot.json" FILE IT IS BEING USED FOR GOOGLE-SHEET AUTHENTICATION.

<h1>Features</h1>

- Navigates the headlines.
- Filters headlines by date posted day-before (Yesterday).
- Retrieves all the headlines posted on day-before (Yesterday). 
- Updates the and save the headlines into a Headlines.csv file with dates. 
- Uploads the local headlines.csv to a Google sheet given in the input Accounts.csv.
- Closes the browser and stay idle for next 24 hours.
- Wakes-up after repeats the process above. 

Note:
-
You can change your Google Sheet as far as it is from the same google account as the client_secret.
Just update the URL and SheetName in the input Accounts.csv
