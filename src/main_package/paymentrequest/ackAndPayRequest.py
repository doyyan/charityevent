import os
import shutil
from _datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from jinja2 import Template

from src.main_package.emailer.emailClient import sendEmail, checkEmailIsValid
from src.main_package.fileops.fileops import checkFileOpen
from src.main_package.loggers.logger import createLogger


def sendAckAndPayRequest(templateName, processedXlsFile):
    currentDateTime = datetime.now()
    shutil.copy(processedXlsFile, '../mainExcelFiles/DanceBeatz2025ProcessedCopy'
                + currentDateTime.strftime("%Y%m%d%H%M%S")
                + '.xlsx')

    logFile, errorFile = createLogger()

    if checkFileOpen(processedXlsFile):
        logFile.write(" File already open " + processedXlsFile)
        raise Exception(" File already open " + processedXlsFile)

    form = pd.read_excel(processedXlsFile)
    adminEmail = os.environ.get('ADMIN_EMAIL')
    # "dancebeatzedinburgh@gmail.com"

    emailHeaderField = 'Email'
    guestNameField = 'Guest name'
    noOfAdultsField = 'Number of Adults (£12)'
    raffleField = "I'd like to win one of the Great prizes on offer for the Raffle, please can I buy the following Number of tickets (£2 each)"
    noOfKidsField = 'Number of Children aged 5 and above (£6)'
    acknowledgedField = 'Acknowledged'
    cancelledField = 'Cancelled'
    paymentRefField = 'PaymentRef'

    # Read the Jinja2 email template
    with open(templateName, "r") as file:
        template_str = file.read()
        jinja_template = Template(template_str)

    subject = "Dance Beatz Charity Dance Show 2025"
    adultCost = 12
    kidsCost = 6
    raffleCost = 2

    form.fillna(value="", axis=1, inplace=True)

    # Now we iterate over our data to generate and send custom emails to each
    for i, person in form.iterrows():
        # Only Process if a Payment Ref has NOT been emailed!
        if (person[paymentRefField] == "" and person[cancelledField] != 'Cancelled'):
            emailValid, mesg = checkEmailIsValid(person[emailHeaderField])
            if not emailValid:
                errorFile.write("email ID on Line" + str(i) + " is INVALID")
                continue
            kidsPrice = person[noOfKidsField] * kidsCost
            adultsPrice = person[noOfAdultsField] * adultCost
            # voluntaryPrice = person["voluntaryPrice"]
            raffle = person[raffleField] * raffleCost
            indexWithNameSlice = person[guestNameField].upper()[:2] + str(i)
            totalPrice = kidsPrice + adultsPrice + raffle  # + voluntaryPrice
            uniqueRef = (indexWithNameSlice + "A" + str(person[noOfAdultsField]) + "K" + str(
                person[noOfKidsField]) + "R" + str(
                person[raffleField]))
            #   +"V"+str(person["voluntaryPrice"]))
            # Create email content using Jinja2 template
            email_data = {
                "guestName": person[guestNameField],
                "adultNos": person[noOfAdultsField],
                "kidsNos": person[noOfKidsField],
                "adultCost": adultCost,
                "kidsCost": kidsCost,
                "raffleCost": raffleCost,
                "adultPrice": adultsPrice,
                # "voluntaryPrice": voluntaryPrice,
                "uniqueRef": uniqueRef,
                "rafflePrice": raffle,
                "kidsPrice": kidsPrice,
                "totalPrice": totalPrice,
            }
            email_content = jinja_template.render(email_data)

            # Create the email message
            msg = MIMEMultipart()
            msg["From"] = adminEmail
            msg["To"] = person[emailHeaderField]
            msg["Subject"] = subject

            # Attach the HTML content to the email
            msg.attach(MIMEText(email_content, "html"))

            # Print and send the email
            print(f"Sending email to {person[emailHeaderField]}:\n{email_content}\n\n")
            logFile.write(f"Sending email to {person[emailHeaderField]}:\n{email_content}\n\n")

            if person[acknowledgedField] == "":
                sendSuccess = sendEmail(msg.as_string(), person[emailHeaderField], adminEmail, errorFile)

            form.at[i, acknowledgedField] = currentDateTime
            form.at[i, paymentRefField] = uniqueRef

    with pd.ExcelWriter(processedXlsFile, engine="openpyxl",
                        mode="a", if_sheet_exists="replace") as writer:
        form.to_excel(excel_writer=writer, sheet_name='Form Responses 1', index=False)
