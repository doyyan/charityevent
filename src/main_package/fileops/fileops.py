from subprocess import check_output, Popen, PIPE


def checkFileOpen(filename):
    try:
        lsout = Popen(['lsof', filename], stdout=PIPE, shell=False)
        check_output(["grep", filename], stdin=lsout.stdout, shell=False)
        return True
    except:
        return False
