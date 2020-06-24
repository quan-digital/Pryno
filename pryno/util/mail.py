# -*- coding: utf-8 -*-

# - Mail tools -
# * Quan.digital *

import smtplib
import datetime as dt
from email.message import EmailMessage
import pryno.util.settings as settings


def send_email(message, destination=settings.MAIL_TO_ERROR):
    # Connect to server
    server = smtplib.SMTP('smtp.gmail.com', 587)  # 465 1025
    # Secure connection
    server.starttls()
    # Login
    server.login(settings.BOT_MAIL, settings.BOT_PWD)

    # Compose message
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = str("Pryno: Something is up with " + settings.CLIENT_NAME)
    msg['From'] = settings.BOT_MAIL
    msg['To'] = destination
    server.send_message(msg)

    # Quit
    server.quit()


if __name__ == '__main__':
    msg = EmailMessage()
    msg["From"] = "pipryno@gmail.com"
    msg["Subject"] = "Pryno Exception for {0}".format(settings.CLIENT_NAME)
    msg["To"] = settings.MAIL_TO_ERROR
    msg.set_content(
        "Exception occured, processRunner had to restart '%s' bot. \n \
Please check the following error log, master." %
        settings.CLIENT_NAME)
    error_path = settings.LOG_DIR + 'errors_' + \
        str(dt.datetime.today().strftime('%Y-%m-%d')) + '.txt'
    try:
        msg.add_attachment(
            open(
                error_path,
                "r").read(),
            filename="error_file.txt")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(settings.BOT_MAIL, settings.BOT_PWD)
        server.send_message(msg)
        print('Error mail sent.')
    except BaseException:
        print('First run, no mails sent.')
