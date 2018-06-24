# Import smtplib for the actual sending function
import smtplib

ADMIN_EMAILS = ['dat@cgito.net']
G_USER = 'info@mdanerichardson.com'
G_PW = 'Snow1007!'

def send_email(user, pwd, server_ip):
    recipient = ADMIN_EMAILS
    subject = "Captcha solving"
    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject

    # Prepare actual message
    message = """Captcha is showing for user: %s\n\n password:%s\n\n
    from server: %s\n\n
    """ % (user, pwd, server_ip)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(G_USER, G_PW)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the mail')
    except:
        print("failed to send mail")