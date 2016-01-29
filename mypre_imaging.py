"""#######################################
# mypre_imaging.py
# Erica Lastufka 08/20/2015 

#Description: This is a coded version of the directions in https://safe.nrao.edu/wiki/bin/view/ALMA/NAASC/Cycle2ImagingWorkflow and also the setup instructions in https://safe.nrao.edu/wiki/bin/view/ALMA/Cycle2DataReduction

#######################################
# Usage:
#	execfile("mypre_imaging.py") 

#   The user will have to enter: 
#       Project type (Imaging/Manual)
#       lustre username or directory to create Reduce_XXXX directory in (ex. elastufk or /lustre/naasc/elastufk/Imaging)
#       Paragraph form the SCOPS ticket describing project 
#	ex:
#	Project: 2013.1.00099.S
#	GOUS: uid://A001/X122/X45
#	MOUS: uid://A001/X122/X46
#	SBName: NGC253_a_06_TE
#	SBuid: uid://A001/X122/X33
#	ASDMs: uid://A002/X98124f/X478d
#
# 	location and name of the OT file (ex. /lustre/naasc/elastufk/2013.1.00099.S_v2.aot)
#########################################
"""
import os
import urllib2
import subprocess
import glob
import re #to do regular expression searches on the pipeline scripts
import fileinput #to edit the pipeline scripts in place 
import project_info as pi
import fill_README
import OT_info
import list_imparameters as li
import script_generator as sg
import IPython
import sys

#moving to my directory, unpacking the tar-ball, renaming the extracted files, and removing the tarball
def untarStuff(project_dict):
    """Copies tarball from pipetemp, moves it to the working directory and untars the files. Only used for imaging."""
    tarball = project_dict['tarball']
    project_path = project_dict['project_path']
    os.chdir('/lustre/naasc/sciops/pipetemp')

    if os.path.isfile(tarball) == True:
        os.system('cp /lustre/naasc/sciops/pipetemp/%s %s' % (tarball, project_path))
        os.chdir('%s' % project_path)    
        os.system('tar -xvzf %s' % tarball)
        alias = tarball[0:-4]
        os.system('mv %s/sg_ouss_id %s/sg_ouss_id' % (alias, project_path))
        os.system('rm -rf %s' % alias)
        os.system('rm %s' % tarball)
        os.chdir('%s/sg_ouss_id/group_ouss_id/member_ouss_id/' % project_path)
    else: 
        sys.exit('The file %s is not in pipetemp, or failed to copy over properly' % tarball) 

def oldpipelineChanges():
    """Old version of pipelineChanges() that doesn't check for the existing lines first, resulting in duplications."""
    os.chdir('script')

    mods = open('casa_restore_modification.txt', 'w')
    mods.truncate()
    n=0

    if 'fixplanets' or 'fixsyscaltimes' and '# SACM/JAO - Fixes' in open('casa_pipescript.py').read():             
	pipescript = open('casa_pipescript.py', 'r')
	for line in pipescript:
		if re.match('(.*)hifa_import(.*)', line) and n==0: #this n=0 is a dirty work-around for the hifa_importdata command showing up twice
			hifa_import = line
			#the fix taking place is adding the additional path info			
			hifa_import = hifa_import.replace('uid', '../rawdata/uid')
			mods.write(hifa_import)
			n=n+1
		#getting the other "fix" lines we'll need to add to the piperestorescript
		if re.match('    fixsyscaltimes(.*)', line):
			fixsyscaltimes = line
			mods.write(fixsyscaltimes)
		if re.match('    fixplanets(.*)', line):
			fixplanets = line
			mods.write(fixplanets)

    mods.write('    h_save() # SACM/JAO - Finish weblog after fixes\n    h_init() # SACM/JAO - Restart weblog after fixes')
    mods.close()

#writing the modifications to casa_piperestorescript.py

    for line in fileinput.input('casa_piperestorescript.py', inplace=1):
	print line,
	#finding the place I want to input the new commands
	if line.startswith('__rethrow_casa_exceptions = True'):
		print 'from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes'
	if line.startswith('try:'):
		for line in open('casa_restore_modification.txt'):
			#printing the new commands into the script
			print line
    os.chdir('../') 

