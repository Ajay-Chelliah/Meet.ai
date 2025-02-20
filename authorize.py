# import os
# import json
# import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for sending emails
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def main():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials for future use
    with open("token.json", "w") as token_file:
        token_file.write(creds.to_json())
    print("Authorization successful! token.json saved.")


if __name__ == "__main__":
    main()
