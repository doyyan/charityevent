import os
import shutil
from _datetime import datetime

import pandas as pd

from src.main_package.banking.processpayments.bankTransactionProcessor import find_and_update_bank_transactions
from src.main_package.fileops.fileops import checkFileOpen
from src.main_package.loggers.logger import createLogger


def process_bank_statements(processedXlsFile):
    logFile, errorFile = createLogger()
    currentDateTime = datetime.now()
    shutil.copy(processedXlsFile, '../mainExcelFiles/DanceBeatz2025ProcessedCopy'
                + currentDateTime.strftime("%Y%m%d%H%M%S")
                + '.xlsx')

    bank_ref_data = pd.read_excel("BanksReference.xlsx")
    bank_ref_data.fillna(value="", axis=1, inplace=True)
    form = pd.read_excel(processedXlsFile)

    for _, _, filenames in os.walk("."):
        for filename in filenames:
            if filename.endswith(".xlsx"):
                if filename != "BanksReference.xlsx":
                    if checkFileOpen(filename):
                        logFile.write(" File already open " + filename)
                        raise Exception(" File already open " + filename)
                    bank_transactions = pd.read_excel(filename)
                    bank_transactions.fillna(value="", axis=1, inplace=True)
                    find_and_update_bank_transactions(processedXlsFile, bank_ref_data, bank_transactions, logFile,
                                                      errorFile)
