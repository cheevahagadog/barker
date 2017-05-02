# -*- coding:utf-8 -*-
"""http://stackoverflow.com/questions/882712/sending-html-email-using-python"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import html2text
import codecs
import config


class EmailService(object):
    """Loads the newsletter and sends the email"""

    def __init__(self):
        self.msg = MIMEMultipart('alternative')

    @staticmethod
    def load_newsletter_html():
        """Loads html newsletter and returns a html file and a text file to be used by email service"""
        with codecs.open("app/templates/newsletter.html", 'r', 'utf-8') as f:
            html = f.read()
        text = html2text.html2text(html)
        return text, html

    @staticmethod
    def attempt_login():
        """Attempts to connect to Gmail server using the email address and password of the user"""
        try:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
        except Exception as e:
            if config.VERBOSE:
                print("something went wrong in setting up smtp: {}".format(e))
            return False, None
        else:
            return True, server

    def format_and_send_email(self, text, html, server):
        """Fills in email and sends
        
        Args:
            text: html newsletter converted to plain text
            html: actual html for newsletter to be sent
            server: server connection
        """
        self.msg['Subject'] = config.PERSONAL_DATA.get('EMAIL_SUBJECT')
        self.msg['From'] = config.MAIL_USERNAME
        self.msg['To'] = config.MAIL_USERNAME
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        self.msg.attach(part1)
        self.msg.attach(part2)
        server.sendmail(msg=self.msg.as_string(), from_addr=config.MAIL_USERNAME, to_addrs=config.MAIL_USERNAME)
        server.quit()

    def main(self):
        """Run email service"""
        success, server = self.attempt_login()
        if success:
            text, html = self.load_newsletter_html()
            self.format_and_send_email(text=text, html=html, server=server)
        else:
            if config.VERBOSE:
                print("Unable to send email")


if __name__ == "__main__":
    emailer = EmailService()
    emailer.main()
