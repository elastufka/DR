"""#######################################
# project_info.py
# Erica Lastufka 08/20/2015 

#Description: Get the information about a project and store it in a dictionary. Used for staging, filling the readme, generating the script 

#######################################
# Usage:
#	import project_info
#       project_info = project_info.main()

#   The user will have to enter: 
#       Project type (Imaging/Manual)
#       lustre username or directory to create reduction directory in (ex. elastufk or /lustre/naasc/sciops/qa2/elastufk/Imaging)
#       Paragraph form the SCOPS ticket describing project 
#	ex:
#	 Project: 2013.1.00099.S
#	 GOUS: uid://A001/X122/X45
#	 MOUS: uid://A001/X122/X46
#	 SBName: NGC253_a_06_TE
#	 SBuid: uid://A001/X122/X33
#	 ASDMs: uid://A002/X98124f/X478d
#

######################################
"""
import glob
import os
import sys

def extract_id(line):
    """Get string of ASDM id's from SCOPS ticket paragraph."""
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
    """Get list of ASDMs from SCOPS ticket paragraph."""
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
    """Re-formats the MOUS and ASDM codes. Mostly for staging."""
    mous_code = mous_code.replace('/','_').replace(':','_')
    #alias = '%s.MOUS.%s.SBNAME.%s' % (project_number, mous_code, SB_name)
    #project_base = '%s/sg_ouss_id/group_ouss_id/member_ouss_id/' % (project_path)
    tarball = '%s.MOUS.%s.SBNAME.%s.tgz' % (project_number, mous_code, SB_name)
    return mous_code, tarball

def project_type(): # make this behave a little better...maybe not a while loop
    """Query user for project type."""
    proj_type = raw_input('> Is this an imaging assignment or manual reduction? (Imaging/Manual):').strip()
    while (proj_type != 'Imaging' and proj_type != 'Manual'):
        proj_type = raw_input('> Please enter either Imaging or Manual: ').strip()
    return proj_type

def directory( proj_type, project_number, codes):
    """Asks user for project directory or lustre username"""
    import sys
    lustre = raw_input('> Path to working directory? To use or create reduction directory in your lustre QA2 area, enter your username. ').strip()
    if lustre[len(lustre)-1] != '/':
        if lustre.find('/') != -1:
             directory = lustre
        elif proj_type == 'Imaging': 
             directory = '/lustre/naasc/sciops/qa2/' + lustre + '/' + codes[1][:-4] + '-analysis' #new horrible naming convention
        else:
             directory = '/lustre/naasc/sciops/qa2/' + lustre + '/'+ codes[0] # name of directory is MOUS code 
    else:
        lustre = lustre[0:len(lustre)-1]
        if lustre.find('/') != -1:
             directory = lustre

    #if os.path.isdir(directory) == False:
    #    sys.exit('ERROR: %s does not exist or read/write permissions are not granted!' % directory)

    return directory

def SB_name():
    """Asks user for SB name"""
    SB_name = raw_input('> What is the SB name? ').strip()
    return SB_name

def paragraph(): # only really need SB name and OT file name...
    """Asks user for SCOPS or NADR paragraph"""
    paragraph = []
    print 'Please copy and paste the complete paragraph describing your assignment from the SCOPS or NADR ticket'
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
    """Figures out correct CASA version."""
    folders = glob.glob('*')
    if 'sg_ouss_id' in folders:
        os.chdir('sg_ouss_id/group_ouss_id/member_ouss_id/log/')
    elif 'log' in folders:
        os.chdir('log/')
    # open casa logger and see what version was used
    try:
        logs = glob.glob('casapy*.log')
        log = logs[0]
        logtext = open(log,'r')
        lines = logtext.readlines()
        for line in lines:
            if 'CASA Version' in line:
                 version=line[line.find('CASA Version')+13:line.find('CASA Version') + 18]
                 #version = line[51:56]
                 break
    except IndexError:
        version=query_version()
    os.chdir('../')
    return version

def query_version():
    """Asks user for CASA version in case of no log file or can't find it in log file."""    
    version = raw_input('Version of CASA to use? Default is 4.5.1').strip() or '4.5.1'
    return version

def pipeline_path():
    """Asks user for pipeline path. Obsolete."""
    pipeline_path = raw_input('> Please enter the path to the pipeline version you want to run (include filename). Default is /lustre/naasc/sciops/pipeline/pipeline_env_r31667_casa422_30986.sh :').strip() or '/lustre/naasc/sciops/pipeline/pipeline_env_r31667_casa422_30986.sh' 
    return pipeline_path

def project_info_dict(proj_type, project_path, project_number, codes, SB_name, asdm, version):
    project_info_dict={'project_type': proj_type,'project_path': project_path, 'project_number': project_number, 'mous_code': codes[0], 'SB_name': SB_name, 'number_asdms': len(asdm), 'asdm': asdm, 'tarball': codes[1], 'casa_version': version}
    return project_info_dict

# different function that leaves out pipeline, etc. for fill_readme and list_imparameters... coordinate this with OT_info?
def most_info(SBname=False, project_path = False): # project_path is the /lustre/naasc/username/Reduce_XXX directory
    """Gets most of the relevant info - leaves out the stuff needed for pre imaging eg tarball, pipeline path. Also gets the OT dictionaries."""
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
    if 'sg_ouss_id' in folders: # it's an imaging assignment
        proj_type = "Imaging"
        version = casa_version()
    elif 'Imaging' in folders: # it's a manual assignment
        proj_type = "Manual"    
        version = query_version()
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
    """Main method. Gathers information and puts it into a dictionary, project_dict"""
    proj_type = project_type()
    para = paragraph()
    project_number = para[0].strip()
    mous_code = para[1].strip()
    SB_name = para[2].strip()
    asdm = para[3]
    codes = fixCodes(mous_code, project_number, SB_name)
    project_path = directory(proj_type, project_number, codes)

    if proj_type == 'Imaging': # move this elsewhere?
        try:
            os.chdir(project_path)
            version = casa_version() # will have to figure this out in pre-imaging
        except OSError:
            version = ''
    if proj_type == 'Manual':
        version = query_version()

    project_dict = project_info_dict(proj_type, project_path, project_number, codes, SB_name, asdm, version)
    #print project_dict
    return project_dict

if __name__ == "__main__":
    main()

