  
import smtplib
import datetime as dt
from email.message import EmailMessage
import pryno.util.settings as settings


if __name__ == '__main__':
    msg = EmailMessage()
    msg["From"] = "pipryno@gmail.com"
    msg["Subject"] = "Pryno Error for {0}".format(settings.CLIENT_NAME)
    msg["To"] = settings.MAIL_TO_ERROR
    msg.set_content("Error occured, processRunner had to restart '%s' bot. \n \
Please check the following error log, master." % settings.CLIENT_NAME)
    error_path = settings.LOG_DIR + 'errors_' + str(dt.datetime.today().strftime('%Y-%m-%d')) + '.txt'
    try:
        msg.add_attachment(open(error_path, "r").read(), filename="error_file.txt")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("pipryno@gmail.com", "SurubaoParaiso123")
        server.send_message(msg)
        print('Error mail sent.')
    except:
        print('First run, no mails sent.')