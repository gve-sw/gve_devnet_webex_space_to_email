# gve_devnet_webex_space_to_email

This prototype flask application registers a 'new messages' webhook with a webex space, and upon receiving a message, creates and sends an email with the message content to a list of emails. 
Examples are provided for a gmail source email (mailer@gmail.com) and an outlook source email (mailer@outlook.com). A custom email template can also be provided (or the default email template can be used).

## Contacts
* Trevor Maco
* Jorge Banegas

## Solution Components
* Webex Teams
* Email (GMail, Outlook)
* Flask
* Python 3.10

## Installation/Configuration

1. Clone this repository with `git clone https://github.com/gve-sw/gve_devnet_webex_space_to_email` and open the directory of the root repository.

2. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).

3. Install the required Python libraries with the command:
   ``` bash
   pip3 install -r requirements.txt
   ```

4. Rename `settings_template.py` file to `settings.py` and fill in the webex integration fields, the list of webex spaces, and the gmail/outlook details.

    **Note**: This prototype was tested with ngrok, and example settings target this deployment. Refer to this [link](https://ngrok.com/docs/getting-started) if unfamiliar with ngrok. Be sure to launch a session with port `10060`!
   1. Webex Integration: 
      * Please refer to this guide for creating a webex integration: https://developer.webex.com/docs/integrations.
        * Important fields are: `Redirect URI(s)`, and `Scopes` (other fields can contain whatever you like)
          * Redirect URI: This must be of the format `<url>/oauth` where 'url' is the url of the flask app. If using ngrok and testing locally, this would be `http://0.0.0.0:10060/oauth`.
          * Scopes: You must minimally specify `spark:messages_read` and `spark:rooms_read`.
      * Once created, fill in `settings.py` fields. 
        * Values from the webex integration page: Redirect URI must match!
        ``` python
        client_id = '<client-id>'
        secret_id = '<secret-id>'
        redirect_uri = '<url>/oauth'
        ```
        * webhook_uri: This must be of the format `<url>/webhook` where 'url' is the flask app if hosted or ngork url if local.
        ``` python 
        webhook_uri = '<url>/webhook'
        ```
        * secret: random 10 character alphanumeric string
        ``` python 
        secret = '<something>'
         ```
      * Copy `OAuth Authorization URL` from integration page and replace `index.html` line 17 href tag contents. Replace the client_id url parameter and the state parameter with `{{client_id}}` and `{{state}}` respectively. Your href tag should look like this:
        ``` python
        <a href='https://webexapis.com/v1/authorize?client_id={{client_id}}&response_type=code&redirect_uri=http%3A%2F%2F0.0.0.0%3A10060%2Foauth&scope=spark%3Akms%20spark%3Arooms_read%20spark%3Amessages_read&state={{state}}'><button class="btn btn--primary">Grant</button></a>
         ```
   2. Webex Spaces: Enter webex spaces and the emails you wish to forward to. Use a dictionary with the key being the space name, and value a list of emails:
         ``` python
      {
        '<example space>': ['<destination@email.com>'],
      }
         ```
   3. Email Settings
      * Gmail: Requires an 'app password' and some setup. Refer to this guide - https://support.google.com/accounts/answer/185833?visit_id=638001725430109553-3882188526&p=InvalidSecondFactor&rd=1
         * Once configured, enter email username and app password:
        ```python
        email_username = "<email username>"
        email_password = "<app password>"
        ```
      * Outlook: Several configurations
        * If 2-factor is **NOT** configured, enter account username and password
        ```python
        email_username = "<email username>"
        email_password = "<email password>"
        ```
        * If 2-factor **is** configured: Refer to this guide - https://support.microsoft.com/en-us/account-billing/manage-app-passwords-for-two-step-verification-d6dc8c6d-4bf7-4851-ad95-6d07799387e9#:~:text=Sign%20in%20to%20your%20work%20or%20school%20account%2C%20go%20to,page%2C%20and%20then%20select%20Done
        * For **Corporate** Outlook accounts: Refer to this guide - https://learn.microsoft.com/en-us/exchange/clients-and-mobile-in-exchange-online/authenticated-client-smtp-submission

5. Provide a html email template for delivery to the destination email address (or use the default template `email_template.html`)

   **Note:** Important Requirements:
      1. Your file **must** be named `email_template.html`, and located in the project directory
      2. The file must support Jijna templating and include the fields: room_name, sender, time_stamp, content. For ex:
          ``` python
         html = my_templ.render(room_name=room_name, sender = message['personEmail'], time_stamp = message_timestamp, content=message_text)
         ```
            Refer to app.py: `send_email` method to explore these fields further.
      3. For a custom banner, include a `.png` file in `static/images/`, and specify the file in app.py: line 213
          ``` python
         with open('static/images/webex_logo.png', 'rb') as f:
         ```
   
## Usage

1. To start flask app:
   ``` bash
    python3 app.py
    ```

2. Navigate to webpage, you should see the landing page:

![/IMAGES/landing-page.png](/IMAGES/landing-page.png)

3. Click 'Grant' to launch integration authorization flow. You should be presented with the following page (**note**: you may need to log into webex):

![/IMAGES/integration-permissions.png](/IMAGES/integration-permissions.png)

4. You will be redirected to a status page showing configured webhooks for each space.
5. 
![/IMAGES/webhook_status.png](/IMAGES/webhook_status.png)

5. Once a message is received in a configured space, you will get an email that looks like (if using the default template):

![/IMAGES/delivered-email.png](/IMAGES/delivered-email.png)

### SCREENSHOTS

![/IMAGES/0image.png](/IMAGES/0image.png)

### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.


### Resources

* Webex Integration:
  * Configuring Oauth for Webex Integration - https://developer.webex.com/blog/using-oauth-2-with-webex-in-your-flask-application

* Email Configuration:
  * Gmail 2 factor app password: https://support.google.com/accounts/answer/185833?visit_id=638001725430109553-3882188526&p=InvalidSecondFactor&rd=1
  * Outlook 2 factor app password: https://support.microsoft.com/en-us/account-billing/manage-app-passwords-for-two-step-verification-d6dc8c6d-4bf7-4851-ad95-6d07799387e9#:~:text=Sign%20in%20to%20your%20work%20or%20school%20account%2C%20go%20to,page%2C%20and%20then%20select%20Done. 
  * Outlook SMTP settings: https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353
  * Enabling SMTP 587 communication in corporate outlook: https://learn.microsoft.com/en-us/exchange/clients-and-mobile-in-exchange-online/authenticated-client-smtp-submission

* Troubleshooting:
  * SSL Cert issues: https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate