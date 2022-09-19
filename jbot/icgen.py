import logging
import copy
import os
from .job import Job

class ICgen(Job):
    def __init__(self,default_config):
        super().__init__(default_config)
        logging.info('constructing ICgen type')
        self._config.prefix = os.path.join( self._config.prefix,'ic')
