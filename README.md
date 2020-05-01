# Viber Notes Bot
Viber bot for saving notes

# Webhook setup
After server is started you can setup webhook this way:  
```python
import requests
import json
auth_token = 'Your auth token'
hook = 'https://chatapi.viber.com/pa/set_webhook'
headers = {'X-Viber-Auth-Token': auth_token}

data = dict(url='https://your_webhook_url',
           event_types = ['message'])

response = requests.post(hook, json.dumps(data), headers=headers)
response_json = response.json()
if 'status_message' in response_json and response_json['status_message'] == 'ok':
    print('Webhook set up')
else:
    print('Cannot set up webhook')
```