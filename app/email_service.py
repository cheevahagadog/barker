# -*- coding:utf-8 -*-
"""http://stackoverflow.com/questions/882712/sending-html-email-using-python"""
import yagmail
import codecs
from ..barker import config


if __name__ == "__main__":
    # yagmail.register("{}".format(config.MAIL_USERNAME), "{}".format(config.MAIL_PASSWORD))
    yag = yagmail.SMTP("{}".format(config.MAIL_USERNAME))
    subject = "Your weekly newsletter!"

    f = codecs.open("templates/newsletter.html", 'r', 'utf-8')
    html = f.read()
    yag.send(to="{}".format(config.MAIL_USERNAME), subject=subject, contents=html)

    # message = Message(From="{}".format(config.MAIL_USERNAME),
    #                   To="{}".format(config.MAIL_USERNAME))
    # message.Subject = "An HTML Email"
    # message.Html = """<p>Hi!<br>
    #    How are you?<br>
    #    Here is the <a href="http://www.python.org">link</a> you wanted.</p>"""
    #
    # sender = Mailer('smtp.gmail.com', port=587, use_tls=True, usr=config.MAIL_USERNAME, pwd=config.MAIL_PASSWORD)
    # print("sending...")
    # sender.send(message)
