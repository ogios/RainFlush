import datetime

def color(string, color):
    dic = {
        'white': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'purple': '\033[35m',
        'cyan': '\033[36m',
        'black': '\033[37m'
    }
    return dic[color]+string+'\033[0m'

def gettime():
    return str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))