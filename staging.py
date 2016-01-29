#######################################
# staging.py
# Erica Lastufka 08/20/2015 

#Description: Prepares data for visitors in their lustre area
#######################################

#######################################
# Usage:
#	import staging
#       staging.staging('2013.1.00229.S', 'cv-8708')
#######################################

#########################################

import os
import glob
import sys
import subprocess
import get_asdmuid as gasdm
import mypre_imaging as mpre
import project_info
import IPython
import multiprocessing #need to make each instance of the loop go at the same time else it'll take forever!!
import time

def staging_info(project_number, user_name, test=False):
    if test ==False:
        project_path = '/lustre/naasc/observers/' + user_name + '/'
    else:
        project_path='/lustre/naasc/users/elastufk/test/'
    os.chdir('/lustre/naasc/sciops/cycle2_release/') #assume cycle 2 ....
    tarlist = glob.glob('*%s*.tar' % project_number)
    if tarlist == []:
        os.chdir('/lustre/naasc/sciops/cycle1_release/') 
        tarlist = glob.glob('*%s*.tar' % project_number)
    if tarlist == []:
        os.chdir('/lustre/naasc/sciops/cycle3_release/') #assume cycle 2 ....
        tarlist = glob.glob('*%s*.tar' % project_number)
    if tarlist == []:
        sys.exit('ERROR: No tar files found for project %s' % project_number)
    return project_path, project_number, tarlist
    
def stage_data(mous):
        os.chdir('%s/' % mous)
        original_mous=mous[12:-3]
        casa_version = project_info.casa_version()
        asdm_uids = gasdm.main(original_mous)
        project_dict = {'project_type': 'Imaging', 'asdm': asdm_uids, 'casa_version': casa_version}
        mpre.downloadASDM(project_dict)  # run asdm export light on the asdms
        mpre.runPipeline(project_dict)
        return project_dict

def start_process():
    multiprocessing.current_process().name 

def staging(project_number, user_name, test=False):
    start_time=time.time()
    sinfo = staging_info(project_number, user_name, test=test)
    os.chdir('%s' % sinfo[0])
    tarlist = sinfo[2]
    
    #untar stuff
    os.chdir('data')  
    for tarball in tarlist:
        if os.path.isfile('/lustre/naasc/sciops/cycle2_release/%s' % tarball) == True:
            os.system('cp /lustre/naasc/sciops/cycle2_release/%s %sdata/' % (tarball, sinfo[0])) 
            #print tarball
        elif os.path.isfile('/lustre/naasc/sciops/cycle1_release/%s' % tarball) == True:
            os.system('cp /lustre/naasc/sciops/cycle1_release/%s %sdata/' % (tarball, sinfo[0])) 
            #print tarball
        elif os.path.isfile('/lustre/naasc/sciops/cycle3_release/%s' % tarball) == True:
            os.system('cp /lustre/naasc/sciops/cycle3_release/%s %sdata/' % (tarball, sinfo[0]))
            #print tarball 
        else:
            sys.exit('ERROR: %s not found in cycleN_release folders!')
        os.system('tar -xf %s' % tarball) #who needs verbose?
    
    # change into directories, source pipeline, run scriptForPI
    project_path = sinfo[0] + 'data/' + sinfo[1] + '/sg_ouss_id/group_ouss_id/'
    os.chdir(project_path)
    mous_glob = glob.glob('member_ouss_uid*')

    pool_size = multiprocessing.cpu_count() * 4
    pool = multiprocessing.Pool(processes=pool_size, initializer=start_process,)
    pool_outputs= pool.map(stage_data, mous_glob)
    print pool_outputs
    print("--- %s seconds ---" % (time.time() - start_time))
    os.chdir(sinfo[0])
    os.system('sudo chown -R %s: data*' % user_name)
    os.system('sudo chgrp -R naascssg data*' )
    os.system('sudo chmod 770 -R data*')
