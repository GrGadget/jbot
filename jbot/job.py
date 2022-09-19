import logging
import copy
import os
import subprocess

DEFAULT_CONFIG_FNAME='Config.sh'
DEFAULT_PARAM_FNAME='param.txt'
DEFAULT_SLURM_FNAME='job.sh'


class Job():
    def __init__(self,default_config):
        logging.info('constructing Job type')
        self._config = copy.deepcopy(default_config)
        self.build_path = "build"
        self.config_path = "configuration"
        self.out_path="output"
        self.compile=True
    
    def _force_mkdir(self,path):
        try:
            os.mkdir(path)
        except FileExistsError as e:
            pass 
        except Exception as e:
            raise e

    def _write_compile_config(self):
        with open(self.compile_config_file,'w') as f:
            for k,v in self._config.compiler_options['options'].items():
                if v==True:
                    print(k,file=f)
            for k,v in self._config.compiler_options['parameters'].items():
                print(k,"=",v,file=f,sep='')
    
    def _write_paramfile(self):
        with open(self.parameter_file,'w') as f:
            for k,v in self._config.paramfile.items():
                print(k,v,file=f)
    
    def _write_slurm_file(self):
        with open(self.slurm_file,'w') as f:
            print('#!/usr/bin/bash -l',file=f)
            for k,v in self._config.slurm['parameters'].items():
                print('#SBATCH --',k,'=',v,file=f,sep='')
            
            print('module load'," ".join(self._config.slurm['modules']),file=f)
            if self.compile:
                print('cd',self.build_dir,file=f)
                print('meson',
                      self._config.source_dir,
                      '-DGadget4:config_file=%s' % self.compile_config_file,
                      file=f)
                print('ninja',file=f)
            print('cd',self._config.prefix,file=f)
                
    def commit(self):
        self._force_mkdir(self._config.prefix)
        
        self.build_dir = os.path.join(self._config.prefix,self.build_path)
        self._force_mkdir(self.build_dir)
        
        self.output_dir = os.path.join(self._config.prefix,self.out_path)
        self._force_mkdir(self.output_dir)
        
        self.configuration_dir = os.path.join(self._config.prefix,self.config_path)
        self._force_mkdir(self.configuration_dir)
        
        self.compile_config_file = os.path.join(self.configuration_dir,DEFAULT_CONFIG_FNAME)
        self._write_compile_config()
        
        self.parameter_file = os.path.join(self.configuration_dir,DEFAULT_PARAM_FNAME)
        self._write_paramfile()
        
        self.slurm_file=os.path.join(self.configuration_dir,DEFAULT_SLURM_FNAME)
        self._write_slurm_file()
        
        subprocess.run(['bash',self.slurm_file])
