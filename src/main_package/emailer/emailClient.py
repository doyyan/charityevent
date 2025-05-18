try:
    smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
    print(smtp_object.ehlo())
    smtp_object.starttls()

    password = os.environ.get('PASSWORD')
    email = os.environ.get('EMAIL')
    smtp_object.login(email, password)

except Exception as error:
    print("An exception occurred:", type(error).__name__, "–", error)
    raise Exception(" Could not connect to SMTP server")