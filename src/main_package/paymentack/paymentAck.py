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
from src.main_package.utils.stringUtils import prependGBP


def sendPayAck(templateName, processedXlsFile):
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
    acknowledgedField = 'Acknowledged'
    cancelledField = 'Cancelled'
    paymentRefField = 'PaymentRef'
    paidAmountField = 'PaidAmount'
    paidDateField = 'PaidDate'
    paidAcknowledgedField = 'PaidAcknowledged'

    # Read the Jinja2 email template
    with open(templateName, "r") as file:
        template_str = file.read()
        jinja_template = Template(template_str)

    subject = "Dance Beatz Charity Dance Show 2025"
    form.fillna(value="", axis=1, inplace=True)

    emails_sent = 0

    try:
        # Now we iterate over our data to generate and send custom emails to each
        for i, person in form.iterrows():
            # Only Process if a Payment Ref has NOT been emailed!
            if (person[acknowledgedField] != "" and person[cancelledField] != 'Cancelled' and person[
                paidAmountField] != "" and person[paidDateField] != "" and person[paidAcknowledgedField] == ""):
                emailValid, mesg = checkEmailIsValid(person[emailHeaderField])
                if not emailValid:
                    errorFile.write("email ID on Line" + str(i) + " is INVALID")
                    continue

                formatted_payment = prependGBP(person[paidAmountField])
                formatted_date = datetime.date(person[paidDateField]).strftime("%d/%m/%Y")
                # Create email content using Jinja2 template
                email_data = {
                    "guestName": person[guestNameField],
                    "PaidAmount": formatted_payment,
                    "PaidDate": formatted_date,
                    "PaymentRef": person[paymentRefField],
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

                sendSuccess = sendEmail(msg.as_string(), person[emailHeaderField], adminEmail, errorFile)

                if (sendSuccess):
                    form.at[i, paidAcknowledgedField] = currentDateTime
                    emails_sent += 1
    except Exception as e:
        errorFile.write(str(e))

    if emails_sent > 0:
        with pd.ExcelWriter(processedXlsFile, engine="openpyxl",
                            mode="a", if_sheet_exists="replace") as writer:
            form.to_excel(excel_writer=writer, sheet_name='Form Responses 1', index=False)
