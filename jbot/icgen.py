import logging
import copy
import os
import camb
import numpy
import math
from .job import Job
from .job import GADGET_RESTART_CREATE_IC

DEFAULT_POWERSPEC_FILE='camb.txt'

class ICgen(Job):
    def _get_camb_pw(self,zlist,kmax=-1,nonlin=camb.model.NonLinear_none):
        kpc = 3.085678e21 # in cm
        Mpc = kpc*1000
        L = self._config.paramfile['UnitLength_in_cm']
        
        km_p_s = 1e5
        V = self._config.paramfile['UnitVelocity_in_cm_per_s']
        
        boxL = 2*self._config.paramfile['BoxSize']*L/Mpc # Mpc
        
        Ngrid = 2*self._config.ngenic['GridSize'] # gridsize 
        kmin = 2*math.pi/boxL
        if kmax<0.0:
            kmax = kmin * (Ngrid//2)
        npoints  = 200

        pars = camb.CAMBparams()
        
        # Plank 2018
        # pars.set_cosmology(H0=67.32117, ombh2=0.0223828, omch2=0.1201075)
        # pars.InitPower.set_params(As=2.097e-9,ns=0.965)
        
        h = self._config.paramfile['HubbleParam']
        h2 = h*h
        
        Omb = self._config.paramfile['OmegaBaryon']
        Om0 = self._config.paramfile['Omega0']
        Omc = Om0-Omb # cold dark matter
        Oml = self._config.paramfile['OmegaLambda']
        
        ombh2 = Omb*h2
        omch2 = Omc*h2
        
        Hubble = self._config.paramfile['Hubble']
        H0 = h * Hubble / (km_p_s/Mpc)
       
        pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=Omc*h2)
        
        logging.debug('generating power spectrum in box of L = %f Mpc, ombh2 = %f, omch2 = %f, H0 = %f' % (boxL,ombh2,omch2,H0))
            
        pars.InitPower.set_params(As=2.097e-9,ns=0.965)
        
        # what's the relation between sigma8 and the scalar spectral index ns?
        #
        # >>> print(Om0)
        # 0.3143996041505493
        # >>> print(Oml)
        # 0.6856003958494508
        # >>> print(Omb)
        # 0.04938682464547351
        # >>> om0h2
        # 0.14249030000000001

        #Note non-linear corrections couples to smaller scales than you want
        pars.set_matter_power(redshifts=zlist, kmax=kmax)

        #Linear spectra
        pars.NonLinear = nonlin
        results = camb.get_results(pars)
        kh, z, pk = results.get_matter_power_spectrum(
            minkh=kmin, maxkh=kmax, npoints = npoints)
        s8 = numpy.array(results.get_sigma8())
        # self._config.ngenic['Sigma8'] = s8
        return kh,z,pk
        
        #Non-Linear spectra (Halofit)
        # pars.NonLinear = camb.model.NonLinear_both
        # results.calc_power_spectra(pars)
        # kh_nonlin, z_nonlin, pk_nonlin = results.get_matter_power_spectrum(
        #     minkh=kmin, maxkh=kmax, npoints = npoints)
    
    def _get_delta(self,kh,pkl):
        dpk = []
        factpi = 1.0/(2*math.pi*math.pi)
        for pk in pkl:
            #Dk = [ 4*math.pi* k**3 * p for k,p in zip(kh,pk)  ]
            Dk = [ factpi * k**3 * p for k,p in zip(kh,pk)  ]
            dpk.append(Dk)
        return numpy.array(dpk)
    
    def _save_camb_to_file(self,fname,kh,pk):
        with open(fname,'w') as f:
            for k,p in zip(kh,pk):
                print(math.log10(k),math.log10(p),file=f)
    
    def __init__(self,default_config):
        super().__init__(default_config)
        logging.info('constructing ICgen type')
        self._config.prefix = os.path.join( self._config.prefix,'ic')
        self.gadget_instruction=GADGET_RESTART_CREATE_IC
    
    def _append_ngenic(self):
        with open(self.parameter_file,'a') as f:
            for k,v in self._config.ngenic.items():
                print(k,v,file=f)
    
    
    def _generate_powerspec(self):
        z0 = 1.0/self._config.paramfile['TimeBegin'] - 1.
        zlist = [z0]
        kh,z,pk = self._get_camb_pw(zlist)
        dpk = self._get_delta(kh,pk)
        for i in range(len(zlist)):
            self._save_camb_to_file( self.powerspec_file, kh,dpk[i,:])
        
    
    def commit(self):
        super()._write_all_config_files()
        
        self.powerspec_file = os.path.join(self.configuration_dir,DEFAULT_POWERSPEC_FILE)
        self.set_param("PowerSpectrumFile",self.powerspec_file)
        self._generate_powerspec()
        
        self._append_ngenic()
        
        super()._submit()
