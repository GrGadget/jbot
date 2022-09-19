import logging
import copy
import os
from .job import Job

class ICgen(Job):
    def __init__(self,default_config):
        super().__init__(default_config)
        super()._config.prefix = os.path.join( super()._config.prefix,'ic')