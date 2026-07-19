import json
import requests  # Make sure `requests` is installed

def send_whatsapp_public_message(mobilenumber, firstname):
    url = 'https://api.interakt.ai/v1/public/message/'
    api_key = 'aWZNYkJ4UWFBTG5nUTZZVHdDTndLQ0ViZTV4d1o4cHBiNGdGV1Joc01SNDo='
    print('mobilenumber')
    print(mobilenumber)
    headers = {
        'Authorization': f'Basic {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'countryCode': '+91',
        'phoneNumber': mobilenumber,
        'callbackData': 'Succesfully sent Message',
        'type': 'Template',
        'template': {
            'name': 'ikfdonationmessage',
            'languageCode': 'en',
            'headerValues': [],
            'bodyValues': [firstname]
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code >= 200 and response.status_code < 300:
            print("Public message API request was successful!")

        else:
            print(f"Public message API request failed with status code {response.status_code}")
            print(response.content)
    except Exception as e:
        print(e)
        return None
