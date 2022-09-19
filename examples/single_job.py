import autojob

if __name__=="__main__":
    with open('default_config.json','r') as fd:
        
        # default parameters for my runs
        default_config = autojob.Config(fd)
        
        # let's set up a job for the initial conditions
        ic = autojob.ICgen(default_config)
        ic.compile=True
        ic.commit()
        
        # # let's set up a job starting from the initial conditions until z=0
        # my_job = autojob.Job(defaul_config)
        # # there will be 5 snapshot until the end
        # zstops = [ic.z0,10.,5.,2.,1.,0.5,0.2,0.]
        # my_job.set_zstops(zstops)
        # # path to the executable and configurations and output
        # my_job.exec_path = "job-exec"
        # my_job.config_path="job-config"
        # my_job.out_path="job-out"
        # my_job.compile=True
        # # set a dependency
        # my_job.depends(ic)
        # # get initial conditions from
        # my_job.initial_snapshot(ic.snapshots[-1])