def pipelineChanges():
    """Writing modifications to casapiperestorescript if planets were used as calibration sources. Only used for imaging."""
    os.chdir('script')
    #just in case ... will add a line in the cleanup bash script to get rid of these:
    os.system('cp casa_piperestorescript.py casa_piperestorescript.py.original')
    os.system('cp casa_pipescript.py casa_pipescript.py.original')
    n=0
    if 'fixplanets' or 'fixsyscaltimes' and '# SACM/JAO - Fixes' in open('casa_pipescript.py').read():             
	    pipescript = open('casa_pipescript.py', 'r')
            fixsyscaltimes = []
            fixplanets = []
	    for line in pipescript:
		    if (re.match('(.*)hifa_import(.*)', line) and n == 0): # because sometimes hifa_import shows up twice
			hifa_import = line
			#the fix taking place is adding the additional path info			
			hifa_import = hifa_import.replace('uid', '../rawdata/uid')
                        n = n + 1
		#getting the other "fix" lines we'll need to add to the piperestorescript
		    if re.match('    fixsyscaltimes(.*)', line):
			fixsyscaltimes.append(line)
		    if re.match('    fixplanets(.*)', line):
			fixplanets.append(line)
            pipescript.close()

    #writing the modifications to casa_piperestorescript.py 
    #First see if everything is in order. If so, do nothing....
    piperestorescript = open('casa_piperestorescript.py', 'r+')
    lines = piperestorescript.readlines()
    fixes = []
    try:
        if hifa_import not in lines:
            fixes.append(hifa_import)
    except UnboundLocalError:
        pass
    if fixsyscaltimes != []:
        fixsyscaltimes = map(str,fixsyscaltimes)
        if lines[0] != 'from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes\n': # add this if you need to fixsyscal times later on...
            lines[0] = 'from recipes.almahelpers import fixsyscaltimes # SACM/JAO - Fixes\n' + lines[0]
        if fixsyscaltimes not in lines:
            fixes.append(fixsyscaltimes)
                    
    if fixplanets != []:
        fixplanets = map(str,fixplanets)
        if fixplanets not in lines:
            fixes.append(fixplanets)

    if fixes != []:
        for n in range(0, len(lines)):
            if lines[n].startswith('try:'):
                for fix in fixes:
                    if 'hifa_importdata' not in fix:
                        lines[n+1] = lines[n+1] + ''.join(fix)
                    else:
                        lines[n+1] = fix
                break

    piperestorescript.seek(0)
    piperestorescript.writelines(lines)
    piperestorescript.close()
    os.chdir('../') 

def makeDirectories(project_dict): 
    """Makes Reduce_XXXX directory (Imaging and Manual) and directory tree (Manual)"""
    if os.path.isdir('%s' % project_dict['project_path']) == False:
         os.system('mkdir %s' % project_dict['project_path'])
    if project_dict['project_type'] == 'Manual':
       manual_path = project_dict['project_path']
       lustre = manual_path[0:manual_path.rfind('/')]
       os.chdir(lustre)
       if os.path.isdir('%s' % manual_path[manual_path.rfind('/')+1:]) == False:
           os.system('mkdir %s' % manual_path[manual_path.rfind('/')+1:])
       os.chdir('%s' % manual_path[manual_path.rfind('/')+1:])
       for asdmn in project_dict['asdm']:
           os.system('mkdir Calibration_%s' % str(asdmn[asdmn.rfind('X'):])) #make it go from the X to the end
       os.system('mkdir Imaging')
       os.system('mkdir Combination')
       os.chdir('Combination')
       os.system('mkdir calibrated')
       os.chdir('../../')

