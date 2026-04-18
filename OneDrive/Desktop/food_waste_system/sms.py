from twilio.rest import Client

def send_sms(to_number, message):

    account_sid = "YOUR_ACCOUNT_SID"
    auth_token = "YOUR_AUTH_TOKEN"

    client = Client(account_sid, auth_token)

    client.messages.create(
        body=message,
        from_="+1234567890",   # Twilio number
        to=to_number
    )