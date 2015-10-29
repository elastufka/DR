# TO DO:
# add commands that write stuff to readme (DA version only)
# do regrid, contsub, selfcal sections
# incorporate commands to find where the lines/continuum are (or should this be a separate script?)
# see if stripping the commands and comments from Amanda's code can be done and utilized in a reliable fashion
# Include Brian Mason's commands for making masks (DA version only)
# interactive script wrapper that writes and runs the script one piece at a time? Then can do the continuum and mask making parts more easily....
# make error messages ...

#######################################
# script_generator.py
# Erica Lastufka 08/20/2015 

#Description: Generates a basic custom imaging script. WIP.
#######################################

#######################################
# Usage:
#	execfile("script_generator.py") 
#           or 
#       import script_generator as sg
#       sg.generate('SB_name','project_directory')

# or....
# from dr import script_generator as sg # all the relevant stuff
# sg.generate('SB_name','project_directory')
#########################################

#########################################
# functions: 

#	get_parameters(project_dict=False, OT_dict=False)
#	    gets the parameter dictionary from list_imparameters.py


# command definition functions:
#	check_casa():
#	    defines commands that check the CASA version

# script generation functions:
#	script_data_prep(parameters)
#	    write the data prepration portion of the script

#	make_continuum(script, parameters, project_dict)
#	    write the data prepration portion of the script

#	image_setup(script,parameters)
#	    write the imaging control parameters portion of the script

#	cont_image(script,parameters)
#	    write the portion of the script that makes the continuum image

#	contsub(script,parameters)
#	    write the continuum subtraction portion of the script

#	line_image(script,parameters)
#	    write the portion of the script that makes the line images

#	pbcor_fits(script)
#	    write the portion of the script that does the primary beam correction and exports the files to fits

#	write_script(script, project_dict)
#	    write the script to scriptForImaging.py

#	main(project_dict = False, OT_dict = False)
#	    Used in conjunction with mypre_imaging.py or when you want to manually input project info

#	final_main(SB_name, project_path)
#	    For generating the script. If AOT file is not in the project directory, will query the user for it. mous_code option currently for use with manual calibration data. 

#	generate(SB_name, project_path)
#	    identical to final_main ... want this to be the final name of the function that is called 

#########################################
import glob
import IPython
import os
import sys

import list_imparameters as li
import project_info as pi
import OT_info
import comments as com
import static_commands as sc

#####################
# get the parameter dictionary
#####################

def get_parameters(project_dict=False, OT_dict=False):
    if project_dict == False:
        project_dict = pi.main()
    if OT_dict == False:
	OT_dict = OT_info.getOTinfo(project_dict['SB_name'])
    XMLroots=OT_dict[1]
    science_root = XMLroots['science_root']
    namespaces = XMLroots['namespaces']
    nms = li.getnum_ms(project_dict['project_type'], project_dict['project_path'])
    listobs = li.getListobs()
    line = listobs[0]
    index = listobs[1]
    nspws = li.getNspw(line, index)
    cell = li.getCell(line)
    scifld = li.getScienceFields(line, index)
    specinfo = li.getLines(index, int(nspws[0]))
    spwdict = li.getSpwInfo(science_root, namespaces, nspws[1])
    rfreqHz = li.getRestFreq(science_root, namespaces)
    vwidth = li.getVelWidth(science_root, namespaces, rfreqHz=rfreqHz)
    rframe = li.getRefFrame(science_root, namespaces)
    sg = OT_dict[0]
    AOT = OT_dict[0]['AOT']
    sName = li.sourceName(science_root, namespaces, project_dict['SB_name'])
    #mosaic = li.mosaicBool(namespaces, XMLroots['proj_root'], sg['science_goal'])
    mosaic = li.mosaicBool(namespaces, XMLroots['science_root'], sName)
    if mosaic == 'true':
        pc = li.getPhasecenter(science_root, namespaces)
    else: 
        pc = 'N/A'

    # fill dictionary
    pc = li.getPhasecenter(science_root, namespaces)
    lastfield = scifld[scifld.rfind(' ')-1:]

    parameters = {'project_number': project_dict['project_number'],'SB_name': project_dict['SB_name'],'nms':nms, 'specinfo':specinfo,'mosaic': mosaic, 'scifields': scifld,'scifield0': scifld[0], 'scifield1': lastfield, 'cellsize': cell[0], 'imsize':cell[1], 'rframe':rframe, 'vwidth':vwidth[0], 'rwidth': vwidth[1], 'rwidthunit': vwidth[2], 'spw_dict': spwdict, 'rfreq':str(float(rfreqHz)*1e-9), 'plotcmd': '', 'sourceName': sName, 'phasecenter': pc, 'AOT': AOT}
    return parameters

