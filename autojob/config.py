import json
import logging

class Config():
    def __init__(self,fd):
        logging.info('reading config file %s' % fd.name)
        data = json.load(fd)
        for k,v in data.items():
            setattr(self,k,v)
