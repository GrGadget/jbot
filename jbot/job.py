import logging
import copy
import os
import subprocess
import numpy

DEFAULT_CONFIG_FNAME='Config.sh'
DEFAULT_PARAM_FNAME='param.txt'
DEFAULT_SNAPLIST_FNAME='snap-times.txt'
DEFAULT_SLURM_FNAME='job.sh'
DEFAULT_SLURM_OUTPUT='slurm.log'
DEFAULT_EXECUTABLE_FNAME=os.path.join('subprojects','Gadget4','Gadget4')

GADGET_RESTART_FROM_SNAPSHOT=2
GADGET_RESTART_CREATE_IC=6


class Job():
    def __init__(self,default_config):
        logging.info('constructing Job type')
        self._config = copy.deepcopy(default_config)
        self.compile=True
        self.gadget_instruction=GADGET_RESTART_FROM_SNAPSHOT
    
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
            print('OutputDir',self.output_dir,file=f)
            print('OutputListFilename',self.snaplist_file,file=f)
    
    def _write_snaplist(self):
        with open(self.snaplist_file,'w') as f:
            zlist = numpy.sort(self._config.output_redshift)[::-1]
            for z in zlist:
                print(1.0/(1+z),file=f)
    
    def _write_slurm_file(self):
        with open(self.slurm_file,'w') as f:
            print('#!/usr/bin/bash -l',file=f)
            
            print('## SBATCH OPTIONS',file=f)
            for k,v in self._config.slurm['parameters'].items():
                print('#SBATCH --',k,'=',v,file=f,sep='')
            print('#SBATCH --output=',self.slurm_output,file=f,sep='')
            print('',file=f)
            
            print('## MODULES',file=f)
            print('module load'," ".join(self._config.slurm['modules']),file=f)
            print('echo',file=f)
            print('module list',file=f)
            print('echo',file=f)
            print('',file=f)
            
            print('## COMPILE',file=f)
            print('echo',file=f)
            if self.compile:
                print('cd',self.build_dir,file=f)
                print('meson',
                      self._config.source_dir,
                      '-DGadget4:config_file=%s' % self.compile_config_file,
                      file=f)
                print('ninja',file=f)
            print('echo',file=f)
            print('',file=f)
            
            print('## RUN',file=f)
            print('cd',self._config.prefix,file=f)
            print('echo',file=f)
            print('echo "Running on hosts: $SLURM_NODELIST"',file=f)
            print('echo "Running on $SLURM_NNODES nodes"',file=f)
            print('echo "Running on $SLURM_NPROCS processors"',file=f)
            print('echo "Working directory is `pwd`"',file=f)
            print('echo',file=f)
            print('mpirun','-np','$SLURM_NPROCS',self.executable,self.parameter_file,self.gadget_instruction,file=f)
            print('',file=f)
    
    def set_param(self,name,value):
        self._config.paramfile[name]=value
    
    def _define_config_filenames(self):
        self.build_dir = os.path.join(self._config.prefix,self.build_path)
        self.executable = os.path.join(self.build_dir,DEFAULT_EXECUTABLE_FNAME)
        self.output_dir = os.path.join(self._config.prefix,self.out_path)
        self.configuration_dir = os.path.join(self._config.prefix,self.config_path)
        self.compile_config_file = os.path.join(self.configuration_dir,DEFAULT_CONFIG_FNAME)
        self.snaplist_file = os.path.join(self.configuration_dir,DEFAULT_SNAPLIST_FNAME)
        self.parameter_file = os.path.join(self.configuration_dir,DEFAULT_PARAM_FNAME)
        self.slurm_file=os.path.join(self.configuration_dir,DEFAULT_SLURM_FNAME)
        self.slurm_output=os.path.join(self.output_dir,DEFAULT_SLURM_OUTPUT)
   
    def _write_all_config_files(self):
        self._force_mkdir(self._config.prefix)
        self._force_mkdir(self.build_dir)
        self._force_mkdir(self.output_dir)
        self._force_mkdir(self.configuration_dir)
        
        self._write_compile_config()
        self._write_snaplist()
        self._write_paramfile()
        self._write_slurm_file()
        
    def set_snapshotz(self,zlist):
        self._config.output_redshift = zlist
        
    def _submit(self):        
        subprocess.run(['sbatch',self.slurm_file])
    
    def commit(self):
        self._define_config_filenames()
        self._write_all_config_files()
        self._submit()