#########################################
# deal with all the spw nonsense at once
#########################################

def sort_spws(parameters): 
    # fix the indices if the project contains multiple ms's or was combined earlier:
    try:
        os.chdir('Imaging')
        if os.path.isdir('calibrated.ms') == True:
            os.chdir('../')
            calfolders = glob.glob('Calibration*')
            factor = len(calfolders)
            os.chdir('Imaging')
            spw_per_eb = len(parameters['spw_dict'])/factor # number of spws in each ms that was combined
            parameters['spw_dict'] = parameters['spw_dict'][0:spw_per_eb] # shorten the dictionary if it was a calibrated.ms
    except OSError:
        if parameters['nms'] > 1: 
            factor = parameters['nms']
            spw_per_eb = len(parameters['spw_dict'])

    # now fix the indices if you need to
    try:
        if factor:
            for n in range(0,spw_per_eb):
                indices = [n]
                nchan = (parameters['spw_dict'][n]['nchan'])
                for i in range(1, factor): # because starting at 0 gives you 0, 0, 4 etc 
                    indices.append(n + i*(spw_per_eb))
                parameters['spw_dict'][n]['index'] = ','.join(map(str,indices))
    except UnboundLocalError:
        for n in range(0, len(parameters['spw_dict'])): 
            parameters['spw_dict'][n]['index'] = str(parameters['spw_dict'][n]['index']) # make them strings because types

    contspws = []
    width = []
    widthall = []
    spwall = []
    linespw = []
    lineinfo = []

    for n in range(0,len(parameters['spw_dict'])): #nspws:
        if parameters['spw_dict'][n]['transition'] == 'Manual_window':
            manual_window = raw_input('Spw %s is designated as a manual window. Please look at the proposal to determine if it should be treated as a line or continuum spw. If you would like to treat it as a line window, please enter the transition if possible. Otherwise, type "line". If you would like to treat it as continuum, please type "continuum" or press enter.' % str(n)) or 'continuum' 
            if manual_window == 'continuum':
                parameters['spw_dict'][n]['transition'] = 'continuum'
            else:
                parameters['spw_dict'][n]['transition'] = manual_window # in this case it should be treated as a line window when we get around to generating the line imaging commands

    for n in range(0,len(parameters['spw_dict'])): # now that any undefined windows are dealt with, find out what spws are continuum and the number of channels in them
        if parameters['spw_dict'][n]['transition'] == 'continuum':
            contspws.append(parameters['spw_dict'][n]['index'])
            width.append(parameters['spw_dict'][n]['nchan'])  
        else: # uvcontsub will change line indices... so deal with this here.
            transname = "linename = '" + parameters['spw_dict'][n]['transition'] +"'\n"
            #print i, len(parameters['spw_dict']), parameters['spw_dict'][n]['transition']
            spw_index = parameters['spw_dict'][n]['index']
            lineinfo.append({'spw_index': spw_index, 'restfreq': parameters['spw_dict'][n]['restfreq'], 'plotcmd': '', 'transition': transname})
        spwall.append(parameters['spw_dict'][n]['index'])
        widthall.append(parameters['spw_dict'][n]['nchan'])

    #nasty string operations
    width = ', '.join(map(str, width))
    widthall = ', '.join(map(str, widthall))
    contspws = ', '.join(map(str, contspws))

    if ',' in contspws: # more than 0 or 1 continuum spws
        contspws = map(int,contspws.split(','))
        contspws = sorted(contspws, key = int)    
        contspws = ', '.join(map(str, contspws))
    else:
        contspws = '' # make it a string because types

    spwall = ', '.join(map(str, spwall))
    spwall = map(int,spwall.split(','))
    spwall = sorted(spwall, key = int)
    spwall = ', '.join(map(str, spwall))

    for n in range(0, len(lineinfo)):
        try:
            linespw = linespw + map(int, lineinfo[n]['spw_index'].split(',')) 
        except AttributeError:
            linespw = linespw + [lineinfo[n]['spw_index']] 
    linespw = sorted(linespw, key = int)
    linespw = ', '.join(map(str, linespw)) 
    linespw = "linespw = '" + linespw + "'\n" # this is the line you feed into uvcontsub as the list of spws to do subtraction on.

    if (parameters['nms'] > 1 or os.path.isdir('calibrated.ms') == True): # if multiple executions, need to fix widths 
        width0 = width
        widthall0 = widthall
        for n in range(0, factor-1):
            width = width + ',' + width0 
            widthall = widthall + ',' + widthall0

    if (contspws != '' or contspws != spwall): # continuum subtraction is going to change the indices so fix them here. Yay.
        line_spws_per_eb = len(lineinfo) #line spws per eb

        for n in range(0, len(lineinfo)):
            lineinfo[n]['spw_index'] = str(n) # do something clever
            try:
                if factor: #multiple eb's ... this might be an unbound local error in case of single eb, test.
                    for j in range(1, factor):
                        lineinfo[n]['spw_index'] = lineinfo[n]['spw_index'] + ',' + str(n + line_spws_per_eb*j)
            except UnboundLocalError:
                pass
            # update plotms commands
            lineinfo[n]['plotcmd'] = li.genPlotMS(lineinfo[n], parameters['rframe'], lineinfo[n]['spw_index'])
            lineinfo[n]['restfreq'] = "restfreq = '" + lineinfo[n]['restfreq'] + "GHz'\n"

    continfo = {'cont_index': contspws, 'width': width, 'widthall': widthall, 'spwall': spwall}

    return continfo, lineinfo, linespw

