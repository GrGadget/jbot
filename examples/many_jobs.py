#import autojob
import numpy

def z_split(z1,z2,N):
    # this is just an example for a z split, 
    # in a real simulation I guess we should split z-stops such 
    # that the scale factor delta is evenly distributed
    # or physical time delta.
    return numpy.linspace(z1,z2,N+1)[1:]

if __name__=="__main__":
    with open('defaul_config.json','r') as fd:
        
        # default parameters for my runs
        default_config = autojob.config(fd)
        
        # let's set up a job for the initial conditions
        ic = autojob.InitialConditions(default_config)
        ic.exec_path = "ic-exec"
        ic.config_path="ic-config"
        ic.out_path="ic-out"
        ic.compile=True
        
        # let's set up a job starting from the initial conditions until z=0
        job0 = autojob.Job(defaul_config)
        # there will be 5 snapshot until the end
        zstops = z_split(ic.z0,0,5)
        job0.set_zstops(zstops)
        # path to the executable and configurations and output
        job0.exec_path = "job0-exec"
        job0.config_path="job0-config"
        job0.out_path="job0-out"
        job0.compile=True
        # set a dependency
        job0.depends(ic)
        # get initial conditions from
        job0.initial_snapshot(ic.snapshots[-1])
        
        # a run that starts at z0 non-stop until z=0
        job1 = autojob.Job(defaul_config)
        job1.set_zstops([0])
        # path to the executable and configurations and output
        job1.exec_path = "job0-exec"
        job1.config_path="job1-config"
        job1.out_path="job1-out"
        job1.compile=False
        # set a dependency
        job1.depends(job0)
        # get initial conditions from
        job1.initial_snapshot(ic.snapshots[-1])
        
        # let's set some more jobs starting from job0 snapshots
        njoblist=[job0,job1]
        for i in range(len(zstops)-2):
            i_job = autojob.Job(defaul_config)
            
            i_job.set_zstops([0])
            # path to the executable and configurations and output
            i_job.exec_path = "job0-exec"
            i_job.config_path= ("job%d-config" % (i+2))
            i_job.out_path= ("job%d-out" % (i+2))
            i_job.compile=False
            # set a dependency
            i_job.depends(njoblist[-1])
            # get initial conditions from
            job1.initial_snapshot(job0.snapshots[i])
            
            njoblist.append(i_job)
            
