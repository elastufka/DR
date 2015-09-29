#######################################
# OT_info.py
# Erica Lastufka 09/04/2015 

#Description: Get info about the AOT file and import the xml trees. Put these into a dictionary.
#######################################

#######################################
# Usage:
#       import OT_info as OT
#	OT.getOTinfo(SB_name, AOT=False) 
#       (if you don't have the name and location of the OT file)
#	OT.getOTinfo(SB_name, AOT=AOT) 
######################################

#########################################
# functions: 

#	getfileinfo(AOT)
#	    splits input into directory and filename

#	unzipAOT(AOTdir, AOTfile)
#	    Unzips the AOT file into a temp directory

#	importData()
#	    Imports the XML into python

# 	getSB(SB_name, namespaces)
#	    Finds the correct SchedBlock*.xml file for the given SB

#	getDictionaries(AOTdir, AOTfile, prop_root, proj_root, science_root, sg, namespaces)
#	    Puts everything into 2 dictionaries, one with the file info (OT_dict) and one with the actual XML roots (XML_roots)

#	getOTinfo(SB_name, AOT=False)
#	    Generates the dictionaries and returns them as (OT_dict, XML_roots)
#########################################

import os
import glob
import xml.etree.ElementTree as ET
import sys

def getAOT():
    files = glob.glob('*.aot')
    #print files
    if not files:
       AOT=raw_input('Where is the AOT file located? Full path and file name please. ')
    elif len(files) == 1:
        AOT = os.getcwd() + '/' + files[0]
    else:
        print files
        AOT=raw_input('Which is the correct file for this project? ')

    return AOT

def getfileinfo(AOT):
    AOTdir = AOT[0:AOT.rfind('/')]   #everything before the last /
    AOTfile = AOT[AOT.rfind('/')+1:len(AOT)]  # everything after the last /
    return AOTdir, AOTfile

def unzipAOT(AOTdir, AOTfile):
   os.chdir(AOTdir)
   if os.path.isfile(AOTfile) == False:
       sys.exit('ERROR: OT flle %s not find in directory %s!' % (AOTfile, AOTdir))
   if os.path.isdir('temp') == False:
       os.system('mkdir temp' )
   print 'Unzipping .aot file'
   os.system('unzip %s -d temp' % AOTfile) #why is -dfq not working anymore?
   os.chdir('temp/')

# import the data. Will fail if not in the correct directory ... 
def importData():
   proptree = ET.parse('ObsProposal.xml') #sensitivity is here
   projtree = ET.parse('ObsProject.xml') # title is here
   prop_root = proptree.getroot()
   proj_root = projtree.getroot()
   namespaces={'prj':'Alma/ObsPrep/ObsProject', 'sbl': "Alma/ObsPrep/SchedBlock", 'val': "Alma/ValueTypes", 'prp':"Alma/ObsPrep/ObsProposal"}
   return prop_root, proj_root, namespaces

def getSB(SB_name, namespaces): # get correct SchedBlockN.xml file to use. Will fail if not in the correct directory ... 
   import sys
   SBlist=glob.glob('SchedBlock*.xml')
   sg = 'None'
   science_root = ''
   #print SB_name
   for sb in SBlist:
       testtree = ET.parse(sb)
       testroot = testtree.getroot()
       sched_name = testroot.find('prj:name', namespaces)
       #print sched_name.text
       if sched_name.text == SB_name:
           print 'SB found'
           science_goal = sb
           science_root=testroot
           sg = str(science_goal[10])
           if str(science_goal[11]) != '.':
               sg = sg + str(science_goal[11])
   #print sg
   if sg == 'None':
       sys.exit('ERROR: SB_name not found in OT file! Please make sure these are correct.')
   return sg, science_root

def getDictionaries(AOTdir, AOTfile, prop_root, proj_root, science_root, sg, namespaces):
    OT_dict = {'AOT': AOTdir+ '/' + AOTfile, 'tempdir': AOTdir+'/temp', 'science_goal': sg}
    XMLroots = {'prop_root': prop_root, 'proj_root': proj_root, 'science_root': science_root, 'namespaces': namespaces}
    return OT_dict, XMLroots

def cleanup(AOT):
    AOTdir = AOT[0:AOT.rfind('/')]
    os.chdir(AOTdir)
    os.system('rm -rf temp/')

def getOTinfo(SB_name, AOTpath=False):
    if AOTpath==False:
        AOTpath=getAOT()
    OTinfo = getfileinfo(AOTpath)
    unzipAOT(OTinfo[0],OTinfo[1])
    XMLroots = importData()
    namespaces = XMLroots[2]
    SGinfo = getSB(SB_name, namespaces) #have to have variable SB_name already defined else will fail
    dictionaries = getDictionaries(OTinfo[0],OTinfo[1], XMLroots[0], XMLroots[1], SGinfo[1], SGinfo[0], XMLroots[2])
    return dictionaries


