# First let's get jinja2
# We will need smtplib to connect to our smtp email server
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from jinja2 import Template

try:
    name = datetime.now().strftime("%Y%m%d%H%M%S")
    logFile = open(name + ".log", 'a+')
    errorFile = open(name + ".err", 'a+')
finally:
    print(' Files opened successfully')

adminEmail = "ravi.sivaraj@gmail.com"

# Read the Jinja2 email template
with open("paymentrequest.html", "r") as file:
    template_str = file.read()
    jinja_template = Template(template_str)
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

people_data = [
    {"guestName": "Mrs Priya Ravikumar", "email": "priyaravikumar2000@yahoo.com", "adultNos": 2, "kidsNos": 2,
     "voluntaryPrice": 100, "raffle": 5, "uniqueRef": "PR1"},
    # {"guestName": "Jane Smith", "email": "ravi.sivaraj@gmail.com", "adultNos": 2, "kidsNos": 0,
    #  "voluntaryPrice": 0, "uniqueRef": "JS001"},
    # {"guestName": "Bob Johnson", "email": "ravi.sivaraj@gmail.com",
    #  "adultNos": 0, "kidsNos": 2, "voluntaryPrice": 100, "uniqueRef": "JD001"
    #  },
]

subject = "Dance Beatz Charity Dance Show 2025"
adultCost = 12
kidsCost = 6
raffleCost = 1
# Now we iterate over our data to generate and send custom emails to each
for person in people_data:
    kidsPrice = person["kidsNos"] * kidsCost
    adultsPrice = person["adultNos"] * adultCost
    voluntaryPrice = person["voluntaryPrice"]
    raffle = person["raffle"] * raffleCost
    totalPrice = kidsPrice + adultsPrice + raffle #  + voluntaryPrice
    uniqueRef = (person["uniqueRef"]+"A"+str(person["adultNos"])+"K"+str(person["kidsNos"])+"R"+str(person["raffle"]))
    #   +"V"+str(person["voluntaryPrice"]))
    # Create email content using Jinja2 template
    email_data = {
        "guestName": person["guestName"],
        "adultNos": person["adultNos"],
        "kidsNos": person["kidsNos"],
        "adultCost": adultCost,
        "kidsCost": kidsCost,
        "raffleCost": raffleCost,
        "adultPrice": adultsPrice,
        "voluntaryPrice": voluntaryPrice,
        "uniqueRef": uniqueRef,
        "rafflePrice": person["raffle"],
        "kidsPrice": kidsPrice,
        "totalPrice": totalPrice,
    }
    email_content = jinja_template.render(email_data)

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = email
    msg["To"] = person["email"]
    msg["Subject"] = subject

    # Attach the HTML content to the email
    msg.attach(MIMEText(email_content, "html"))

    # Print and send the email
    print(f"Sending email to {person['email']}:\n{email_content}\n\n")
    logFile.write(f"Sending email to {person['email']}:\n{email_content}\n\n")

    try:
        smtp_object.sendmail(email, person["email"], msg.as_string())
    except Exception as error:
        # handle the exception
        print("An exception occurred:", type(error).__name__, "–", error)
        errorFile.write(" Could not send email to emailID: " + person['email'])
        raise Exception(" Could not send email to emailID: " + person['email'])

# Close the server connection
smtp_object.quit()



