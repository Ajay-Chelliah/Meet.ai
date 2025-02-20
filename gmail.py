# Step 1: Import Libraries
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

# Step 2: Authentication using token.json
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

creds = Credentials.from_authorized_user_file("token.json", SCOPES)

# Step 3: Build Gmail Service
service = build("gmail", "v1", credentials=creds)


# Step 4: Create Email Message
def create_message(sender, to, subject, message_text):
    message = MIMEMultipart()
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    message.attach(MIMEText(message_text, "plain"))
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


# Step 5: Send Email
def send_email(service, user_id, message):
    try:
        sent_message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        print(f"Message sent. Message Id: {sent_message['id']}")
    except Exception as error:
        print(f"An error occurred: {error}")


__all__ = ["service", "create_message", "send_email"]


# Step 6: Use the functions to send the email
# if __name__ == "__main__":
#     sender = "ajaychelliah842005@gmail.com"
#     to = "ajay8425p@gmail.com"
#     subject = "Meeting Summary"
#     message_text = "Here are the key points from the meeting..."

#     message = create_message(sender, to, subject, message_text)
#     send_email(service, "me", message)
