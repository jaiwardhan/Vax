import json
from modules.DateGenerator import DateGenerator

class Logger:

    path="logs.txt"

    @staticmethod
    def configure(path):
        Logger.path = path
    
    @staticmethod
    def log(msg):
        if msg is None:
            return
        elif type(msg) is str:
            if len(msg) == 0:
                return
        elif type(msg) is dict or type(msg) is list:
            if len(msg) == 0:
                return
            else:
                msg = json.dumps(msg)
        else:
            msg = str(msg)

        with open(Logger.path, "a+") as f:
            f.write(DateGenerator.get_ts() + " -- " + msg + "\n")
