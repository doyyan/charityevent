import pandas as pd
from fuzzywuzzy import fuzz

from src.main_package.fileops.fileops import checkFileOpen


def hasPaidCorrectAmount(**kwargs):
    paid = kwargs['totalPaid']
    toPay = (kwargs['adults'] * kwargs['adultTicketPrice']) + (
            kwargs['kids'] * kwargs['kidsTicketPrice']) + (kwargs['raffle'] * kwargs['raffleTicketPrice'])
    if paid > toPay:
        return "OverPaid"
    elif paid < toPay:
        return "UnderPaid"
    else:
        return "CorrectlyPaid"


def find_and_update_bank_transactions(processedXlsFile, bank_ref_data, current_statement, logFile, errorFile):
    try:
        paymentRefField = 'PaymentRef'
        paidAmountField = 'PaidAmount'
        paidDateField = 'PaidDate'
        transactionPaymentReferenceField = 'TransactionReferenceColumn'
        transactionPaymentDateField = 'TransactionDateColumn'
        transactionPaymentAmountField = 'TransactionAmountColumn'
        fuzzyMatchField = 'FuzzyMatchRatio'
        adultTicketPriceField = 'AdultTicketPrice'
        kidsTicketPriceField = 'KidsTicketPrice'
        raffleTicketPriceField = 'RafflePrice'
        rafflePriceField = "I'd like to win one of the Great prizes on offer for the Raffle, please can I buy the following Number of tickets (£2 each)"
        noOfAdultsField = 'Number of Adults (£12)'
        noOfKidsField = 'Number of Children aged 5 and above (£6)'
        paymentMismatchField = 'PaymentMismatch'
        totalPaidField = 'TotalPaid'
        paidAcknowledgedField = 'PaidAcknowledged'
        closestMatchField = 'ClosestMatch'
        closestMatchRatioField = 'ClosestMatchRatio'

        fuzzyMatchWanted = bank_ref_data[fuzzyMatchField][0]
        kidsTicketPrice = bank_ref_data[kidsTicketPriceField][0]
        adultTicketPrice = bank_ref_data[adultTicketPriceField][0]
        rafflePrice = bank_ref_data[raffleTicketPriceField][0]

        googleForm = pd.read_excel(processedXlsFile)
        googleForm[totalPaidField].fillna(0)

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
            for i, form_rows in googleForm.iterrows():
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
                                raffle=form_rows[rafflePriceField],
                                raffleTicketPrice=rafflePrice,
                            )
                            googleForm.at[i, paidAmountField] = statementAmount
                            googleForm.at[i, paidDateField] = statementPaymentDate
                            googleForm.at[i, paymentMismatchField] = paidCorrectly
                            googleForm.at[i, totalPaidField] = totalPaidSoFar
                            googleForm.at[i, closestMatchRatioField] = fuzzyMatchRatio
                            googleForm.at[i, closestMatchField] = statment_row[
                                bank_ref_data_row[transactionPaymentReferenceField]]
                            googleForm.at[i, paidAcknowledgedField] = float("nan")
                            rows_updated = rows_updated + 1
                            # break
                        else:
                            closestMatch = form_rows[closestMatchField]
                            closestMatchRatioValue = form_rows[closestMatchRatioField]
                            if closestMatch == "" or pd.isna(closestMatch) or (
                                    closestMatch != "" and fuzzyMatchRatio >= closestMatchRatioValue):
                                googleForm.at[i, closestMatchRatioField] = fuzzyMatchRatio
                                googleForm.at[i, closestMatchField] = statment_row[
                                    bank_ref_data_row[transactionPaymentReferenceField]]
                                rows_updated = rows_updated + 1

        if rows_updated > 0:
            with pd.ExcelWriter(processedXlsFile, engine="openpyxl",
                                mode="a", if_sheet_exists="replace") as writer:
                googleForm.to_excel(excel_writer=writer, sheet_name='Form Responses 1', index=False)
    except Exception as e:
        print(e)
        errorFile.write(str(e))