#Downloading the ASDMs and renaming them
def downloadASDM(project_dict, lbc=False):
    """Downloads the ASDMs associated with the SB by running ASDMExportLight. Changes the names of the asdms (Imaging) and generates the manual reduction script (Manual)"""
    project_type = project_dict['project_type']
    asdm = project_dict['asdm']
    #asdm = asdm[1:] #EL not permanent
    if project_type == 'Imaging':
        if os.path.isdir('raw') == False:
            os.system('mkdir raw')
        os.chdir('raw')
        for current_asdm in asdm: #range(0,asdm_num)
	    subprocess.call(['source /lustre/naasc/sciops/pipeline/pipeline_env.asdmExportLight.sh && asdmExportLight %s' % current_asdm], shell=True)
	    #changing the names of the usdm to match when it was changed by asdmExport
	    new_asdm = current_asdm.replace('/','_').replace(':','_')
	    os.system('mv %r %r.asdm.sdm' % (new_asdm, new_asdm))
        os.chdir('../')
    else:
        script_name=[]
        for current_asdm in asdm:
            #IPython.embed()
	    os.chdir('Calibration_%s' % str(current_asdm[current_asdm.rfind('X'):]).strip())
	    subprocess.call(['source /lustre/naasc/sciops/pipeline/pipeline_env.asdmExportLight.sh && asdmExportLight %s' % current_asdm], shell=True)
	    #changing the names of the asdm to match when it was changed by asdmExport
	    new_asdm = current_asdm.replace('/','_').replace(':','_')
            #IPython.embed()
            print "Generating script... if this crashes, specify a reference antenna eg. es.generateReducScript(new_asdm, refant='CM06')"
            if lbc ==True:
                subprocess.call(["casa", "-c", "es.generateReducScript(\'%s\', lbc=True)" % new_asdm])
            else:
                subprocess.call(["casa", "-c", "es.generateReducScript(\'%s\')" % new_asdm])
            #script_name.append(new_asdm + '.scriptForCalibration.py')
            #es.generateReducScript(new_asdm, refant='CM06')
                os.chdir('../')
        return script_name


#Copying the *_flagtemplate.txt files from calibration directory to /lustre/naasc/PipelineTestData/flagfiles 
#Add template filename, project code, MOUS, and SB name to /lustre/naasc/PipelineTestData/flagfiles/listflagfiles.txt

def copyFiles(project_dict):
    """Copies the *_flagtemplate.txt files from calibration directory to /lustre/naasc/PipelineTestData/flagfiles, and add template filename, project code, MOUS, and SB name to /lustre/naasc/PipelineTestData/flagfiles/listflagfiles.txt"""
    project_number = project_dict['project_number']
    mous_code = project_dict['mous_code']
    SB_name = project_dict['SB_name']

    os.chdir('calibration')
    os.system('cp *_flagtemplate.txt /lustre/naasc/sciops/PipelineTestData/flagfiles')
    flag_templates = glob.glob('*_flagtemplate.txt')
    flag_file = open('/lustre/naasc/sciops/PipelineTestData/flagfiles/listflagfiles.txt', 'a')
    for i in flag_templates:
	string = '%s\t%s\t%s\t%s\n' % (i, project_number, mous_code, SB_name)
	flag_file.write(string)
    flag_file.close()
    os.chdir('../')

def testcopyFiles(project_dict):
    """A test version of copyFiles that doesn't actually copy or write the files. Use when testing to avoid filling up the flagfiles and listflagfiles.txt unneccesarily"""
    project_number = project_dict['project_number']
    mous_code = project_dict['mous_code']
    SB_name = project_dict['SB_name']

    os.chdir('calibration')
    #os.system('cp *_flagtemplate.txt /lustre/naasc/PipelineTestData/flagfiles')
    flag_templates = glob.glob('*_flagtemplate.txt')
    #flag_file = open('/lustre/naasc/PipelineTestData/flagfiles/listflagfiles.txt', 'a')
    for i in flag_templates:
	string = '%s\t%s\t%s\t%s\n' % (i, project_number, mous_code, SB_name)
	#flag_file.write(string)
    #flag_file.close()
    os.chdir('../')

#Moving to the script directory and running the pipeline - figure out the pipeline version first: 

