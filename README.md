# PushCalendar

This projects utilizes GoogleCalendarAPI and pushBulletAPI Wrappers push a nootification to a device of the Schedule for the day, and the day after.

🔗  Key Links 🔗
https://developers.google.com/calendar/api/quickstart/python
https://github.com/rbrcsk/pushbullet.py

# Installation and Running the script
1. Install dependencies
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install pushbullet.py
pip install python-dotenv
```
2. Enable Google Calendar API and download `credentials.json`, from the [Google Cloud Platform](https://console.cloud.google.com/apis/credentials)

3. Save your Pushbullet token in a `.env` on the main directory

4. To run simply
```
python run main.py
```

You can make it run periodically by assigning it to cronjob ou by using the APScheduler python module

# Disclaimer

Sometimes Google Calendar access token can expire. Can be solved by deletinng the `token.json` file and rerunning the script
