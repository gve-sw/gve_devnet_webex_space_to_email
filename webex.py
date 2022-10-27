"""
Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Trevor Maco <tmaco@cisco.com>"
__copyright__ = "Copyright (c) 2022 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import requests, json, os

import settings

# Global variables
base_url = 'https://webexapis.com/v1/'

# oauth_token = os.getenv('oauth_token')
# refresh_token = os.getenv('refresh_token')

# Token expired custom exception
class TokenExceptionError(Exception):
    """ Raised when the Webex OAuth Token has expired """
    pass

# Decorator which wraps each api call, and forces a token refresh if necessary
def refresh_on_expire(func):
    
    refresh_token = os.getenv('refresh_token')

    def wrapper(token, *args, **kwargs):
        try:
            # First webex api call attempt
            result = func(token, *args, **kwargs)
        except TokenExceptionError:
            
            # Get a new token
            print('Error, token is invalid/expired! Generating a new token...')
            os.environ['oauth_token'] = refresh_expired_token(refresh_token)
            print('New oauth token: {}'.format(os.environ['oauth_token']))
            
            # Re run webex api call
            result = func(os.getenv('oauth_token'), *args, **kwargs)
        finally:
            return result
    return wrapper

# If primary token expires, refresh the token
def refresh_expired_token(refresh_token):    
    url = "access_token"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = json.dumps({
        "grant_type": "refresh_token",
        "client_id": f"{settings.client_id}",
        "client_secret": f"{settings.secret_id}",
        "refresh_token": f"{refresh_token}"
    })
    
    response = requests.post(url=f'{base_url}{url}', headers=headers, data=payload)
    
    # print(f'response status: {response.status_code}, and message: {response.json()}')
    
    if response.status_code == 200:
        return response.json()['access_token']
    
# Get room id for the room we are interested in
@refresh_on_expire
def get_room_id(token, target_room):
    # Get list of rooms 
    url = "rooms"
    
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(url=f'{base_url}{url}', headers=headers)
    
    if response.status_code == 200:
        # List of rooms
        rooms = response.json()['items']
        
        # Search list of returned rooms, if you find the room, return id
        for room in rooms:
            if room['title'] == target_room:
                print('Found room: {} with room id: {}'.format(target_room, room['id']))
                return room['id']

        print('Error: {} not found'.format(target_room))
        return None
    elif response.status_code == 401:
        # Expired token response
        raise TokenExceptionError('Webex Oauth expired, retrieving a new one...')
    else:
        print('Unexpected status code: {}, message: {}'.format(response.status_code, response.text))
        return None
        
# Configure webhook for room that responds when new messages are returned
@refresh_on_expire
def configure_webhook(token, room_id):
    url = "webhooks"
    
    payload = json.dumps({
        "resource": "messages",
        "event": "created",
        "filter": f"roomId={room_id}",
        "targetUrl": settings.webhook_uri,
        "name": "Space Email Webhook",
        "secret": settings.secret
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.post(url=f'{base_url}{url}', headers=headers, data=payload)
    
    # print(f'response status: {response.status_code}, and webhook: {response.json()}')
    
    if response.status_code == 200:
        webhook = response.json()
        print('Webhook created! Heres the id: {}'.format(webhook['id']))
        return webhook
    elif response.status_code == 409:
        print('Webhook conflict detected, webhook already exists. Using existing webhook...')
    elif response.status_code == 401:
        # Expired token response
        raise TokenExceptionError('Webex Oauth expired, retrieving a new one...')
    else:
        print('Unexpected status code: {}, message: {}'.format(response.status_code, response.text))
        return None

# List user webhooks
@refresh_on_expire
def list_webhooks(token):
    url = "webhooks"

    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(url=f'{base_url}{url}', headers=headers)

    # print(f'response status: {response.status_code}, and room details: {response.json()}')

    if response.status_code == 200:
        webhooks = response.json()['items']
        print('{} webhook(s) found!'.format(len(webhooks)))
        return webhooks
    else:
        print('Unexpected status code: {}, message: {}'.format(response.status_code, response.text))
        return None

# Get room details by id
@refresh_on_expire
def room_details(token, room_id):
    url = f"rooms/{room_id}"
    
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(url=f'{base_url}{url}', headers=headers)
    
    # print(f'response status: {response.status_code}, and room details: {response.json()}')
    
    if response.status_code == 200:
        room = response.json()
        print('room id: {} and room name: {}'.format(room['id'], room['title']))
        return room
    elif response.status_code == 401:
        # Expired token response
        raise TokenExceptionError('Webex Oauth expired, retrieving a new one...')
    else:
        print('Unexpected status code: {}, message: {}'.format(response.status_code, response.text))
        return None

# Get message details by id
@refresh_on_expire
def message_details(token, message_id):
    url = f"messages/{message_id}"
    
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(url=f'{base_url}{url}', headers=headers)

    # print(f'response status: {response.status_code}, and message: {response.json()}')

    if response.status_code == 200:
        message = response.json()
        print('Message id: {} and text: {}'.format(message['id'], message['text']))
        return message
    elif response.status_code == 401:
        # Expired token response
        raise TokenExceptionError('Webex Oauth expired, retrieving a new one...')
    else:
        print('Unexpected status code: {}, message: {}'.format(response.status_code, response.text))
        return None
