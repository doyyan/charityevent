import pandas as pd

from src.main_package.fileops.fileops import checkFileOpen


def find_and_update_bank_transactions(processedXlsFile, bank_ref_data, current_statement, logFile, errorFile):
    paymentRefField = 'PaymentRef'
    paidAmountField = 'PaidAmount'
    paidDateField = 'PaidDate'
    transactionPaymentReferenceField = 'TransactionReferenceColumn'
    transactionPaymentDateField = 'TransactionDateColumn'
    transactionPaymentAmountField = 'TransactionAmountColumn'

    form = pd.read_excel(processedXlsFile)
    if checkFileOpen(processedXlsFile):
        logFile.write(" File already open " + processedXlsFile)
        raise Exception(" File already open " + processedXlsFile)
    # read the bank reference data rows to scan the payment ref column names
    for i, bank_ref_data_row in bank_ref_data.iterrows():
        if bank_ref_data_row[transactionPaymentReferenceField] == "":
            continue
        len = 0
        try:
            current_data = current_statement[bank_ref_data_row[transactionPaymentReferenceField]]
        except KeyError as e:
            break;
        for i, form_rows in form.iterrows():
            rows_updated = 0
            for j, statment_row in current_statement.iterrows():
                if form_rows[paymentRefField] == statment_row[bank_ref_data_row[transactionPaymentReferenceField]]:
                    print(statment_row[bank_ref_data_row[transactionPaymentDateField]])
                    print(statment_row[bank_ref_data_row[transactionPaymentAmountField]])
                    statementPaymentDate = statment_row[bank_ref_data_row[transactionPaymentDateField]]
                    statementAmount = statment_row[bank_ref_data_row[transactionPaymentAmountField]]
                    form.at[i, paidAmountField] = statementAmount
                    form.at[i, paidDateField] = statementPaymentDate
                    rows_updated = rows_updated + 1
                    None

            if rows_updated > 0:
                with pd.ExcelWriter(processedXlsFile, engine="openpyxl",
                                    mode="a", if_sheet_exists="replace") as writer:
                    form.to_excel(excel_writer=writer, sheet_name='Form Responses 1', index=False)
