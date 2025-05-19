import os
import smtplib

from email_validator import validate_email


def checkEmailIsValid(email):
    try:
        v = validate_email(email)
        email = v["email"]
        return True, email
    except Exception as e:
        # email is not valid, exception message is human-readable
        return False, str(e)


def createSMTPServer():
    try:
        smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
        print(smtp_object.ehlo())
        smtp_object.starttls()

        password = os.environ.get('PASSWORD')
        email = os.environ.get('EMAIL')
        smtp_object.login(email, password)

        return smtp_object

    except Exception as error:
        print("An exception occurred:", type(error).__name__, "–", error)
        raise Exception(" Could not connect to SMTP server")


def sendEmail(data, email, adminEmail, errorFile):
    smtp_object = createSMTPServer()
    try:
        smtp_object.sendmail(adminEmail, email, data)
        return True
    except Exception as error:
        # handle the exception
        print("An exception occurred:", type(error).__name__, "–", error)
        errorFile.write(" Could not send email to emailID: " + email + "\n")
        return False

    smtp_object.quit()
