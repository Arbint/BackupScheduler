import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Emailer:
    def __init__(self):
        self.SMTP_SERVER = "smtp.gmail.com"
        self.SMTP_PORT = 587
        
        self.EMAIL_ADDRESS = os.getenv("PERFORCE_GMAIL")
        self.EMAIL_PASSWORD = os.getenv("PERFORCE_GMAIL_APP_PWD")

    def SendGroupEmail(self, recipients, subject, body):
        try:
            server = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
            server.starttls()
            server.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)

            batchSize = 100
            for i in range(0, len(recipients), batchSize):
                batchRecipents = recipients[i : i+batchSize]

                msg = MIMEMultipart()
                msg["From"] = self.EMAIL_ADDRESS
                msg["Subject"] = subject
                msg.attach(MIMEText(body, "plain"))

                server.sendmail(self.EMAIL_ADDRESS, batchRecipents, msg.as_string())
                print(f"Send batch {i  // batchSize+1} to {len(batchRecipents)} recipients")
                time.sleep(1)
                
            server.quit()
            print("Emails sent successfully")

        except Exception as e:
            print(f"Error: {e}")
        

    def SendEMail(self, to, subject, body):
        msg = MIMEMultipart()
        msg["From"] = self.EMAIL_ADDRESS
        msg["To"] = to
        msg["Subject"] = subject 

        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT)
            server.starttls()
            server.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
            server.sendmail(self.EMAIL_ADDRESS, msg["To"], msg.as_string())
            server.quit()
            
        except Exception as e:
            print(f"Error: {e}")

