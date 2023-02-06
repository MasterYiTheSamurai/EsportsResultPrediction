import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import os
import sys


def send_mail(send_from, send_to, subject, text,password):

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    with open(os.getcwd() + "/results.txt", "r") as fil:
        part = MIMEApplication(
            fil.read(),
            Name=basename(os.getcwd() + "/results.txt")
        )
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(os.getcwd() + "/results.txt")
        msg.attach(part)

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(send_from, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()


send_mail("blasko.gergo.hun@gmail.com","blasko.gergo.hun@gmail.com","Your Daily Dose of Esports Results","",sys.argv[1])