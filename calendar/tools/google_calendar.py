import os
import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarTool(Tool):
    def _build_service(self):
        credentials_info = json.loads(self.runtime.credentials["google_service_account"])
        credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
        return service

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        service = self._build_service()
        action = tool_parameters.get("action", "").lower()
        query = tool_parameters.get("query", "")

        if action not in ["create", "fetch", "delete"]:
            yield self.create_text_message(f"Invalid action: {action}. Must be one of create, fetch, delete.")
            return

        try:
            if action == "fetch":
                now = datetime.utcnow().isoformat() + 'Z'
                events_result = service.events().list(
                    calendarId='primary', timeMin=now, maxResults=5, singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events = events_result.get('items', [])
                if not events:
                    yield self.create_text_message("No upcoming events found.")
                else:
                    formatted = "\n".join(f"{e['summary']} at {e['start'].get('dateTime', e['start'].get('date'))}" for e in events)
                    yield self.create_text_message(f"Upcoming events:\n{formatted}")

            elif action == "create":
                event = {
                    'summary': 'Quick Event',
                    'description': query,
                    'start': {'dateTime': (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'},
                    'end': {'dateTime': (datetime.utcnow() + timedelta(hours=2)).isoformat() + 'Z'},
                    'timeZone': 'UTC'
                }
                created_event = service.events().insert(calendarId='primary', body=event).execute()
                yield self.create_text_message(f"Event created: {created_event.get('htmlLink')}")

            elif action == "delete":
                # Not implemented – would need event ID
                yield self.create_text_message("Delete action requires event ID and is not implemented here.")
        except Exception as e:
            yield self.create_text_message(f"Google Calendar error: {str(e)}")
