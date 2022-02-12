


def lambda_handler(event, context):
    print(event)
    intentName=event['sessionState']['intent']['name']
    print(intentName)

    

    response={
            'sessionState':{
            # 'sessionAttributes':sessionAttributes,
            'dialogAction':{
                'type':'Close',
                'fulfillmentState':'Fulfilled'
            },
            'intent': {
                'confirmationState': 'Confirmed',
                'name': intentName,
                'state': 'Fulfilled'
            }
        },
        'messages': [{'contentType': 'PlainText', 'content': f'{intentName} Fulfilled'}]
    }

    return response






