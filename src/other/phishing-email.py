#/usr/bin/env python3

import os
import ssl
import smtplib
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class PhishingEmail:
    def __init__(self):
        self.attacker_email = None
        self.attacker_pass = None
        self.victim_email = None
        self.subject = None
        self.body = None
        self.attachment_path = None

    def clear(self):
        cmd = 'cls' if os.name == 'nt' else 'clear'
        os.system(cmd)

    def get_creds(self):
        self.clear()
        self.attacker_email = input("Enter attacker email: ")
        self.attacker_pass = getpass.getpass("Enter attacker's password email: ")
        self.victim_email = input("Enter victim's email: ")
        self.subject = input("Enter header of emails' message: ")
        self.body = input("Enter main mesage: ")

        file_choice = str(input("Do you want to pin the file? [Y/n]: ")).lower()
        if file_choice in['', 'y', 'yes']:
            self.attachment_path = input("Enter path to file: ")

    def send_email(self):
        try:
            message = MIMEMultipart()
            message["From"] = self.attacker_email
            message["To"] = self.victim_email
            message["Subject"] = self.subject

            message.attach(MIMEText(self.body, "plain"))

            if self.attachment_path and os.path.exists(self.attachment_path):
                with open(self.attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
            
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(self.attachment_path)}",
                )

                message.attach(part)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.attacker_email, self.attacker_pass)
                server.send_message(message)

            print("Email successfully sent. GoodBye!")

        except Exception as e:
            print(f"Erorr sending email {e}")

def main():
    email = PhishingEmail()
    email.clear()
    email.get_creds()
    email.send_email()

if __name__ == '__main__':
    main()
