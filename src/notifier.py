import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_commit_status(repo, commit_sha, status, token):
    """Sends a commit status update to GitHub."""
    url = f"https://api.github.com/repos/{repo}/statuses/{commit_sha}"
    
    if status == "success":
        state = "success"
        description = "CI build succeeded!"
    elif status == "failure":
        state = "failure"
        description = "CI build failed."
    else:
        state = "pending"
        description = "CI build in progress..."

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "state": state,
        "description": description,
        "context": "continuous-integration/custom-ci",
        "target_url": f"https://github.com/{repo}/actions"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            logging.info(f"Successfully updated commit status for {commit_sha}")
        else:
            logging.error(f"Failed to update commit status. Status code: {response.status_code}")
            logging.error(f"Response: {response.text}")
    except Exception as e:
        logging.error(f"Error sending commit status: {str(e)}")

def send_email_notification(recipient, subject, message, smtp_server, smtp_port, sender_email, sender_password):
    """Sends an email notification with build results."""
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        logging.info(f"Successfully sent email to {recipient}")
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")

def send_notification(status, repo=None, commit_sha=None, token=None, email_config=None):
    """Handles sending notifications (commit status or email) based on config."""
    logging.info(f"Processing notification with status: {status}")
    
    # Send commit status update if repository details are provided
    #if repo and commit_sha and token:
    send_commit_status(repo, commit_sha, status, token)
    
#     # Send email notification if email configuration is provided
#     if email_config:
#         message = f"""
# CI Build Notification
# 
# Status: {status}
# Repository: {repo}
# Commit: {commit_sha}
# 
# For more details, please check the repository.
# """
#         
#         try:
#             send_email_notification(
#                 recipient=email_config.get("recipient"),
#                 subject=f"CI Build Status: {status}",
#                 message=message,
#                 smtp_server=email_config.get("smtp_server"),
#                 smtp_port=email_config.get("smtp_port"),
#                 sender_email=email_config.get("sender_email"),
#                 sender_password=email_config.get("sender_password")
#             )
#         except Exception as e:
#             logging.error(f"Failed to send email notification: {str(e)}")