#########################################
# fill in the script
#########################################

def script_data_prep(parameters, project_dict, comments):

    # some short commands we'll need:
    singleex = "concatvis = vislist[0]\n"
    multipleex = "concatvis='calibrated.ms'\n"
    vishead = "vishead(vis=concatvis)\n"

    noregrid = "os.system('mv -i ' + sourcevis + ' ' + 'calibrated_final.ms')\n"
    regrid = "os.system('mv -i ' + regridvis + ' ' + 'calibrated_final.ms')\n"

    backup = "os.system('cp -ir calibrated_final.ms calibrated_final.ms.backup')\n\n"

    if comments == False:
        script = com.header_brief() + sc.check_casa(project_dict) + com.glob_list() + sc.get_vislist(project_dict)
    else:
        script = com.header() + sc.check_casa(project_dict) + com.glob_list()  + sc.get_vislist(project_dict)

    if parameters['mosaic'] == 'true': # remove pointing tables if mosaic
        script = script + com.pointing() + sc.pointing_table()

    # to concat or not concat?
    if project_dict['project_type'] == 'Imaging' and parameters['nms'] > 1:
        if comments == False: 
            script = script + com.combine_header() + sc.concat_setup() +com.split()  + multipleex + vishead + sc.split_science() + sc.checksplit() 
        else:
            script = script + com.combine() + sc.concat_setup() +com.split() +  multipleex + vishead + com.vishead() + sc.split_science() + com.check_split() + sc.checksplit() 
    else:
        if comments == False:
            script = script + com.split() + singleex + vishead + sc.split_science() + sc.checksplit() 
        else:
             script = script + com.split() + singleex + vishead + com.vishead() + sc.split_science() + com.check_split() + sc.checksplit() 
  
    os.chdir(project_dict['project_path'])
    if project_dict['project_type'] == 'Manual':
        os.chdir('Imaging')
        if  os.path.isdir('calibrated.ms') == True: # need concatvis = 'calibrated.ms' but no split
            if comments == False: 
                script = script + com.split() + multipleex + vishead + sc.split_science() + sc.checksplit() 
            else:
                script = script + com.split()+ multipleex + vishead + com.vishead() + sc.split_science() + com.check_split() + sc.checksplit() 
        else:
            if comments == False:
                script = script + com.split() + singleex + vishead + sc.split_science() + sc.checksplit() 
            else:
                 script = script + com.split() + singleex + vishead + com.vishead() + sc.split_science() + com.check_split() + sc.checksplit() 
        os.chdir('../')
  
    #if you need to regrid your velocities... build this in later

    script = script + com.backup() + noregrid + backup
    return script

