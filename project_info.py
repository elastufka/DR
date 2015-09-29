#######################################
# project_info.py
# Erica Lastufka 08/20/2015 

#Description: Get the information about a project and store it in a dictionary
#######################################

#######################################
# Usage:
#	import project_info
#       project_info = project_info.main()

#   The user will have to enter: 
#       Project type (Imaging/Manual)
#       lustre username or directory to create Reduce_XXXX directory in (ex. elastufk or /lustre/naasc/elastufk/Imaging)
#       Paragraph form the SCOPS ticket describing project 
#	ex:
#	 Project: 2013.1.00099.S
#	 GOUS: uid://A001/X122/X45
#	 MOUS: uid://A001/X122/X46
#	 SBName: NGC253_a_06_TE
#	 SBuid: uid://A001/X122/X33
#	 ASDMs: uid://A002/X98124f/X478d
#
# 	pipeline version to source (ex. /lustre/naasc/pipeline/pipeline_env_r31667_casa422_30986.sh)

######################################

#########################################
# functions: 

#	extract_id(line)
#	    Parses the paragraph to get the relevant parameters

#	asdmLoop(paragraph)
#	    Gets the complete list of ASDMs

#	fixCodes(mous_code, project_number, SB_name, project_path)
#	    re-formats the MOUS and ASDM codes

#	proj_type()
#	    Asks user for project type

#	directory()
#	    Asks user for project directory or lustre username

#	project_path(proj_type, directory, project_number = False, mous_code = False)
#	    Constructs project path and base directory (if imaging)

#	paragraph()
#	    Asks user for SCOPS or NADR paragraph

#	pipeline_path()
#	    Asks user for pipeline version - don't need this anymore

#	SB_name()
#	    Asks user for SB name

#	project_info_dict(proj_type, project_path, project_number, codes, SB_name, asdm, pipeline_path)
#	    Constructs dictionary

#	most_info()
#	    Gets most of the relevant info - leaves out the stuff needed for pre imaging eg tarball, pipeline path. Also gets the OT dictionaries.

#	main()
#	    Gets the info and fills the dictionary
#########################################
import glob
import os

def extract_id(line):
    colon = line.find(': ')
    comma= line.find(',')
    amperstand= line.find('and')
    if colon != -1:
        return line[colon+2:len(line)]
    elif comma != -1: 
        return (line[0:comma], line[comma+1:len(line)])
    elif amperstand != -1:
        return (line[0:amperstand-1],line[amperstand+4:len(line)])

def asdmLoop(paragraph):
    asdm=[]
    asdmloop=[]
    asdmid=extract_id(paragraph[5])
    asdmloop=extract_id(asdmid)
    while asdmloop != None:
        if len(asdmloop) == 2:
            asdm.append(asdmloop[0])
        else:
            asdm.append(asdmloop)
        asdmid=asdmloop[1]
        asdmloop=extract_id(asdmid)
    asdm.append(asdmid)
    for n in range(0,len(asdm)):
        asdm[n]=asdm[n].lstrip()
    #print asdm
    return asdm #asdm is now the complete list of asdms

def fixCodes(mous_code, project_number, SB_name):
    mous_code = mous_code.replace('/','_').replace(':','_')
    #alias = '%s.MOUS.%s.SBNAME.%s' % (project_number, mous_code, SB_name)
    #project_base = '%s/sg_ouss_id/group_ouss_id/member_ouss_id/' % (project_path)
    tarball = '%s.MOUS.%s.SBNAME.%s.tgz' % (project_number, mous_code, SB_name)
    return mous_code, tarball

def project_type(): # make this behave a little better...maybe not a while loop
    proj_type = raw_input('> Is this an imaging assignment or manual reduction? (Imaging/Manual):').strip()
    while (proj_type != 'Imaging' and proj_type != 'Manual'):
        proj_type = raw_input('> Please enter either Imaging or Manual: ').strip()
    return proj_type

def directory():
    lustre = raw_input('> Path to working directory? To use or create directory Reduce_XXXXX in your lustre area, enter your username. ').strip()
    if lustre[len(lustre)-1] != '/':
        if lustre.find('/') != -1:
             directory = lustre
        else: 
             directory = '/lustre/naasc/' + lustre 
    else:
        lustre = lustre[0:len(lustre)-1]
        if lustre.find('/') != -1:
             directory = lustre
        else: 
             directory = '/lustre/naasc/' + lustre 

    if os.path.isdir(directory) == False:
        sys.exit('ERROR: %s does not exist or read/write permissions are not granted!' % directory)

    return directory

def project_path(proj_type, directory, project_number = False, mous_code = False):
    if proj_type == 'Imaging': 
        project_path = directory + '/Reduce_' + project_number[7:12]
        #project_base = '%s/sg_ouss_id/group_ouss_id/member_ouss_id/' % (project_path)
    if proj_type == 'Manual':
        project_path = directory + '/Reduce_' + str(mous_code[mous_code.rfind('/')+1:])  
        #project_base = project_path

    return project_path

