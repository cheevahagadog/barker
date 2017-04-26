# -*- coding:utf-8 -*-
"""http://stackoverflow.com/questions/882712/sending-html-email-using-python"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import html2text
import codecs
import config


if __name__ == "__main__":
    msg = MIMEMultipart('alternative')
    with codecs.open("app/templates/newsletter.html", 'r', 'utf-8') as fp:
        html = fp.read()
    text = html2text.html2text(html)
    try:
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        s.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
    except Exception as e:
        print("something went wrong in setting up smtp: {}".format(e))
    else:
        msg['Subject'] = "Your weekly newsletter!"
        msg['From'] = config.MAIL_USERNAME
        msg['To'] = config.MAIL_USERNAME

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        s.sendmail(msg=msg.as_string(), from_addr=config.MAIL_USERNAME, to_addrs=config.MAIL_USERNAME)
        s.quit()
