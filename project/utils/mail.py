def user_mail_register(title,body,email):
    from flask import render_template
    from project import mail
    from flask_mail import Message
    msg = Message(title, sender="faizandiwan921@gmail.com",
                      recipients=[email])
    msg.html = render_template('otp.html', otp=body)
    msg.body = body
    mail.send(msg)