def make_continuum(script, parameters, project_dict, continfo, comments, flagchannels=False):
    width = continfo['width']
    widthall = continfo['widthall']
    if continfo['cont_index'] == continfo['spwall']:
        contspws = "contspws = '" + continfo['cont_index'] + "' # Because there are no continuum-dedicated spws, all of the spws are included. You will need to flag out line emission before proceeding. \n\n"
        width=widthall
    else:
        contspws = "contspws = '" + continfo['cont_index'] + "'\n"
        width=widthall
    spwall = continfo['spwall']

    if comments == False:
        script =  script + com.im_template_header() + sc.finalvis() + sc.plotspw()
    else:
        script =  script + com.im_template() + sc.finalvis() + sc.plotspw()

    if not flagchannels:
        flagchannels = "flagchannels = '0'\n\n"
        splitcomplete = sc.splitcont()  + "      width=[" + width + "], # widths for all the spws are [" + widthall + "]\n      datacolumn='data')\n\n"
    else: # use all the spws, not just continuum-dedicated:
        flagchannels = "flagchannels = '" + flagchannels + "'\n\n"
        contspws = "contspws = '" + spwall + "\n"
        splitcomplete = sc.splitcont()  + "      width=[" + widthall + "], # widths for all the spws are [" + widthall + "]\n      datacolumn='data')\n\n"

    # 4.4 fixes....
    if project_dict['project_type'] == 'Manual':
        initweights = "initweights(vis=finalvis,wtmode='weight',dowtsp=True)\n\n"
        splitcomplete = sc.splitcont2() + "      width=[" + width + "], # widths for all the spws are [" + widthall + "]\n      datacolumn='data')\n\n"
        checkweights = "plotms(vis=contvis, yaxis='wtsp',xaxis='freq',spw='',antenna='DA42',field='%s')\n" % parameters['scifield0'] # how to get the antenna?
        script = script + contspws + initweights + sc.flags() + flagchannels + sc.flagdata() + sc.plotspw() + sc.contvis() + splitcomplete + sc.flagrestore() + checkweights + sc.plotuv()
    else:
        script = script + contspws + sc.flags() + flagchannels + sc.flagdata() + sc.contvis() + splitcomplete + sc.flagrestore() + sc.plotuv()


    return script

def image_setup(script,parameters, comments):
    weights = "weighting = 'briggs'\nrobust=0.5\nniter=1000\nthreshold = '0.0mJy'\n"

    if len(parameters['scifields']) == 1:
        field = "field = '" + parameters['scifield0'] + "'\n"
    else:
        field = "field = '" + parameters['scifields'] + "'\n"
    if parameters['mosaic'] == 'true':
        imgmode = "imagermode='mosaic'\n"
	phasec = "phasecenter='" + parameters['phasecenter'] +"'\n" 
        imgmode = imgmode + phasec
        field = "field = '" + parameters['scifield0'] + "~" + parameters['scifield1']+ "'\n"
    else:
	imgmode = "imagermode='csclean'\n"

    cell = "cell='" + parameters['cellsize'] + "'\n" # cell size for imaging.
    imsize = 'imsize =' + '[' + parameters['imsize'] + ',' + parameters['imsize'] + '] \n'

    if comments == False:
         script = script + com.source_param_header() + field + imgmode + cell + imsize + weights
    else:
       script = script + com.source_param() + field + imgmode+ com.cellcalc() + cell + imsize + com.imcontrol() + weights
  
    return script

def cont_image(script,parameters, comments, mask = False): # what about multiple targets in one SB?
    if parameters['mosaic'] == 'true':
        if not mask:
            clean = sc.mosaic_cont_clean()
        else: 
            clean = sc.mosaic_cont_clean_mask()
    else:
        if not mask:
            clean = sc.single_cont_clean()
        else: 
            clean = sc.single_cont_clean_mask()

    if comments == False:
        script = script + com.im_cont_header() + sc.contvis() + sc.contimagename() + sc.rmtables() + clean
    else:
        script = script + com.im_cont() + sc.contvis() + sc.contimagename() + sc.rmtables() + clean + com.cont_rms()
    return script

def contsub(script,parameters, continfo, linespw, comments, fitspw = False): # this is going to change all your spw indices if you do it...

    finalvis = "finalvis='calibrated_final.ms'\n"
    
    uvcontsub = "uvcontsub(vis=finalvis,\n\
          spw=linespw, # spw to do continuum subtraction on\n\
          fitspw=fitspw, # select spws to fit continuum. exclude regions with strong lines.\n\
          combine='spw', \n\
          solint='int',\n\
          fitorder=1,\n\
          want_cont=False) # This value should not be changed.\n\n"

    if fitspw:
        fitspw = "fitspw = '" + fitspw + "'\n"
    else:
        fitspw = "fitspw ='" + continfo['spwall'] + "' # example only\n\n" # should I put contspws here?

    if comments == False:
        script = script + com.contsub_header() + finalvis +linespw + fitspw + uvcontsub
    else:
        script = script + com.contsub() + finalvis +linespw + fitspw + uvcontsub
    return script