def SB_name():
    SB_name = raw_input('> What is the SB name? ').strip()
    return SB_name

def paragraph(): # only really need SB name and OT file name...
    paragraph = []
    print 'Please copy and paste the complete paragraph describing your assignment from the scops or nadr ticket'
    for n in range(0,6):
        input_str = raw_input(">")
        paragraph.append(input_str)
    # get information about a project and store it in a dictionary
    project_number = extract_id(paragraph[0])
    mous_code = extract_id(paragraph[2]) 
    SB_name = extract_id(paragraph[3]) 
    SB_name = SB_name.lstrip() #get rid of extra whitespace
    asdm = asdmLoop(paragraph)

    return project_number, mous_code, SB_name, asdm

def casa_version():
    folders = glob.glob('*')
    if 'sg_ouss_id' in folders:
        os.chdir('sg_ouss_id/group_ouss_id/member_ouss_id/log/')
    elif 'log' in folders:
        os.chdir('log/')
    # open casa logger and see what version was uesd
    logs = glob.glob('casapy*.log')
    log = logs[0]
    logtext = open(log,'r')
    lines = logtext.readlines()
    for line in lines:
        if 'CASA Version' in line:
             version = line[51:56]
             break
    os.chdir('../')
    return version

def pipeline_path():
    pipeline_path = raw_input('> Please enter the path to the pipeline version you want to run (include filename). Default is /lustre/naasc/pipeline/pipeline_env_r31667_casa422_30986.sh :').strip() or '/lustre/naasc/pipeline/pipeline_env_r31667_casa422_30986.sh' 
    return pipeline_path

def project_info_dict(proj_type, project_path, project_number, codes, SB_name, asdm, version):
    project_info_dict={'project_type': proj_type,'project_path': project_path, 'project_number': project_number, 'mous_code': codes[0], 'SB_name': SB_name, 'number_asdms': len(asdm), 'asdm': asdm, 'tarball': codes[1], 'casa_version': version}
    return project_info_dict

# different function that leaves out pipeline, etc. for fill_readme and list_imparameters... coordinate this with OT_info?
def most_info(SBname=False, project_path = False): # project_path is the /lustre/naasc/username/Reduce_XXX directory
    import OT_info as OT
    import glob
    import os
    import sys

    #proj_type = project_type()
    if project_path == False:
        project_path = directory()
    if SBname == False:
        SBname = SB_name() 

    # figure out the project type:
    os.chdir(project_path)
    #print project_path
    folders = glob.glob('*')
    if 'sg_ouss_id' in folders:
        proj_type = "Imaging"
        version = casa_version()
    elif 'Imaging' in folders:
        proj_type = "Manual"    
        version = '4.4.0'
    elif 'S.MOUS.uid' in folders[0]: # in case people still do that
        proj_type = "Imaging"
        version = casa_version()
        project_path = project_path + folders[0]
    else:
        sys.exit('ERROR: Wrong directory or wrong structure in directory! Please make sure folder names comply with NA arc best practices for imaging or manual calibration.')

    os.chdir(project_path)
    AOT = glob.glob('*.aot')
    if not AOT:
         AOTpath = False
    else:
        AOTpath = os.getcwd()+'/' + AOT[0]
    print AOTpath
   
    OT_dict = OT.getOTinfo(SBname, AOTpath=AOTpath)
    AOTfile = OT_dict[0]['AOT']  
    project_number = AOTfile[AOTfile.rfind('/')+1:len(AOTfile)]
    project_number = project_number[0:14]

    codes = ['N/A', 'N/A']
    asdm = ['N/A']

    project_dict = project_info_dict(proj_type, project_path, project_number, codes, SBname, asdm, version)
    #print project_dict, OT_dict
    return project_dict, OT_dict


def main():
    proj_type = project_type()
    wd = directory()
    para = paragraph()
    project_number = para[0].strip()
    mous_code = para[1].strip()
    SB_name = para[2].strip()
    asdm = para[3]
    codes = fixCodes(mous_code, project_number, SB_name)
    if proj_type == 'Imaging': # move this elsewhere?
        project_path = wd + '/Reduce_' + project_number[7:12]
        os.chdir(project_path)
        version = casa_version() # will have to figure this out in pre-imaging
        #project_base = '%s/sg_ouss_id/group_ouss_id/member_ouss_id/' % (project_path)
    if proj_type == 'Manual':
        project_path = wd + '/'+ codes[0]  
        version = '4.4.0'
        #project_base = project_path
    
    project_dict = project_info_dict(proj_type, project_path, project_number, codes, SB_name, asdm, version)
    #print project_dict
    return project_dict

if __name__ == "__main__":
    #most_info('NGC6357__a_03_7M','/lustre/naasc/elastufk/Imaging/testscript/sg_ouss_id/group_ouss_id/member_ouss_id/calibrated')
    main()

