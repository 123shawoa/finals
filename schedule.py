# Import necessary libraries
import datetime as dt
import os.path

# Import Google API libraries
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define the scope of the Google API
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Main function to authenticate and connect to Google Calendar API
def main():
    # Initialize credentials
    creds = None
    
    # Check if token file exists
    if os.path.exists("tokens.json"):
        # Load credentials from token file
        creds = Credentials.from_authorized_user_file("tokens.json")
    
    # Check if credentials are valid
    if not creds or not creds.valid:
        # If credentials are expired, refresh them
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # If no credentials or refresh token, authenticate using client secrets file
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    # Try to build the Google Calendar API service
    try:
        service = build("calendar", "v3", credentials=creds)

        
        event = {
            "summary": "My Python Event",
            "location": "Somewhere Online",
            "description": "Some more details on this awesome event",
            "colorId": 6,
            "start": {
                "dateTime": "2025-03-10T09:00:00-05:00",
                "timeZone": "America/New_York"
            },
            "end": {
                "dateTime": "2025-03-10T16:00:00-05:00",
                "timeZone": "America/New_York"
            },
            "recurrence" : [
                "RRULE:FREQ=DAILY;COUNT=3"
            ],
            "attendees": [
                {"email": "olabayooluyamo@gmail.com"},
                {"email": "user1@example.com"},
                {"email": "user1@example.com"},
            ]
        }
        
        
        event = service.events().insert(calendarId = "primary", body = event).execute()
        
        print(f"Event created {event.get('htmlLink')}")
    except HttpError as error:
        # Handle any HTTP errors
        print(f"An HTTP error occurred: {error}")


def create_event(event_data):
    # Existing auth code
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # ... (rest of existing auth code)
    
    try:
        service = build("calendar", "v3", credentials=creds)
        event = service.events().insert(calendarId="primary", body=event_data).execute()
        print(f"Successfully created event: {event.get('htmlLink')}")
        return True
    except HttpError as error:
        print(f"Error creating event: {error}")
        return False        
if __name__ =="__main__":
    main()