def line_image(script,parameters, lineinfo, comments):# what about multiple targets in one SB?
    # some short commands
    finalv="finalvis = 'calibrated_final.ms'\n"
    linev = "linevis = finalvis + '.contsub'\n" 
    sname = "sourcename ='" + parameters['sourceName'] + "'\n" 
    lineim = "lineimagename = sourcename+'_'+linename+'_image' # name of line image\n"
  
    vparam = "start =''\n\
width='" + str(parameters['vwidth']) + "m/s' \n\
nchan = -1  \n\
outframe='" + parameters['rframe'] +"' \n\
veltype='radio'\n\n"

    if parameters['mosaic'] == 'true':
        lineclean = sc.mosaic_line_clean()
    else:
        lineclean = sc.single_line_clean()
    if comments == False:
        script = script + com.im_line_header()+ finalv + linev + sname
    else:
        script = script + com.im_line() + finalv + linev + sname
 
    #for as many lines as there are, do this:
    for n in range(0,len(lineinfo)):
        if comments == False:
            script = script + lineinfo[n]['transition'] + "spw = '" + lineinfo[n]['spw_index']+ "'\n" + lineim + lineinfo[n]['restfreq'] + lineinfo[n]['plotcmd'] + '\n\n' + vparam + sc.rmtablesline() + lineclean
        else:
            script = script + lineinfo[n]['transition'] + "spw = '" + lineinfo[n]['spw_index']+ "'\n" + lineim + lineinfo[n]['restfreq'] + com.velparam()+ lineinfo[n]['plotcmd']  + '\n\n' + vparam + com.veltype() + com.line_cvel() + sc.rmtablesline() + lineclean + com.line_rms() 
 
    return script

def pbcor_fits(script):
    script = script + com.pbcor() + sc.pbcor() + com.export() + sc.fits() + com.analysis()
    return script

###################################
# write the script
####################################

def write_script(script, project_dict, filename=False):
    import stat
    #os.chdir("/lustre/naasc/elastufk/Imaging/test/") #script directory ... /calibrated or Imaging/
    project_path = project_dict['project_path']
    os.chdir(project_path)
    if project_dict['project_type'] == 'Imaging':
        os.chdir('sg_ouss_id/group_ouss_id/member_ouss_id/calibrated/')
    else:
        os.chdir('Imaging/')
    if not filename:
        if os.path.isfile('scriptForImaging.py') == False:
            mode = 0666|stat.S_IRUSR
            os.mknod('scriptForImaging.py', mode)
        filename = 'scriptForImaging.py'

    imscript = open(filename, 'w')
    imscript.writelines(script)
    imscript.close()
    print '\n\nYour custom ' + filename + ' is in ' + os.getcwd()

# main method
def generate(SB_name, project_path = False, comments = True):
    if project_path == False:
        project_path = os.getcwd()    
    dictionaries = pi.most_info(SB_name, project_path=project_path)    
    project_dict = dictionaries[0]
    OT_dict = dictionaries[1]
    os.chdir(project_path)
    parameters = get_parameters(project_dict = project_dict, OT_dict = OT_dict) 
    script = script_data_prep(parameters, project_dict, comments)
    spws = sort_spws(parameters)
    continfo = spws[0]
    lineinfo = spws[1]
    linespws = spws[2]
    script = make_continuum(script,parameters, project_dict, continfo, comments, flagchannels=False)
    script = image_setup(script,parameters, comments)
    script = cont_image(script,parameters, comments)
    if lineinfo != []:
        script = contsub(script,parameters, continfo, linespws, comments)
        script = line_image(script,parameters, lineinfo, comments)
    script = pbcor_fits(script)
    write_script(script,project_dict, filename = 'scriptForImaging_test.py')
    # cleanup temp files
    OT_info.cleanup(parameters['AOT'])

# FOR TESTING ONLY
if __name__ == "__main__":
    generate('NGC_1068_a_07_TE','/lustre/naasc/elastufk/Reduce_00014', comments = False)

