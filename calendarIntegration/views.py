
from django.shortcuts import render
from django.template.loader import render_to_string
# Create your views here.
import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import View
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']



class GoogleCalendarInitView(View):
    def get(self, request):
        flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_CLIENT_SECRET_FILE,
                scopes=SCOPES,
                redirect_uri='http://localhost:8000/rest/v1/calendar/redirect/'
)
        
        auth_url,state  = flow.authorization_url(prompt='consent')
        request.session['state'] = state
        return HttpResponseRedirect(auth_url)
       


class GoogleCalendarRedirectView(View):
    def get(self, request):
        code = request.GET.get('code')
        if code:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.GOOGLE_CLIENT_SECRET_FILE,
                scopes=SCOPES,
                redirect_uri='http://localhost:8000/rest/v1/calendar/redirect/'
            )
            flow.fetch_token(code=code)
            
            service = build('calendar', 'v3', credentials=flow.credentials)
            events_result = service.events().list(calendarId='primary', maxResults=100).execute()
            events = events_result.get('items', [])
             # Prepare the table header and rows
            table_header = ['Date', 'Summary', 'Link']
            event_data = []
            # Process the events and populate the table rows
          
        # Process the events and create the table-like response
            event_table = []
            for event in events:
                start_datetime = event['start'].get('dateTime', event['start'].get('date'))
                if 'T' in start_datetime:
                    formatted_date = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d")
                else:
                    formatted_date = start_datetime
                event_data = {
                    'date': formatted_date,
                    'summary': event.get('summary', ''),
                   # 'description': event.get('description', ''),
                    'link': event.get('htmlLink', ''),
                }
                event_table.append(event_data)
              # Render the table template with the event data
            table_html = render_to_string('table_template.html', {'events': event_table})

            return HttpResponse(table_html)
