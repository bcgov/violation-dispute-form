import logging

from django.conf import settings

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

from smtplib import SMTP, SMTPException

LOGGER = logging.getLogger(__name__)


def send_email(recipient_email: str, pdf_data: bytes):
    server_addr = settings.SMTP_SERVER_ADDRESS
    sender_email = settings.SMTP_SENDER_EMAIL
    sender_name = settings.SMTP_SENDER_NAME
    if not server_addr:
        LOGGER.debug("SMTP server address not configured")
        return
    if not sender_email:
        LOGGER.error("Sender email address not configured")
        return
    if not recipient_email:
        LOGGER.error("No recipient email address provided")
        return

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

    LOGGER.info("Recipient email address: %s", recipient_email)

    sender_info = formataddr((str(Header(sender_name, "utf-8")), sender_email))

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    # # Add file as application/octet-stream
    # # Email client can usually download this automatically as attachment
    base = MIMEBase("application", "octet-stream")
    base.set_payload(pdf_data)
    encoders.encode_base64(base)

    # # Add header as key/value pair to attachment part
    base.add_header("Content-Disposition", 'attachment; filename="report.pdf"')
    # # Add attachment to message and convert message to string
    msg.attach(base)
    text = msg.as_string()

    with SMTP(server_addr) as smtp:
        try:
            smtp.sendmail(sender_info, (recipient_email,), text)
            LOGGER.debug("Email sent successfully!")
        except SMTPException as err:
            LOGGER.exception("Email failed!", err)
