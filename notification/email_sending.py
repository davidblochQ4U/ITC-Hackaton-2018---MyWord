import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class notification:

	def __init__(self):
		self.EMAIL_SENDER = "mywordltd@gmail.com"
		self.PASSWORD = "ALEXIS1993david$"
		self.html=open("../notification/newsletter.html", 'r').read()
		self.BODY_HTML = '<!DOCTYPE html><html><head><title>Test</title></head><body>This is an <b>HTML</b> test.</body></html>'


	def send_email(self, email_addr, message):
		messaging = MIMEMultipart('alternative')
		messaging.attach(MIMEText(self.html.replace('SUSPICIOUS_MESSAGE', message), 'html'))
		with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
		    # Encrypting the connection:
		    smtp.starttls()
		    # Logging in and sending the email:
		    smtp.login(self.EMAIL_SENDER, self.PASSWORD)
		    smtp.send_message(messaging, self.EMAIL_SENDER, email_addr)
