"""
Copyright 2022 Diogo Coelho

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
#Standard library imports
import datetime
import os

# Third party imports
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from pushbullet import Pushbullet
from dotenv import load_dotenv


load_dotenv()

PB_TOKEN = os.getenv("PB_TOKEN")
GCAL_Id = os.getenv("GCAL_ID")
GCAL_TOKEN = os.getenv("G_TOKEN")

pb = Pushbullet(PB_TOKEN)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
phone = pb.devices[0]

def create_token():
    """
    Creates or reads the token.json file which stores the user's access and refresh tokens
    """
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w', encoding="UTF-8") as token:
            token.write(creds.to_json())
    return creds


def fetch_events(data):
    """
    Gets the events from Google calendar API
    Args:
        creds (Credentials, optional): Defaults to create_token().
    """
    creds = create_token()

    today = data.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = data.replace(hour=23, minute=59, second=59, microsecond=999999)

    today = today.isoformat() + 'Z'  # 'Z' indicates UTC time
    end_of_day = end_of_day.isoformat() + 'Z'  # 'Z' indicates UTC time

    try:
        service = build('calendar', 'v3', credentials=creds)
        events_results = service.events().list(calendarId='primary', # pylint: disable=maybe-no-member
                                               timeMin=today,
                                               timeMax=end_of_day,
                                               singleEvents=True,
                                               orderBy='startTime').execute()
        events = events_results.get('items', [])
        return events
    except HttpError as error:
        phone.push_note("",f'An error occurred: {error}')
    

def parse_message(events):
    """
    Parses the events into the proper message strings
    Args:
        date (date/dateTime): _description_
    """
    message = "Today: \n"
    for event in events[0]:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if "T" in start:
            time = "at " + start.split("T")[1]
        else:
            time = "all day "
        message += f"{event['summary']} {time[:-1]} \n"
    message += "============*============\nTomorrow\n"
    for event in events[1]:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if "T" in start:
            time = "at " + start.split("T")[1]
        else:
            time = "all day "
        message += f"{event['summary']} {time[:-1]} \n"

    return message[:-1]

def push(message):
    """
    Deletes all previous pushes and sends todays and tomorrow Schedule to phone
    Args:
        message (str): message to send, from parse_message
    """
    pb.delete_pushes()
    phone.push_note("Schedule", message)


def main():
    today = datetime.datetime.now()
    events_today = fetch_events(today)
    tomorrow = today.replace(day=today.day+1)
    events_tomorrow = fetch_events(tomorrow)
    events = [events_today, events_tomorrow]
    push(parse_message(events))
    
    


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
