# Webex Integration information
client_id = '<client-id>'
secret_id = '<secret-id>'
redirect_uri = '<url>/oauth'
webhook_uri = '<url>/webhook'
secret = '<secret>'

# Note: tokens are dynamically set from oauth grant flow
oauth_token = ""
refresh_token = ""

# Webex space details - dictionaries specifying spaces and configured emails that will receive notification
webex_spaces = {
    '<example space>': ['<destination@email.com>'],
}

# Gmail SMTP Details
email_username = "<email username>"
email_password = "<app password>"
smtp_domain = "smtp.gmail.com"
smtp_port = 587

# Outlook SMTP Details
# email_username = "<email username>"
# email_password = "<email password>"
# smtp_domain = "smtp.office365.com"
# smtp_port = 587