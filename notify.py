"""
Email Notifications
"""

from flask_mail import Mail, Message
from app import app, configs
from demo import iftoday, timediff
from services.models.signals import SignalModel

# configuration of email
app.config["MAIL_SERVER"] = configs.get("EMAIL", "MAIL_SERVER")
app.config["MAIL_PORT"] = int(configs.get("EMAIL", "MAIL_PORT"))
app.config["MAIL_USERNAME"] = configs.get("EMAIL", "MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = configs.get("EMAIL", "MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = configs.getboolean("EMAIL", "MAIL_USE_TLS")
app.config["MAIL_USE_SSL"] = configs.getboolean("EMAIL", "MAIL_USE_SSL")

email_subject = configs.get("EMAIL", "MAIL_SUBJECT")
email_body = configs.get("EMAIL", "MAIL_BODY")
email_sender = configs.get("EMAIL", "MAIL_SENDER")
email_recipient = configs.get("EMAIL", "MAIL_RECIPIENT")

mail = Mail(app)  # instantiate the mail class


def get_waiting_time(signal_to_check):

    send_email = False
    warned = False
    print("*** checking to warn ***")

    if signal_to_check:
        if iftoday(str(signal_to_check.timestamp)):
            diff = timediff(str(signal_to_check.timestamp))

            if signal_to_check.error_msg:
                if "(warned)" in signal_to_check.error_msg:
                    warned = True

            if int(diff) > 2 and not warned:
                print("*** SENDING EMAIL ****")
                send_email = True

    else:
        print("*** nothing to warn ***")

    return send_email


def warning_email_context():

    with app.app_context():  # being executed outside the app context
        try:

            signal_to_check = SignalModel.check_latest()

            send_email = get_waiting_time(signal_to_check)

            if send_email:
                msg = Message(
                    email_subject, sender=email_sender, recipients=[email_recipient]
                )
                msg.body = email_body
                mail.send(msg)
                print("*** warning email sent...***")

                if signal_to_check.error_msg:
                    signal_to_check.error_msg = signal_to_check.error_msg + "(warned)"
                else:
                    signal_to_check.error_msg = "(warned)"

                signal_to_check.update(signal_to_check.rowid)

            else:

                print("*** no email ***")

        except Exception as e:
            print("*** Email Notification Error ***")
            print(e)
