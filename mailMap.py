import imaplib

def connectMail(user, password):
    url = 'imap.gmail.com'
    try:
        mail = imaplib.IMAP4_SSL(url)
        mail.login(user, password)
        mail.select('inbox')
        return mail
    except Exception as e:
        logging.error("Connection Failed, reason: {}".format(e))
        raise