def runPipeline(project_dict): 
    """Sources the specified pipeline version and runs scriptForPI. Only used for imaging."""
    if project_dict['casa_version'] == '':
        version = pi.casa_version()
    else:
        version = project_dict['casa_version']
    if version == '4.2.2':
        #pipeline_path = '/lustre/naasc/sciops/pipeline/pipeline_env_r31667_casa422_30986.sh'
        pipeline_path = '/home/casa/packages/RHEL6/release/casapy-42.2.30986-pipe-1-64b/casapy --pipeline'
    elif version == '4.3.1':
        #pipeline_path =  '/lustre/naasc/sciops/pipeline/pipeline_env_r34044_casa431_r32491.sh'
        pipeline_path = '/home/casa/packages/RHEL6/release/casa-release-4.3.1-pipe-el6/casapy --pipeline'
        #pipeline_path = 'casa -r 4.3.1-pipe-el6 '
    else:
        version == '4.5.0'
        #pipeline_path = 'casa -r 4.5.0' #no pipeline yet but need to run in 4.5 else error
        pipeline_path = '/home/casa/packages/RHEL6/release/casa-release-4.5.0-el6/casapy'
    os.chdir('script')
    subprocess.call(['%s -c scriptForPI.py' % pipeline_path], shell=True, executable='/bin/bash')
    os.chdir('../')

#Untar the weblog reports from the /qa directory
def untarWeblog():
    """Untars the weblog reports from the /qa directory. Only used for imaging."""
    os.chdir('qa/')
    weblog = glob.glob('*.weblog.tar.gz')
    if os.path.isfile(weblog[0]):
        os.system('tar -xvzf %s' % weblog[0])
    elif os.path.isfile('weblog.tar.gz'):
        os.system('tar -xvzf weblog.tar.gz')   
    os.chdir('../')

#Moving into /calibrated and downloading the latest version of the imaging script template
def getScript(project_dict):
    """Downloads the imaging script template. No longer called in main() because the script generator is used."""
    project_type = project_dict['project_type']
    os.chdir(project_dict['project_path'])
    if project_type == 'Imaging':
        os.chdir('%s/sg_ouss_id/group_ouss_id/member_ouss_id/calibrated/' % project_dict['project_path'])
    else:
        os.chdir('%s/Imaging' % project_dict['project_path'] ) # should already be in 'Imaging' if it's manual...
    response = urllib2.urlopen('https://raw.githubusercontent.com/aakepley/ALMAImagingScript/master/scriptForImaging_template.py')
    html = response.read()
    template = open('scriptForImaging.py', 'w').write(html)
    #template.close() #this throws an error for some reason?
    os.chdir('../')

#Calling Erica's code that will pre-fill the README for me
def fillReadme(project_dict, AOT=False):
    """Fills out the header information in the README"""
    #print AOT, project_dict['SB_name']
    AOT_dict = OT_info.getOTinfo(project_dict['SB_name'],AOTpath=AOT)
    AOTdir = AOT_dict[0]
    readme_info = fill_README.getInfo(project_dict,AOT_dict)
    fill_README.write2Readme(project_dict['project_type'], project_dict['project_path'], readme_info, project_dict['casa_version']) # why won't this write??
    #fill_README.testwrite()
    #fill_README.cleanup(AOTdir['AOT'])
    return AOT_dict

def generate_script(project_dict, OT_dict, comments=True):
    """Generates a custom imaging script. Only used for imaging."""
    os.chdir(project_dict['project_path'])
    parameters = sg.get_parameters(project_dict = project_dict, OT_dict = OT_dict) 
    script = sg.script_data_prep(parameters, project_dict, comments)
    spws = sg.sort_spws(parameters)
    continfo = spws[0]
    lineinfo = spws[1]
    linespws = spws[2]
    script = sg.make_continuum(script,parameters, project_dict, continfo, comments, flagchannels=False)
    script = sg.image_setup(script,parameters, comments)
    script = sg.cont_image(script,parameters, comments)
    if lineinfo != []:
        script = sg.contsub(script,parameters, continfo, linespws, comments)
        script = sg.line_image(script,parameters, lineinfo, comments)
    script = sg.pbcor_fits(script)
    sg.write_script(script,project_dict, filename = 'scriptForImaging.py')
    # cleanup temp files
    OT_info.cleanup(parameters['AOT'])


