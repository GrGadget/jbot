import logging
import copy
import os
from .job import Job
from .job import GADGET_RESTART_CREATE_IC

class ICgen(Job):
    def __init__(self,default_config):
        super().__init__(default_config)
        logging.info('constructing ICgen type')
        self._config.prefix = os.path.join( self._config.prefix,'ic')
        self.gadget_instruction=GADGET_RESTART_CREATE_IC
    
    def _append_ngenic(self):
        with open(self.parameter_file,'a') as f:
            for k,v in self._config.ngenic.items():
                print(k,v,file=f)
    
    def commit(self):
        super()._write_all_config_files()
        self._append_ngenic()
        super()._submit()
