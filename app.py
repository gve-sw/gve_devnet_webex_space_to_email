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

from flask import Flask, request, render_template, redirect, url_for

from jinja2 import Template

import os, json, random, string, requests
import hashlib, hmac

import smtplib
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

import settings
from webex import *


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = os.urandom(24)

# global state variable
state = ''

"""
    Function Name : main_page
    Description : main landing page and kick starts oauth grant flow
"""
@app.route("/") 
def main_page():
    global state
    
    """Main Grant page"""
    state = generate_state_param()
    return render_template("index.html", client_id=settings.client_id, state=state)


"""
    Function Name : webhook
    Description : detect and respond to webhook post requests
"""
@app.route('/webhook', methods=["GET", "POST"])
def webhook():
    # Validate webhook request
    raw = request.get_data()
    key_bytes = bytes(settings.secret, 'UTF-8')
    
    hashed = hmac.new(key_bytes, raw, hashlib.sha1)
    validatedSignature = hashed.hexdigest()
    
    print('validatedSignature', validatedSignature)
    print('X-Spark-Signature', request.headers.get('X-Spark-Signature'))
    
    # If signature matches, process webhook data
    if validatedSignature == request.headers.get('X-Spark-Signature'):
        data = request.get_json()
    
        # get room name
        room = room_details(settings.oauth_token, data['data']['roomId'])

        if not room:
            print('Received error: webhook request ignored...')
            return

        room_name = room['title']
        
        # get message details
        message = message_details(settings.oauth_token, data['data']['id'])

        if not message:
            print('Received error: webhook request ignored...')
            return

        target_space = {}
        
        # Find the correct space we received the webhook on
        for space in settings.webex_spaces:
            if space == room_name:
                target_space = space
                break
        
        # Craft an email and send to everyone on the list  
        for email in settings.webex_spaces[target_space]:
            send_email(room_name, email, message)
            
    else:
        print('Secret does not match! Ignoring webhook request...')
    
    return render_template("granted.html")
    
     
"""
    Function Name : subscribe
    Description : Create webhook for designated webex spaces in settings file
"""
@app.route('/subscribe')
def subscribe():

    webhook_list = []

    # Configure webhooks for each space
    for space in settings.webex_spaces:
        print('We need a webhook for {}'.format(space))
        
        # Get room id
        room_id = get_room_id(settings.oauth_token, space)
        
        # Room not found or Error
        if not room_id:
            continue

        # Set up webhook to listen for new messages
        configure_webhook(settings.oauth_token, room_id)

    # Retrieve list of webhooks for display
    webhooks = list_webhooks(settings.oauth_token)

    if not webhooks:
        return

    for w in webhooks:
        # Only grab the webhooks we care about
        if w['name'] == 'Space Email Webhook':
            w['spaceName'] = room_details(settings.oauth_token, w['filter'].split('=')[1])['title']
            webhook_list.append(w)

    return render_template("granted.html", webhook_list=webhook_list, emails=settings.webex_spaces)
    

"""
    Function Name : oauth
    Description : After the grant button is clicked from index.html
              and the user logs into their Webex account, the 
              are redirected here as this is the html file that
              this function renders upon successful authentication
              is granted.html. else, the user is sent back to index.html
              to try again. This function retrieves the authorization
              code and calls get_tokens() for further API calls against
              the Webex API endpoints. 
"""
@app.route("/oauth") #Endpoint acting as Redirect URI.    
def oauth():
    # print("function : oauth()")
    """Retrieves oauth code to generate tokens for users"""
    returned_state = request.args.get("state")
    if returned_state == state:
        code = request.args.get("code") # STEP 2 : Capture value of the 
                                        # authorization code.
        # print("OAuth code:", code)
        # print("OAuth state:", returned_state)
        get_tokens(code)
        return redirect(url_for('subscribe'))
    else:
        return render_template("index.html")


"""
    Function Name : get_tokens
    Description : This is a utility function that takes in the 
              Authorization Code as a parameter. The code 
              is used to make a call to the access_token end 
              point on the webex api to obtain a access token
              and a refresh token that is then stored as in the 
              Session for use in other parts of the app. 
    Params:
        code: oauth code
"""
def get_tokens(code):    
    # print("function : get_tokens()")
    # print("code:", code)
    #STEP 3 : use code in response from webex api to collect the code parameter
    #to obtain an access token or refresh token
    url = "https://webexapis.com/v1/access_token"
    headers = {'accept':'application/json','content-type':'application/x-www-form-urlencoded'}
    payload = ("grant_type=authorization_code&client_id={0}&client_secret={1}&"
                    "code={2}&redirect_uri={3}").format(settings.client_id, settings.secret_id, code, settings.redirect_uri)
    req = requests.post(url=url, data=payload, headers=headers)
    results = json.loads(req.text)
    
    # print(results)
    
    settings.oauth_token = results["access_token"]
    settings.refresh_token = results["refresh_token"]
    
    print("Token stored: ", settings.oauth_token)
    print("Refresh Token stored: ", settings.refresh_token)
    return 


"""
    Function Name : generate_state_param
    Description : Generate state parameter for grant flow (random lowercase, uppercase, digit string) 
"""
def generate_state_param():
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=15))


"""
    Function Name : send_email
    Description : Send webex space message to designated email
    Params:
        room_name: webex room name
        recipient: email recipient for message
        message: message details (including time stamp, sender, contents, etc.)
"""
def send_email(room_name, recipient, message):
    
    # Src/Dest Email information
    sender = settings.email_username
    to = recipient
    
    # Create email message container
    email = MIMEMultipart("alternative")
    
    # Attach webex banner
    with open('static/images/webex_logo.png', 'rb') as f:
        # set attachment mime and file name, the image type is png
        mime = MIMEBase('image', 'png', filename='webex_logo.png')
        # add required header data:
        mime.add_header('Content-Disposition', 'attachment', filename='webex_logo_white.png')
        mime.add_header('X-Attachment-Id', '0')
        mime.add_header('Content-ID', '<0>')
        # read attachment file content into the MIMEBase object
        mime.set_payload(f.read())
        # encode with base64
        encoders.encode_base64(mime)
        # add MIMEBase object to MIMEMultipart object
        email.attach(mime)
    
    # Prepare variable components of html body
    time_stamp = message['created'].split('T')
    message_timestamp = time_stamp[0] + ' - ' + time_stamp[1][:-1]
    
    # Decide which representation of message content to include
    message_text = ''
    if "html" in message:
        message_text = message['html']
    elif "markdown" in message:
        message_text = message['markdown']
    else:
        message_text = message['text']
        
    # read in base html, create and apply jinja template to format email content
    with open('email_template.html', 'r') as fp:
        my_templ = Template(fp.read())
        
        html = my_templ.render(room_name=room_name, sender = message['personEmail'], time_stamp = message_timestamp, content=message_text)
        
        text = MIMEText(html, 'html')
        email.attach(text)
                            
    # Email meta data 
    email['From'] = sender
    email['To'] = to
    email['Subject'] = room_name + ' - Webex Space Message'
    
    try:    
        # Setup SMTP server and login
        with smtplib.SMTP(settings.smtp_domain, settings.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(user=settings.email_username, password=settings.email_password)
            server.sendmail(sender, to, email.as_string())
            
            print('Email sent successfully!')
            
    except Exception as e:
        print('There was an exception: ', e)
 
 
if __name__ == "__main__":
    app.run("0.0.0.0", port=10060, debug=False)