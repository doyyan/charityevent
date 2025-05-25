import pandas as pd
from fuzzywuzzy import fuzz

from src.main_package.fileops.fileops import checkFileOpen


def hasPaidCorrectAmount(**kwargs):
    paid = kwargs['totalPaid']
    toPay = (kwargs['adults'] * kwargs['adultTicketPrice']) + (
            kwargs['kids'] * kwargs['kidsTicketPrice'])
    if paid > toPay:
        return "OverPaid"
    elif paid < toPay:
        return "UnderPaid"
    else:
        return "CorrectlyPaid"


def find_and_update_bank_transactions(processedXlsFile, bank_ref_data, current_statement, logFile, errorFile):
    paymentRefField = 'PaymentRef'
    paidAmountField = 'PaidAmount'
    paidDateField = 'PaidDate'
    transactionPaymentReferenceField = 'TransactionReferenceColumn'
    transactionPaymentDateField = 'TransactionDateColumn'
    transactionPaymentAmountField = 'TransactionAmountColumn'
    fuzzyMatchField = 'FuzzyMatchRatio'
    adultTicketPriceField = 'AdultTicketPrice'
    kidsTicketPriceField = 'KidsTicketPrice'
    noOfAdultsField = 'Number of Adults (£12)'
    noOfKidsField = 'Number of Children aged 5 and above (£6)'
    paymentMismatchField = 'PaymentMismatch'
    totalPaidField = 'TotalPaid'

    fuzzyMatchWanted = bank_ref_data[fuzzyMatchField][0]
    kidsTicketPrice = bank_ref_data[kidsTicketPriceField][0]
    adultTicketPrice = bank_ref_data[adultTicketPriceField][0]

    form = pd.read_excel(processedXlsFile)
    form[totalPaidField].fillna(0)

    if checkFileOpen(processedXlsFile):
        logFile.write(" File already open " + processedXlsFile)
        raise Exception(" File already open " + processedXlsFile)

    rows_updated = 0
    # read the bank reference data rows to scan the payment ref column names
    for i, bank_ref_data_row in bank_ref_data.iterrows():
        if bank_ref_data_row[transactionPaymentReferenceField] == "":
            continue
        try:
            current_data = current_statement[bank_ref_data_row[transactionPaymentReferenceField]]
        except KeyError as e:
            break;
        for i, form_rows in form.iterrows():
            for j, statment_row in current_statement.iterrows():
                form_row_value = str(form_rows[paymentRefField]).lower()
                statement_row_value = str(statment_row[bank_ref_data_row[transactionPaymentReferenceField]]).lower()
                if fuzzyMatchWanted != "":
                    fuzzyMatchRatio = fuzz.ratio(form_row_value, statement_row_value)
                    if fuzzyMatchRatio >= fuzzyMatchWanted:
                        totalPaidSoFar = 0
                        statementPaymentDate = statment_row[bank_ref_data_row[transactionPaymentDateField]]
                        statementAmount = statment_row[bank_ref_data_row[transactionPaymentAmountField]]
                        if form_rows[paidDateField] != "" and form_rows[paidDateField] != statementPaymentDate:
                            totalPaidSoFar = form_rows[totalPaidField] + statementAmount
                        else:
                            totalPaidSoFar = statementAmount
                        paidCorrectly = hasPaidCorrectAmount(
                            totalPaid=totalPaidSoFar,
                            adults=form_rows[noOfAdultsField],
                            adultTicketPrice=adultTicketPrice,
                            kids=form_rows[noOfKidsField],
                            kidsTicketPrice=kidsTicketPrice,
                        )
                        form.at[i, paidAmountField] = statementAmount
                        form.at[i, paidDateField] = statementPaymentDate
                        form.at[i, paymentMismatchField] = paidCorrectly
                        form.at[i, totalPaidField] = totalPaidSoFar
                        rows_updated = rows_updated + 1

    if rows_updated > 0:
        with pd.ExcelWriter(processedXlsFile, engine="openpyxl",
                            mode="a", if_sheet_exists="replace") as writer:
            form.to_excel(excel_writer=writer, sheet_name='Form Responses 1', index=False)
