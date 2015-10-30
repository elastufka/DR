#######################################
# readme_comments.py
# Erica Lastufka 08/20/2015 

#Description: Generates sentences that will be written to readme, based on the script. Comments beginning with #README, #readme, or #R will be written to the readme and then erased by my_strip_instructions.py
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

#######################################
import IPython

def projecttype(): # get type from folders
   import os
   pwd =os.getcwd()
   if pwd.find('calibrated') != -1:
      ptype = "The data was calibrated using the pipeline version [insert version here]."
   else:
      ptype = 'The data was calibrated manually.'
   return ptype

def fluxcal(): # if scriptForFluxCalibration exists, print this...
    fluxcal = 'Additional flagging was necessary because of [reason]. These flagging commands, in scriptForFluxCalibration.py, were executed before the rest of the imaging process.'
    return fluxcal     

def combined():
    import glob
    import os
    if glob.glob('*.ms.split.cal') != []:
        nms = len(glob.glob('*.ms.split.cal'))
    else:
        os.chdir('../')
        nms = len(glob.glob('Calibration*'))        
        os.chdir('Imaging')
    combined = "Data from the %s executions was combined using the concat() command." % str(nms)
    return combined

def regrid():
    regrid = 'you regridded using cvel'
    return regrid

def cont_flag_reason(line):
    # if there's a comment about why things in the continuum were flagged
    cont_flag_reason = 'Select channels in the continuum were flagged due to %s.' % line[11:]
    return cont_flag_reason 

def contimage():
    contimage = 'The continuum image had'
    return contimage

def weighting(line1, line2):
    if line1 != 'weighting=weighting':
        if (line1.find('Briggs') != -1 or line1.find('briggs') != -1):
            weighting = "The image was made using %s weighting with a robustness of %s. " % (line1[line1.find('=')+3:-2], line2[line2.find('=')+1:-1])
        else:
            weighting = "The image was made using %s weighting. " % line1[line1.find('=')+2:-1]
    return weighting

def linewidth(lines):
    l=lines[0]
    l=l[l.find("'")+1:l.rfind("'")] # this is the line name
    for line in lines[1:]:
        if (line.startswith("width") and line.find('width=width') ==-1):
            w = line[line.find("'")+1:line.rfind("'")]
            width = 'The %s line was imaged with a velocity width of %s. It had ' % (l,w)
            break
        else:
            width = ''
    #width = 'The %s line was imaged with a velocity width of %s. It had ' % (l,w)
    return width

def selfcal(lines,lindex): # if selfcal was used - only gets the final rms and niter
    segment = lines[lindex: lindex + 290] # length of the section is  291 lines with comments
    selfcal = "The continuum was bright enough to attempt self-calibration. The final image had "
    segment.reverse()
    for bit in segment:
        if '#R' in bit:
            selfcal = selfcal + processline(bit)
            break
    return selfcal

def contsub():
    contsub = "After continuum subtraction, the lines were imaged using the same parameters. "
    return contsub 

def line_selfcal(): # if selfcal was used
    line_selfcal = "The self-calibration was applied to the line spectral windows to acheive better quality. "
    return line_selfcal

def QA2semipass(): # print this if it's a QA2 semipass
     QA2semipass= "This project was declared QA2 SEMIPASS, meaning that it did not meet the PI requested performance parameters but is being delivered anyway. The reason for the early delivery is [insert reason here]. "
     return QA2semipass

def DRlimited(): # print this if it's dynamic range limited
    DRlimited = "The image is dynamic range limited , meaning that [whatever it means]. "
    return DRlimited

def processline(line):
    line = line[2:] # get rid of #R
    rfunctions=[QA2semipass(),DRlimited()]
    keywords=['QA2_SEMIPASS','DR_LIMITED']
    for n in range(0,len(rfunctions)):
        if keywords[n] in line:
            newline = rfunctions[n]
        try: 
            if newline:
                pass
        except NameError:
            if line.find('FLAGREASON') != -1:
                newline=cont_flag_reason(line[:-1])
            elif line.find('rms') != -1:
                newline=' a rms of %s after %s clean iterations.' % (line[line.rfind('s')+1:-1], line[0:line.find(',')]) # assume either 'the continuum image' or 'the XX line image' proceeds this.
            else: # just print the line
                newline=line[:-1] # get rid of the \n on the end
    return newline

