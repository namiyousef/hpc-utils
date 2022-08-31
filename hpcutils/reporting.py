import os
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from email.utils import make_msgid
from hpcutils.config import EMAIL, EMAIL_PASSWORD

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter
date_format = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s', datefmt=date_format)
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
LOGGER.addHandler(ch)


def _generate_msg_id():
    my_id = make_msgid()
    os.environ['EMAIL_ID'] = my_id
    return my_id

def send_email(
        receiver,
        subject,
        mail_content,
        images=[],
        email_id=None,
):

    # Setup the MIME
    message = MIMEMultipart()
    message['Message-ID'] = _generate_msg_id()
    message['From'] = EMAIL
    message['To'] = receiver
    message['Subject'] = subject

    if email_id:
        message["In-Reply-To"] = email_id
        message["References"] = email_id

    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))
    for img_buffer in images:
        message.attach(MIMEImage(img_buffer))

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(EMAIL, EMAIL_PASSWORD)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(EMAIL, receiver, text)
    session.quit()
    LOGGER.info('Sent email.')

def create_email_content():
    pass

def job_start_report(subject, recipients, metadata_path):
    with open(metadata_path, 'r') as f:
        json_str = json.dumps(json.load(f))
    mail_content = json_str
    send_email(
        receiver=recipients,
        subject=subject,
        mail_content=mail_content
    )

def job_completion_report(subject, recipients):
    email_id = os.environ.get('EMAIL_ID')
    send_email(
        receiver=recipients,
        subject=subject,
        mail_content='Job complete',
        email_id=email_id
    )

def main():
    import sys
    report_type = sys.argv[1]
    subject = sys.argv[2]
    recipients = sys.argv[3]

    if report_type == 'start':
        path = sys.argv[4]
        job_start_report(subject, recipients, path)
    elif report_type == 'end':
        job_completion_report(subject, recipients)


if __name__ == '__main__':
    main()