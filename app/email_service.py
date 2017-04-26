# -*- coding:utf-8 -*-
"""http://stackoverflow.com/questions/882712/sending-html-email-using-python"""

import smtplib
import yagmail
import codecs
import config


if __name__ == "__main__":
    try:
        server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server_ssl.login('nathan.cheever12@gmail.com', 'NYCis8rH0^^e')
    except Exception as e:
        print("something went wrong in email: {}".format(e))
    else:
        subject = "Your weekly newsletter!"
        html = codecs.open("templates/newsletter.html", 'r', 'utf-8').read()
        server_ssl.sendmail(msg=html, from_addr=config.MAIL_USERNAME, to_addrs=config.MAIL_USERNAME)
        server_ssl.close()

    # # yagmail.register("{}".format(config.MAIL_USERNAME), "{}".format(config.MAIL_PASSWORD))
    # with yagmail.SMTP("{}".format(config.MAIL_USERNAME)) as yag:
    #
    #
    #     yag.send(to="{}".format(config.MAIL_USERNAME), subject=subject, contents=html)

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
