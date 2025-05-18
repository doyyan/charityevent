from datetime import datetime

def createLogger():
    try:
        name = datetime.now().strftime("%Y%m%d%H%M%S")
        logFile = open(name + ".log", 'a+')
        errorFile = open(name + ".err", 'a+')
        return logFile, errorFile
    finally:
        print(' Files opened successfully')