def beamsize(): # gets beamsizes
    import glob
    images = glob.glob('*.image') # treat continuum image separately
    for image in images:
        imhead(image, mode = 'get', hdkey='bmaj') # make this work in casa ... or find one of todd's things that does what i want
        beamsize = 'blah'
    return beamsize

def strip_all_instructions(keywords, infilename): #slight modification of Amanda's script
    
    import shutil
    import os.path

    backupfilename = infilename + '.backup'

    if os.path.isfile(backupfilename):
        print "Backup file exists! Stopping."
        return
    else:
        print "Moving " + infilename + " to " + backupfilename +"."
        shutil.move(infilename,backupfilename)
        outfilename = infilename
        infilename = backupfilename
         
    infile = open(infilename,'r')
    outfile = open(outfilename, 'w')

    print "Stripping instructions and replacing #R with #"
    for line in infile:
       if line.startswith('#>>>'):
            continue
       elif line.startswith('#R'):
           for n in range(0,len(keywords)):
                if line.find(keywords[n]) != -1:
                    break
           else:           
               line = '#' + line[2:]
               outfile.write(line)
       else:
           outfile.write(line)

    infile.close()
    outfile.close()

def readme_comments():
    import os
    #main method
    #get section headers and #R comments from scriptForImaging
    headers=['Combining Measurement Sets','Regridding spectral windows','Imaging the Continuuum','Continuum Subtraction for Line Imaging', 'Apply continuum self-calibration to line data'] 
    functions = [combined(), regrid(), contimage(), contsub(), line_selfcal()]
    selfcalstuff = 'Self-calibration on the continuum'# selfcal is special, separate section for that?

    text = projecttype()
    if os.path.isfile('scriptForFluxCalibration.py'):
        text = text + fluxcal()
    script = open('scriptForImaging.py','r')
    lines = script.readlines()

    lindex=0
    for line in lines:
        try:
            for n in range(0, len(headers)):
                if headers[n] in line: #this doesn't work for some reason
                    #print headers[n], functions[n]
                    text=text+functions[n] 
                    break
            if (lines[lindex].find('weighting') != -1 and lines[lindex].find('weighting=weighting') == -1 and lines[lindex].find('weighting = weighting') == -1):
                text = text + weighting(lines[lindex], lines[lindex+1])
            elif lines[lindex].startswith('linename') == True: # and lines[lindex+1].startswith('nchan') == False):
                #get next 20 lines just in case...
                text = text + linewidth(lines[lindex:lindex+20])
            elif '#R' in lines[lindex]:
                newline =processline(lines[lindex])
                text = text + newline  
            elif lines[lindex].find(selfcalstuff) !=-1:
                text = text + selfcal(lines,lindex)
                lindex = lindex + 290
                # get that whole section and deal with it   
        except IndexError:
            break
        lindex = lindex + 1
    text = text + '\n'
    print text

    # write to readme
    if os.path.isfile('README.header.txt') != True:
       os.chdir('../') # it's an imaging project
       #os.system('cp -i /users/thunter/AIV/science/qa2/README.header.cycle2.txt README.header.txt')
    readme = open('README.header.txt','r') 
    readme.close
    rinfo = readme.readlines()
    rinfo[13] = text
    readme.writelines(rinfo)
    os.mknod('readme.txt')
    readmenew = open('readme.txt', 'w')
    
    readmenew.writelines(rinfo) # why doesn't this write???
    readmenew.close()
    os.system('mv -f readme.txt README.header.txt') #don't know why I have to do all this...
    os.system('chmod 666 README.header.txt')
 
    # strip instructions and #R 's
    try:
        os.chdir('calibrated')
    except OSError:
        pass
    keywords=['QA2_SEMIPASS','DR_LIMITED', 'FLAGREASON']
    strip_all_instructions(keywords, 'scriptForImaging.py')