def main(lbc=False): # will ask for the OT file twice ... fix that
    """For imaging: 
	    Asks the user to enter information about the project, downloads and untars data from pipetemp, runs ASDMExportLight and the pipeline, applies fixes to the piperestore script, copies the flagtemplate files over, gets the imaging script, untars the weblog, fills the readme, and generates the file imaging_parameters.txt
For manual reduction:
        Creates the directory tree, runs ASDMExportLight and generates calibration script, fills the readme, asks the user whether or not to run the script through once and generate weblog plots in a pdf
    """
    project_dict = pi.main()
    OTfile = OT_info.getAOT(project_number=project_dict['project_number']) 
    makeDirectories(project_dict)
    if project_dict['project_type'] == 'Imaging':
        untarStuff(project_dict)
        os.chdir('%s/sg_ouss_id/group_ouss_id/member_ouss_id/' % project_dict['project_path'])
        project_dict['casa_version'] = pi.casa_version()
        if project_dict['casa_version'] != '4.3.1':
            pipelineChanges()
        downloadASDM(project_dict,lbc=lbc)
        copyFiles(project_dict) #don't actually do this yet
        #project_dict['casa_version'] = pi.casa_version()
        runPipeline(project_dict)
        #getScript(project_dict) #don't need this if we're generating the script
        untarWeblog()
        OT_dict = fillReadme(project_dict, AOT=OTfile)
        #OT_dict = OT_info.getOTinfo(project_dict['SB_name'], AOTpath = OTfile) # just fill the dictionary instead....
        #li.main(project_dict=project_dict, OT_dict = OT_dict)
        generate_script(project_dict, OT_dict)
    else : 
        os.chdir('%s' % project_dict['project_path'])
        script_name = downloadASDM(project_dict)
        #getScript(project_dict)
        OT_dict = fillReadme(project_dict, AOT=OTfile)
	for asdm in project_dict['asdm']:
	    os.chdir('%s/Calibration_%s' % (project_dict['project_path'],str(asdm[asdm.rfind('X'):]).lstrip()))
	    ms_name = glob.glob('*.ms')
	    snr = subprocess.Popen(["casa", "-c", "au.gaincalSNR(\'%s\')" % ms_name[0]], shell=False,stdout=subprocess.PIPE, stderr=subprocess.STDOUT) #this doesn't work yet for some reason...
	    snr.wait()
            print 'The results of running au.gaincalSNR are in %s/gaincalSNR.txt' % os.getcwd()
	    gaincal = snr.communicate()
            if os.path.isfile('gaincalSNR.txt') == False:
                os.mknod('gaincalSNR.txt')
            text = open('gaincalSNR.txt','w')
            text.writelines(gaincal[0])
            text.close()
        #runscript = raw_input('Run calibration script through and check the visibilities by generating a pdf of the weblog plots? Warning - this will take a while and do it for all the asdms!')
        #os.chdir('../')
        #if runscript == 'Y':
        #     for asdm in project_dict['asdm']:
	#         os.chdir('%s/Calibration_%s' % (project_dict['project_path'],str(asdm[-4:])))
        #         script_name = glob.glob('*.py')
        #         script = open(script_name, 'rw+') # insert line mysteps = [] at beginning of script...
        #         steps = script.readlines()
        #         steps[1] = 'mysteps = []\n'
        #         script.writelines(steps)
        #         script.close() 
        #         subprocess.call(["casa", "-c", "'%s'" % script_name[0]])
        #         script = open(script_name, 'rw+') # remove line mysteps = [] 
        #         steps = script.readlines() 
        #         steps[1] = '\n'
        #         script.writelines(steps)
        #         script.close() 
                 
        #         subprocess.call(["casa", "-c", "/lustre/naasc/elastufk/Python/checkvispdf.py"]) # does this need the path?
        #os.chdir('../')
        print 'Make sure to run the script generator once your calibrated or combined ms is in the Imaging/ directory!'

if __name__ == "__main__" :
    main()
