import os
import smtplib

smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
print(smtp_object.ehlo())

smtp_object.starttls()

# password = getpass.getpass(prompt='Password: ', stream=None)
# email = getpass.getpass(prompt='Email: ', stream=None)
password = os.environ.get('PASSWORD')
email = os.environ.get('EMAIL')
print(smtp_object.login(email, password))

from_address = email
to_address = email
subject = 'Ticket Form'
message = 'Ticket Form'

smtp_object.sendmail(from_address, to_address, subject)
