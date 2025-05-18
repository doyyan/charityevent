from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Template

from src.main_package.emailer.emailClient import sendEmail
from src.main_package.loggers.logger import createLogger


def sendAckAndPayRequest(people_data, templateName):
    logFile, errorFile = createLogger()

    adminEmail = "ravi.sivaraj@gmail.com"

    # Read the Jinja2 email template
    with open(templateName, "r") as file:
        template_str = file.read()
        jinja_template = Template(template_str)

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
        totalPrice = kidsPrice + adultsPrice + raffle  # + voluntaryPrice
        uniqueRef = (person["uniqueRef"] + "A" + str(person["adultNos"]) + "K" + str(person["kidsNos"]) + "R" + str(
            person["raffle"]))
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
        msg["From"] = adminEmail
        msg["To"] = person["email"]
        msg["Subject"] = subject

        # Attach the HTML content to the email
        msg.attach(MIMEText(email_content, "html"))

        # Print and send the email
        print(f"Sending email to {person['email']}:\n{email_content}\n\n")
        logFile.write(f"Sending email to {person['email']}:\n{email_content}\n\n")

        sendEmail(msg.as_string(), person['email'], adminEmail, errorFile)
