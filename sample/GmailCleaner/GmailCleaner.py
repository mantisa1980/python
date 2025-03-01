import os
import pickle
import base64
import re
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from collections import Counter

# Define Gmail API Scopes
#SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
SCOPES = ["https://mail.google.com/"]

def my_input(prompt):
    #return input(prompt)
    return "y"

def authenticate_gmail():
    """Authenticate and return Gmail API service."""
    creds = None
    token_path = "token.pickle"

    # Load credentials from token file if it exists
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)

    # Refresh or request new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("C:\\Users\\manti\\credential\\gmail_cleaner_oauth_client.apps.googleusercontent.com.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)

def get_email_content(service, email_id):
    """Fetches the email's subject, sender, and body using the email ID."""
    try:
        message = service.users().messages().get(userId="me", id=email_id, format="full").execute()
        
        # Extract headers (Subject, From, etc.)
        headers = message["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

        # Extract body (handle both plain text and HTML)
        body = "No body found"
        if "parts" in message["payload"]:  # Handle multipart emails
            for part in message["payload"]["parts"]:
                if part["mimeType"] == "text/plain":  # Prefer plain text body
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                    break
        elif "body" in message["payload"]:
            body = base64.urlsafe_b64decode(message["payload"]["body"]["data"]).decode("utf-8")

        return {"subject": subject, "sender": sender, "body": body}
    except Exception as e:
        print(f"Error retrieving email content: {e}")
        return None

def get_emails(service, query):
    """Retrieve emails matching the search query."""
    try:
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])
        return messages
    except Exception as e:
        print("Error retrieving emails:", e)
        return []

def _process_delete_emails(service, query):
    print("query by sender:", query)
    counter=0
    while True:
        emails = get_emails(service, query)
        if len(emails) == 0:
            break
        email_ids = [email["id"] for email in emails]
        counter+=len(email_ids)
        print("Emails", emails)
        if my_input("Delete these emails? (y/n): ") == "y":
            batch_delete_emails(service, email_ids)
    print(f"successfully deleted {counter} emails for query{query}")

def batch_delete_emails(service, email_ids):
    """Deletes multiple emails in a batch request."""
    if not email_ids:
        print("No emails to delete.")
        return
    
    try:
        service.users().messages().batchDelete(userId="me", body={"ids": email_ids}).execute()
        print(f"Deleted {len(email_ids)} emails successfully.")
    except Exception as e:
        print(f"Batch delete failed: {e}")

def clean_by_sender(service, sender_email):
    query = f"from:{sender_email} AND -is:starred"
    _process_delete_emails(service, query)

def clean_by_subject(service, subject_pattern):
    query = f"subject:{subject_pattern} AND -is:starred"
    _process_delete_emails(service, query)

def clean_by_category(service, category_pattern):
    query = f"category:{category_pattern} AND -is:starred"
    _process_delete_emails(service, query)

def main(service):
    
    patterns = [
#        "emms@billing.tbb.com.tw", 
#        "no-reply@kingnetsmart.com.tw",
#        "invitations@linkedin.com",
#        "newsletter@digitaltrends.com",
#        "info@meetup.com",
#        "yo@dev.to",
#        "comp.lang.python@googlegroups.com",
#        "notifications@github.com",
#        "services@org1-mailhunter.standardchartered.com.tw",
#        "cwgbkk@cw.com.tw",
        "MMA@mx1.edm.sinopac.com",
    ]
    #for pattern in patterns:
    #    clean_by_sender(service, pattern)

    query_type = input("query type (sender/subject/category): ")
    if query_type == "sender":
        while True:
            query = input("input sender email address:\n")
            clean_by_sender(service, query)
    elif query_type == "subject":
        while True:
            query = input("input subject pattern:\n")
            clean_by_subject(service, query)
    elif query_type == "category":
        while True:
            query = input("input category pattern:(ex. promotions)\n")
            clean_by_category(service, query)

if __name__ == "__main__":
    service = authenticate_gmail()
    main(service)
   
