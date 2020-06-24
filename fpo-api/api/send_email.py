from smtplib import SMTP, SMTPException
import logging

from string import Template
import smtplib , ssl , email
import os

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from email.utils import formataddr
from email.header import Header

LOGGER = logging.getLogger(__name__)

def send_email(receiver_email, pdf):
    server_addr = os.environ.get("SMTP_SERVER_ADDRESS")
    sender_email= os.environ.get("SENDER_EMAIL")
    sender_name = os.environ.get("SENDER_NAME")

   
    subject = "Responded to attend your Traffic Hearing"
    body = """\
    <html>
    <body>
    <p>Hi,<br></p>
       <b>Thank-you for choosing how you wish to attend your traffic hearing.<b>
       <p>A copy of your completed form is attached for your records.</p>
       <p>Your preference will be reviewed, and a Notice of Hearing will be sent in the mail telling you of the date and time of your hearing. The notice will also tell you whether you will be attending your hearing in-person, by telephone or by video and will provide you with important information about attending your hearing.</p>
       <p>If you want to learn more about the hearing process, please visit the Provincial Court of British Columbia¿s website and read their Guide to Disputing a Ticket which is found here: https://www.provincialcourt.bc.ca/downloads/Traffic/Traffic-Court-Guide.pdf
          If you have any questions, please contact the Violation Ticket Centre at: 1-877-661-8026</p>
    </body>
    </html>
    """ 

    LOGGER.info("User's email Id is  %s>", receiver_email)
    
    sender_info = formataddr((str(Header(sender_name, "utf-8")), sender_email))

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    
    msg.attach(MIMEText(body, "html"))

    # # Add file as application/octet-stream
    # # Email client can usually download this automatically as attachment
    base=MIMEBase("application", "octet-stream")
    base.set_payload(pdf) 
    encoders.encode_base64(base)

    # # Add header as key/value pair to attachment part
    base.add_header('Content-Disposition','attachment; filename="report.pdf"')
    # # Add attachment to message and convert message to string
    msg.attach(base)
    text = msg.as_string()

    with SMTP(server_addr) as smtp:
        try:
            smtp.sendmail(sender_info, (receiver_email,), text)
            LOGGER.debug("Email sent successfully!")
        except SMTPException as err:
            LOGGER.exception("Email failed!", err)


