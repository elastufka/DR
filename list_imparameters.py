"""#######################################
# list_imparameters.py
# Erica Lastufka 08/20/2015 

#Description: Gets useful parameters for imaging from the OT XML files and writes them to imaging_parameters.txt. Places this file in the /calibrated/ directory of the current project. Also used to generate parameter dictionary to pass to the script generator.
#######################################

#######################################
# Usage:
#	execfile("list_parameters.py") 
#           or 
#       import list_parameters as li
#       li.main(project_dict, OT_dict)   
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
"""
#########################################
# functions: 

#	getnum_ms(project_path, alias)
#           returns the number of ms's in the folder

#       getListobs()
#	    gets information from listobs, etc by running casa_stuff.py in CASA

#	getNspw(lines, index)
#	    returns the number of spws and an integer array of their indexes

#	getCell(lines, index)
#	    returns cell size and image size recommended by au.pickCellSize

#	getScienceFields(lines, index)
#	    returns the first and last index of the science fields
    
#	getLines(index, numspws)
#	    returns lines from the listobs that have to do with the spws

#	getSpwInfo(science_root, namespaces, spws)
#	    returns a dictionary containing information on each spw's rest frequency, transition, and number of channels

#	getRestFreq(science_root, namespaces)
#	    returns the representative frequency in Hz 

#	getVelWidth(science_root,namespaces, rfreqHz=False)
#	    converts the bandwidth for sensitivity to velocity units. Returns velocity width, bandwidth for sensitivity and unit

#	getRefFrame(science_root, namespaces)
#	    returns the reference frame of the source

#	genPlotMS(spwinfo, rframe)
#	    returns plotms commands for velocity transformations in line spws

#	mosaicBool(namespaces, projroot, sg)
#	    returns a boolean telling whether the project is a mosaic or not

#	ismosaic(projroot, namespaces, sg, lastfield, firstfield)
#	    returns strings with information about whether a project is a mosaic and the number of pointings.

#	sourceName(science_root, namespaces)
#	    returns name of the science target

#	openFile()
#	    opens imaging_parameters.txt in /calibrated/ directory

#	fillInfo(p)
#	    puts the dictionary information in easy-to-use text

#	writeText(param, info)
#	    writes text to file

#	testmain()
#	    tests the program with a predefined dictionary
    
#	main()
#	   runs everything

######################################### 

import subprocess
import glob
import xml.etree.ElementTree as ET
import os
import scipy.constants
import OT_info 
import project_info 
import fill_README
import IPython
import sys

#######################
# get the relevant parameters
#######################

# find if there are multiple ms's 
def getnum_ms(project_type, project_path):
    if project_type == "Imaging":
        os.chdir('%s/sg_ouss_id/group_ouss_id/member_ouss_id/calibrated' % project_path)
    else:
        os.chdir('%s/Imaging' % project_path)
    vislist=glob.glob('*.ms.split.cal')
    if not vislist:
        vislist = glob.glob('calibrated.ms')
    nms = len(vislist)
    return nms

