import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Emailer:
    def __init__(self):
        SMTP_SERVER = "smtp.office365.com"
        SMTP_PORT = 587


