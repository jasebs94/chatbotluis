import requests

def getIntent(input):
    key = 'a6abad89190342d2a5006377f7e9bf54' # your Runtime key
    endpoint = 'https://westus.api.cognitive.microsoft.com/' # such as 'your-resource-name.api.cognitive.microsoft.com'
    appId = '6a5c2179-a3d6-4be4-b99e-b191229b5b06'
    utterance = input

    headers = {
    }

    params ={
        'query': utterance,
        'timezoneOffset': '0',
        'verbose': 'true',
        'show-all-intents': 'true',
        'spellCheck': 'false',
        'staging': 'false',
        'subscription-key': key
    }

    r = requests.get(f'https://westus.api.cognitive.microsoft.com/luis/prediction/v3.0/apps/{appId}/slots/production/predict',headers=headers, params=params)
    print(r.json())
    result = r.json()
    print(result['prediction']['topIntent'])
    intent = result['prediction']['topIntent']
    score = result['prediction']['sentiment']['score']
    print(intent)
    print(score)
    if intent == "Welcome" and score > 0.5:
        reply = "Hello how are you.To where can I book you a flight?"
    elif intent == "BookFlight" and score > 0.5:
        reply = "ok?"
        
    return reply
