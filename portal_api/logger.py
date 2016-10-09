import logging

class Logger():
    def __init__(self,filename,debug=True,sid=None):
        if debug:
            self.level=logging.DEBUG
        else:
            self.level=logging.ERROR
        if not sid:
            logging.basicConfig(level=self.level,
                    format="%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    filename=filename,
                    filemode="a"
            )
        else:
            logging.basicConfig(level=self.level,
                    format="%(asctime)s %(filename)s[line:%(lineno)d][id:{sid}] %(levelname)s %(message)s".format(sid=sid),
                    datefmt="%Y-%m-%d %H:%M:%S",
                    filename=filename,
                    filemode="a"
            )
    def debug(self,message):
        logging.debug("%s" % message)
    def error(self,message):
        logging.error("%s" % message)


if __name__ == '__main__':
    log=Logger(debug=None,filename="zhanghao.txt")
    for i in range(10):
        log.debug("bebug %d" % i)
        log.error("bebug %d" % i)