def getListobs():
    variables=subprocess.Popen([ "casa","-r" "4.3.1" " -c", " /lustre/naasc/users/elastufk/Python/casa_stuff.py"], shell=False,         stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    variables.wait()
    stuff = variables.communicate()
    lines = stuff[0].split('\n')
    print lines
    for line in lines:
        if line.startswith('Median OBSERVE_TARGET') or line.startswith('Field'):
            index = lines.index(line)
            break
            #else: #something bad happend with casa...
            #    print 'Error message'
    try:
        if index:
            pass
    except UnboundLocalError:
        sys.exit('something went wrong with CASA!')
    return lines, index

# get number of spws, science fields, and cell size while we're at it.
def getNspw(lines, index):
    nspws = lines[index + 1] # stuff in the line after Median OBSERVE_TARGET frequency = 343.463 GHz 
    nspws = nspws[1:-1].strip() # get rid of the [ ]
    nspws = nspws.replace('  ', ',') # separate with commas
    nspws = nspws.replace(' ', ',') # separate with commas
    # turn into an integer vector
    spws = map(int,nspws.split(','))
    numspws = len(spws)
    return numspws, spws

def getCell(lines): #will this be true for multiple executions?
    for line in lines:
        if 'arcsec' in line:
            cellsize = line[2:line.find(",")-1]
            imsize = line[line.find(",")+2:-1] # what if it's a mosaic?
    return cellsize, imsize[0:imsize.rfind(']')+1]

def getScienceFields(lines, index):
    index = index + 2
    sfields = lines[index] #because I doubt you'll ever have enough spws to go over to 2 lines
    while sfields[len(sfields)-1] !=']':
        index = index+1
        sfields = sfields + lines[index] # search for starting [ and append until there.... 
 
    sfields = sfields[1:-1].strip()
    sfields = sfields.replace('  ',',')
    sfields = sfields.replace(' ',',')
    return sfields

# get relevant lines from the text files
def getLines(index, numspws):
    specinfo = []
    listobs=glob.glob('*.listobs.txt')
    for obs in listobs:
        text = open(obs, 'rw+')
        listtext = text.readlines()
        for num, line in enumerate(listtext,0):
            if 'Spectral Windows' in line: 
                index = num
        specinfo.append(listtext[index:index+numspws+2])
        specinfo.append('\n')
        text.close()
    return specinfo

# spw info 
def getSpwInfo(science_root, namespaces, spws): # let's put stuff into an spw dictionary....
    spwprint = 'You have no continuum-dedicated spws. \n' # default
    #get the right 'SpectralSpec' block...don't want the pointing one! <sbl:name>HCN v=0 J=1-0 Science setup_1</sbl:name>
    spectralspec = science_root.findall('.//sbl:SpectralSpec/', namespaces)

    for n in range(0, len(spectralspec)): # don't want to get the pointing setup instead!
        if 'Science setup' in spectralspec[n].text:
            correlator = spectralspec[n+1]
            nchannels=correlator.findall('sbl:BLBaseBandConfig/sbl:BLSpectralWindow/sbl:effectiveNumberOfChannels', namespaces)
            avg = correlator.findall('sbl:BLBaseBandConfig/sbl:BLSpectralWindow/sbl:spectralAveragingFactor', namespaces) # get the averaging factor
            if nchannels == []:
                nchannels=correlator.findall('sbl:ACABaseBandConfig/sbl:ACASpectralWindow/sbl:effectiveNumberOfChannels', namespaces)
                avg = correlator.findall('sbl:ACABaseBandConfig/sbl:ACASpectralWindow/sbl:spectralAveragingFactor', namespaces)
            break
        #else:
        #    print 'blah'# ? sys.exit etc
    spwtype = science_root.findall('.//sbl:SpectralSpec/sbl:BLCorrelatorConfiguration/sbl:BLBaseBandConfig/sbl:BLSpectralWindow/sbl:SpectralLine/sbl:transition', namespaces) # won't work if it's ACA!!!!
    spwrfreq = science_root.findall('.//sbl:SpectralSpec/sbl:BLCorrelatorConfiguration/sbl:BLBaseBandConfig/sbl:BLSpectralWindow/sbl:SpectralLine/sbl:restFrequency', namespaces)

    if (spwtype == [] and spwrfreq == []):
        spwtype = science_root.findall('.//sbl:SpectralSpec/sbl:ACACorrelatorConfiguration/sbl:ACABaseBandConfig/sbl:ACASpectralWindow/sbl:SpectralLine/sbl:transition', namespaces) 
        spwrfreq = science_root.findall('.//sbl:SpectralSpec/sbl:ACACorrelatorConfiguration/sbl:ACABaseBandConfig/sbl:ACASpectralWindow/sbl:SpectralLine/sbl:restFrequency', namespaces)
    #skyfreq = science_root.findall('.//sbl:SpectralSpec/sbl:BLCorrelatorConfiguration/sbl:BLBaseBandConfig/sbl:BLSpectralWindow/sbl:SpectralLine/sbl:restFrequency', namespaces)
    spwdict=[]

    # if calibrated.ms instead of .ms.split.cal ... data may have been combined before. 
    #os.chdir('../') #hope this doesn't mess anything up....
    if os.path.isdir('calibrated.ms'): 
        print 'WARNING: Your data have been combined into a single ms from multiple executions, resulting in %s spws. Please check the resulting script carefully!' % str(len(spws))
        aa = spwtype
        bb = spwrfreq
        cc = nchannels
        dd = avg
        while len(spwtype) != len(spws): # you have more spws because they're from different executions. 
            spwtype = spwtype + aa
            spwrfreq = spwrfreq + bb
            nchannels = nchannels + cc
            avg = avg + dd
        #os.chdir('Imaging')

    for n in spws:
        # get number of channels
        nchan = str(int(nchannels[n].text)/int(avg[n].text))
        kw = ['continuum','Continuum','cont','Cont']
        for i in range(0,len(kw)):
            if kw[i] in spwtype[n].text: 
                transition = 'continuum'
                break
            elif spwtype[n].text == 'Spec__Scan_': #panic
                spwprint = 'This is a spectral scan ... good luck' + '\n'
                transition = 'Spectral Scan'
            else: 
                transition= spwtype[n].text # it's a line with this transition
        spwdict.append({'index': n, 'type': spwtype[n].text, 'nchan': nchan, 'restfreq': spwrfreq[n].text, 'transition': transition})
        #IPython.embed()
    return spwdict

# get rest frequency
def getRestFreq(science_root, namespaces):
    rfreq = science_root.find('.//sbl:SchedulingConstraints/sbl:representativeFrequency',namespaces)
    rfrequnit = rfreq.attrib
    if rfrequnit['unit'] == 'GHz':
        rfreqHz = float(rfreq.text)*1e9
    elif rfrequnit['unit'] == 'MHz':
        rfreqHz = float(rfreq.text)*1e6
    return rfreqHz

# get velocity width - restructure that if statement
def getVelWidth(science_root,namespaces, rfreqHz=False):
    rwidth = science_root.find('.//sbl:ScienceParameters/sbl:representativeBandwidth',namespaces)
    rwidthunit = rwidth.attrib
    if rwidthunit['unit'] == 'MHz':
        rwidthHz = float(rwidth.text)*1e6
    elif rwidthunit['unit'] == 'GHz':
        rwidthHz = float(rwidth.text)*1e9
    elif rwidthunit['unit'] == 'KHz':
        rwidthHz = float(rwidth.text)*1e3
    elif rwidthunit['unit'] == 'm/s':
        vwidth = rwidth.text*(1e-3) # let's go to km/s
        rwidthunit['unit'] == 'km/s'
    elif rwidthunit['unit'] == 'km/s':
        vwidth = rwidth.text

    # convert bandwidth to sensitivity to velocity units if that hasn't already been done
    if (rwidthunit['unit'] != 'm/s' or rwidthunit['unit'] != 'km/s'):
        if rfreqHz !=False:
            vwidth = (scipy.constants.c/rfreqHz)*rwidthHz # m/s
        else: 
            print 'Please specify the rest frequency in Hz'
            vwidth = '1' #not 0 just in case
    return vwidth, rwidthHz, rwidthunit['unit']

# get reference frame
def getRefFrame(science_root, namespaces):
    query = science_root.findall('.//sbl:FieldSource/sbl:isQuery',namespaces)
    sv = science_root.findall('.//sbl:FieldSource/sbl:sourceVelocity',namespaces)
    for n in range(0,len(query)):
        if query[n].text == 'false':
            rframe = sv[n].attrib['referenceSystem']
            break

    if rframe == 'hel': #bary for helio
        rframe = 'BARY'
    elif rframe == 'bar':
        rframe = 'BARY'
    else: 
        rframe = rframe.upper()
    return rframe

# generate plotms commands for each line spw to help with picking start and nchan
# if the ms is combined, have to modify the spw argument
# maybe generate these in the script generator instead
def genPlotMS(spwinfo, rframe, spw):
    for n in range(0,len(spwinfo)):
        if spwinfo['transition'] != 'continuum':
        #if not spw: # do we actually need this? if generating the commands in sg.line_image()
        #    spw = str(n)
            plotcmd = "plotms(vis=linevis, xaxis='velocity', yaxis='amp', spw = '%s', transform=T, freqframe='%s',\n        restfreq='%sMHz', avgtime='1e8', avgantenna=T)" % (spw, rframe, str(float(spwinfo['restfreq'])*1e3))

    return plotcmd
 
# mosaic? 
def mosaicBool0riginal(namespaces, projroot,sg):   
    goals = projroot.findall('.//prj:ScienceGoal',namespaces)
    sci_goal = goals[int(sg)] # won't work for a spectral scan! have to use the name for that one....
    sp = sci_goal.findall('prj:TargetParameters/prj:SinglePoint',namespaces)
    ismosaic = sci_goal.findall('prj:TargetParameters/prj:isMosaic',namespaces)

    if not sp:
    #if ismosaic[0].text == 'true':
        mosaicbool = 'true'
    elif ismosaic[0].text == 'true':
        mosaicbool = 'false'
        print 'WARNING: OT designates target as mosaic, but only a single pointing is found. Please check results carefully! imagermode will be set to "csclean" for the time being.'
    else:
        mosaicbool = 'false'
    return mosaicbool

# yet another attempt at getting a reliable mosaic indicator .... seems like the best thing to do is count the pointings, since ismosaic is always true
def mosaicBool(namespaces, science_root, sourceName):   
    query = science_root.findall('.//sbl:FieldSource/sbl:isQuery',namespaces) # if false that's the science target 
    pattern = science_root.findall('.//sbl:FieldSource/sbl:PointingPattern',namespaces)
    for n in range(0,len(query)):
        if query[n].text == 'false':
            #get the # of pointings 
            pointings=pattern[n].findall('sbl:phaseCenterCoordinates',namespaces)
            npointings=len(pointings)
            break 
        else: 
            npointings=0
    #IPython.embed()
    if npointings > 1:
        mosaicbool = 'true'
    elif npointings == 0:
        print "Couldn't find information about the number of pointings so assuming it's just 1"
        #error, default to single pointing
    else:
        mosaicbool = 'false'
    return mosaicbool

def ismosaic(mosaicbool,lastfield, firstfield): # fix this using mosaicbool
    if mosaicbool == 'true' :
        isMosaic = ''
        pointings = 'with ' + str(int(firstfield) - int(lastfield)) + ' pointings (fields ' + lastfield + '~' + firstfield + ' ). Use imagermode="mosaic".' # number of pointings - same as number of fields if it's a mosaic I guess
    else:
        isMosaic = 'not'
        pointings = 'so use imagermode="csclean". \n The science field index is ' + firstfield
    return isMosaic, pointings

def getPhasecenter(science_root, namespaces):
    # get source coordinates for science field
    sourceLong = science_root.findall('.//sbl:FieldSource/sbl:sourceCoordinates/val:longitude',namespaces)
    sourceLat = science_root.findall('.//sbl:FieldSource/sbl:sourceCoordinates/val:latitude',namespaces)
    system = science_root.findall('.//sbl:FieldSource/sbl:sourceCoordinates',namespaces)
    query = science_root.findall('.//sbl:FieldSource/sbl:isQuery',namespaces) # if false that's the science target ... or name = Primary:

    for n in range(0,len(query)):
        if query[n].text == 'false':
            sourceCoords = [sourceLong[n].text, sourceLat[n].text] 
            coordUnits = [sourceLong[n].attrib['unit'], sourceLat[n].attrib['unit']]
            break

    phasecenter = system[n].attrib['system'] + ' ' + sourceCoords[0] + coordUnits[0] + ' ' + sourceCoords[1] + coordUnits[1]
    return phasecenter
 
def sourceName(science_root, namespaces, SB_name):
    sourcenames = science_root.findall('.//sbl:FieldSource/sbl:sourceName',namespaces)
    name = science_root.findall('.//sbl:FieldSource/sbl:name',namespaces) # if false that's the science target ... or name = Primary:
    for n in range(0,len(sourcenames)):
        if sourcenames[n].text in SB_name:
            sourceName = sourcenames[n].text
            break
        elif name[n].text == 'Primary:':
            sourceName = sourcenames[n].text
            break
    try:
        sourceName
    except NameError:
        print 'source name could not be found! Will use the SB name instead.'
        sourceName = SB_name
    return sourceName

#######################
# write to image_parameters.txt
#######################
# go to directory
#if project_path[len(project_path)-1] != '/': 
#    project_path = project_path + '/'

#os.chdir(project_path + '%s-analysis/sg_ouss_id/group_ouss_id/member_ouss_id/calibrated' % alias)
def openFile():
    import stat
    if os.path.isfile('imaging_parameters.txt') != True:
        mode = 0666|stat.S_IRUSR
        os.mknod('imaging_parameters.txt', mode)
#    os.system('rm imaging_parameters.txt')
    param = open('imaging_parameters.txt','rw+')
    return param

def fillInfo(p): #pass the whole dictionary
    info = []
    info.append('Project code: ' + p['project_number'] + '\n')
    info.append('SB name: ' + p['SB_name'] + '\n')
    info.append('PI name: ' + p['PI_name'] + '\n')
    info.append('Project title: ' + p['title'] +'\n \n')

    info.append('You have ' + str(p['nms']) + ' ms with these frequency properties: \n')
    for line in p['specinfo']:
        for a in line:
            info.append(a)  # print the relevant lines from listobs

    #! print science field(s) somewhere
    info.append('This is ' + p['mosaic'] + ' a mosaic ' + p['pointings'] +'\n')
    info.append('The phasecenter coordinates are: ' + p['phasecenter'])
    info.append('The science field indexes are: ' + p['scifields'] + '\n') # print science field(s) somewhere
    info.append('Recommended cell and image sizes are: \n' + p['cellsize'] + '	' + '[' + p['imsize'] + ',' + p['imsize'] + '] \n')

    info.append('\n')
    info.append('Velocity parameters are: '+ '\n')
    info.append('Rest frame: ' +p['rframe'] + '\n')
    info.append('Representative frequency: ' + p['rfreq']+ ' GHz \n')
    info.append('Width for sensitivity: ' + str(p['rwidth']) + ' ' + p['rwidthunit'] + ' or ' + str(p['vwidth']) + ' m/s'+ '\n')  #fix the unit

    info.append('Transitions, number of channels, and rest frequencies (GHz) for spws: '+ '\n')
    
    for n in range(0,len(p['spw_dict'])):
        info.append(p['spw_dict'][n]['transition'] + '      ' + p['spw_dict'][n]['nchan']+ '	'+ p['spw_dict'][n]['restfreq'] + '\n') 

    info.append('\n')
    #info.append('Here are some plotms commands to help you find the appropriate start velocity and number of channels: '+ '\n')
    #for n in range(0,len(p['plotcmd'])):
    #    info.append(p['plotcmd'][n]+ '\n')

    info.append('\n')
    info.append('Try to meet the requested line rms of ' + p['rms'] + ' '+ p['rms_unit'])
    return info

def writeText(param, info):
    param.writelines(info)
    param.close()

#######################

def main(SB_name = False, project_path = False): 
    if project_path == False:
        project_path = os.getcwd()
    dictionaries = project_info.most_info(SBname = SB_name, project_path = project_path)
    OT_dict = dictionaries[1]
    project_dict = dictionaries[0]
    #readme_info = fill_README.getInfo(dictionaries[0], OT_dict)
    XMLroots=OT_dict[1]
    science_root = XMLroots['science_root']
    namespaces = XMLroots['namespaces']

    nms = getnum_ms(project_dict['project_type'],project_dict['project_path'])
    #IPython.embed()
    listobs = getListobs()
    line = listobs[0]
    index = listobs[1]
    nspws = getNspw(line, index)
    cell = getCell(line)
    scifld = getScienceFields(line, index)
    specinfo = getLines(index, int(nspws[0]))
    spwinfo = getSpwInfo(science_root, namespaces, nspws[1])
    rfreqHz = getRestFreq(science_root, namespaces)
    vwidth = getVelWidth(science_root, namespaces, rfreqHz=rfreqHz)
    rframe = getRefFrame(science_root, namespaces)
    #plotcmd = genPlotMS(spwinfo, rframe)
    plotcmd = ''
    sg = OT_dict[0]
    sName = sourceName(science_root, namespaces, project_dict['SB_name'])
    mbool = mosaicBool(namespaces, science_root, sName)
    mosaic = ismosaic(mbool, scifld[0], scifld[scifld.rfind(' ')-1:])
    if mbool == 'true':
        pc = getPhasecenter(science_root, namespaces)
    else: 
        pc = 'N/A'
    # get stuff from readme
    readme_dict = fill_README.getInfo(dictionaries[0], OT_dict)

    # fill dictionary
    parameters = {'project_number': project_dict['project_number'],'SB_name': project_dict['SB_name'],'PI_name': readme_dict['PI_name'],'title': readme_dict['title'],'nms':nms, 'specinfo':specinfo,'mosaic': mosaic[0], 'pointings': mosaic[1], 'scifields': scifld, 'scifield0': scifld[0], 'scifield1': scifld[scifld.rfind(' ')-1:], 'cellsize': cell[0], 'imsize':cell[1], 'rframe':rframe,  'vwidth':vwidth[0], 'rwidth': vwidth[1], 'rwidthunit': vwidth[2], 'spw_dict': spwinfo, 'plotcmd': plotcmd, 'rms': readme_dict['rms'], 'rms_unit': readme_dict['rms_unit'], 'rfreq':str(float(rfreqHz)*1e-9), 'phasecenter': pc}
    param = openFile()
    info = fillInfo(parameters) #! re-work this one too
    writeText(param, info)
    print 'The file imaging_parameters.txt is now in %s' % os.getcwd()
    # remove temp files
    fill_README.cleanup(OT_dict[0]['tempdir'])   

if __name__ == "__main__":
    main()

