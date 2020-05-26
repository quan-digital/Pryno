import os
import sys
import smtplib
from datetime import datetime
from optparse import OptionParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import EmailMessage
import pryno.util.settings as settings


bot_mail = "pipryno@gmail.com"
bot_pwd = "SurubaoParaiso123"
# Birth date 10/03/2000
port = 587 #465 1025

# Parser to receive inputs
parser = OptionParser()
# Error message
parser.add_option("-e", "--error", dest="error", help="Error message.")
# Error file
parser.add_option("-f", "--file", dest="file", help="Error file.")

# Parser handling
(options, args) = parser.parse_args()
errorMessage = str(options.error)
fileName = str(options.file)


def send_email(message,destination=settings.MAIL_TO_ERROR):
    # Connect to server
    server = smtplib.SMTP('smtp.gmail.com', port)
    # Secure connection
    server.starttls()
    # Login
    server.login(bot_mail,bot_pwd)

    # Compose message
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = str("Pryno: Something is up with " + settings.MAIL_NAME)
    msg['From'] = bot_mail
    msg['To'] = destination
    server.send_message(msg)

    # Quit
    server.quit()

if __name__ == '__main__':
    msg = EmailMessage()
    msg["From"] = "pipryno@gmail.com"
    msg["Subject"] = "Pryno Error"
    msg["To"] = settings.MAIL_TO_ERROR
    msg.set_content("Error occured, processRunner had to restart Pryno. \n \
        Please check the following error log, master.")
    error_path = settings.LOG_DIR + 'errors_' + str(datetime.today().strftime('%Y-%m-%d')) + '.txt'
    try:
        msg.add_attachment(open(error_path, "r").read(), filename="error_file.txt")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("pipryno@gmail.com", "SurubaoParaiso123")
        server.send_message(msg)
        print('Error mail sent.')
    except:
        print('First run, no mails sent.')


