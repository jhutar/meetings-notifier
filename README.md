Meetings notifier
=================

Get credentials to access Google Calendar
-----------------------------------------

First, go to Google Cloud console, create project "Meetings notifier" and switch to it:

    https://console.cloud.google.com/

Click "Apis and Services" to go to it's properties and then click "Credentials":

    https://console.cloud.google.com/apis/credentials?project=meetings-notifier

Click "Configure consent screen" and then followed the wizzard and selected external application (because I'm not Google Workspace user, otherwise I would go with internal). It was bit painfull to be able to go to next step - either filling all the fields helped or Console page refresh.

Once you created the client, open it in the console and download it's secret. You will get file like `client_secret_...-....apps.googleusercontent.com.json`.

Then I went to "Clients" menu and created "OAuth 2.0 Client IDs" client:

    Application type: Desktop app

Then in "Data Access" clicked "Add or remove scopes" and used "Manually add scopes" to add:

    https://www.googleapis.com/auth/calendar.events.readonly

Then in "Enabled APIs & services" find "Google Caledar API", click it and enable it.
