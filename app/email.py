
from threading import Thread
from flask import current_app, render_template
from flask.ext.mail import Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['IFIND_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['IFIND_MAIL_SENDER'], recipients=[to])
    msg.body = "You have successfully registered with IFindCard"
    msg.html =  "<h2>You have successfully registered with IFindCard</h2>"
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
