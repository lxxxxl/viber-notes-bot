# Viber Notes Bot
Viber bot for saving notes  
Saves your text notes, files, location info.  

# Credentials setup
Provide your access token in _VIBERBOT\_TOKEN_ environment variable and whitelist of allowed users in _VIBERBOT\_ALLOWED\_USERS_ var.  
Also set name of your bot in _VIBERBOT\_NAME_ and avatar URL in _VIBERBOT\_AVATAR_ vars.  
Yandex Disk access token should be provided in _YADISK\_TOKEN_ var.  

_VIBERBOT\_TOKEN_ can be obtained via [Viber Admin panel](https://partners.viber.com/account/create-bot-account)  
Instructions about _YADISK\_TOKEN_ can be found [here](https://yandex.ru/dev/disk/api/concepts/quickstart-docpage/)  
Example:  
```bash
VIBERBOT_NAME='Bot Name' \
VIBERBOT_AVATAR='https://avatar.url/file.jpg' \
VIBERBOT_TOKEN='111111111111-1111111111111-1111111111-11111111111' \
VIBERBOT_ALLOWED_USERS='AAAAAAAAAAAAAA,BBBBBBBBBBBBB' \
YADISK_TOKEN='111111111111111_111111111111_11111' \
./api.py
```

# Webhook setup
After server is started you can setup webhook this way:  
```python
import requests
import json
import os
auth_token = os.environ('VIBERBOT_TOKEN')
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