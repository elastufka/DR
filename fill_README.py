#######################################
# fill_README.py
# Erica Lastufka 08/20/2015 

#Description: Fills out the header information of the README
#######################################

#######################################
# Usage:
#	execfile("fill_README.py") 
#           or 
#       import fill_README as fr
#       fr.main(project_dict=project_dict, AOT=AOT)
#       (if you already have the dictionaries)

#   In the first instance, the user will have to enter: 
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
# 	OPTIONAL pipeline version to source (ex. /lustre/naasc/pipeline/pipeline_env_r31667_casa422_30986.sh)
# 	location and name of the OT file (ex. /lustre/naasc/elastufk/2013.1.00099.S_v2.aot)
#########################################

#########################################
# functions: 

#	getInfo(project_dict, OT_dict)
#           Gets PI name, project title, and proposed rms from the XML

#       write2Readme(project_type, project_path, project_info, version)
#	    Writes header information to READMe

#	testwrite()
#	    test method for writing 

#	cleanup(AOTdir)
#	    removes temp directory

#	main(project_dict=False, AOT=False)
#	    Asks the user for project information or reads the information from the provided dictionaries to write to the README

######################################### 

#import glob
import numpy as np
import xml.etree.ElementTree as ET
import os
import glob
import OT_info 
import project_info

    
def getInfo(project_dict, OT_dict):
    XMLroots = OT_dict[1]
    prop_root = XMLroots['prop_root']
    proj_root = XMLroots['proj_root']
    science_root = XMLroots['science_root']
    namespaces = XMLroots['namespaces']

    # get PI name
    PI_name = prop_root.find('prp:PrincipalInvestigator', namespaces)

    # get project title 
    title = proj_root.find('prj:projectName', namespaces) #test this

    '''
    # get configuration (may have to get this from the weblog, Observation Summary table)
    htmldir = '../qa/pipewhatever/html/'
    html=open(htmldir+ 'index.html')
    '''

    # get rms (line) -> this might depend on which science goal, be careful! 
    rms = science_root.find('.//sbl:ScienceParameters/sbl:sensitivityGoal', namespaces) 
    unit = rms.attrib

    project_info = {'project_number': project_dict['project_number'], 'SB_name': project_dict['SB_name'], 'PI_name': PI_name[0].text, 'title': title.text, 'rms': rms.text, 'rms_unit': unit['unit']}
    return project_info

def write2Readme(project_type, project_path, project_info, version):
    # go to directory
    if project_path[len(project_path)-1] != '/': 
        project_path = project_path + '/'
    
    os.chdir(project_path)
    
    if project_type == 'Imaging':
        os.chdir(project_path + 'sg_ouss_id/group_ouss_id/member_ouss_id/')
        #version = '4.2.2'
    else:
        os.chdir('Imaging')
        #version = '4.4.0'
    
    if os.path.isfile('README.header.txt') != True:
       os.system('cp -i /users/thunter/AIV/science/qa2/README.header.cycle2.txt README.header.txt')
    os.system('pwd')
    readme = open('README.header.txt','r') 
    rinfo = readme.readlines()
    readme.close
    rinfo[5] = 'Project code: ' + project_info['project_number'] + '\n'
    rinfo[6] = 'SB name: ' + project_info['SB_name'] + '\n'
    rinfo[7] = 'PI name: ' + project_info['PI_name'] + '\n'
    rinfo[8] = 'Project title: ' + project_info['title'] +'\n'
    #rinfo[9] = 'Configuration: ' + config + cunit +'\n'
    rinfo[10] = 'Proposed rms: ' + project_info['rms'] +' ' + project_info['rms_unit'] + ' (line)\n'
    rinfo[11] = 'CASA version used for reduction: ' + version +'\n'

    os.mknod('readme.txt')
    readmenew = open('readme.txt', 'w')
    
    readmenew.writelines(rinfo) # why doesn't this write???
    readmenew.close()
    os.system('mv -f readme.txt README.header.txt') #don't know why I have to do all this...

def cleanup(AOT):
    AOTdir = AOT[0:AOT.rfind('/')]
    os.chdir(AOTdir)
    os.system('rm -rf temp/')

def main(project_dict=False, AOT=False):
    if project_dict == False:
        project_dict = project_info.main()
    if AOT == False:
        AOT_dict = OT_info.getOTinfo(project_dict['SB_name'], AOTpath=False)
    else:
        AOT_dict = OT_info.getOTinfo(project_dict['SB_name'],AOTpath=AOT)
    AOTdir = AOT_dict[0]
    readme_info = getInfo(project_dict,AOT_dict)
    write2Readme(project_dict['project_type'], project_dict['project_path'], readme_info, project_dict['casa_version']) # why won't this write??
    #fill_README.testwrite()
    cleanup(AOTdir['AOT'])

if __name__ == "__main__":
    main()
