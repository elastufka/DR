#######################################
# static_commands.py
# Erica Lastufka 09/23/2015 

#Description: Contains the imaging script commands that don't change

#########################################
# functions: 

#	check_casa():
#	    defines commands that check the CASA version

#	get_vislist()
#	    defines commands that get the list of visibilities

#	pointing_table()
#	    defines commands that remove the pointing table

#	concat_setup()
#	    defines commands that run concat

#	split_science()
#	    defines commands that split out science data

#	checksplit()
#	    defines commands that check that the split worked correctly

#	finalvis()
#	    defines commands that define finalvis

#	plotspw()
#	    defines commands that plot amp v. channel for each spw

#	plotamp()
#	    defines commands that plot amp v channel

#	contvis()
#	    defines commands that defines contvis

#	splitcont()
#	    defines commands that create the continuum ms

#	splitcont2()
#	    defines commands that create the continuum ms for 4.4 reductions

#	plotuv()
#	    defines commands that plots amp v uvdist

#	flagrestore()
#	    defines commands that restores flag versions

#	contimagename()
#	    defines commands that defines continuum image name

#	rmtables()
#	    defines commands that deletes tables for continuum image

#	rmtablesline()
#	    defines commands that deletes tables for line image

#	mosaic_cont_clean()
#	    defines commands that cleans a continuum mosaic

#	single_cont_clean()
#	    defines commands that cleans a continuum single pointing

#	mosaic_line_clean()
#	    defines commands that cleans a line mosaic

#	single_line_clean()
#	    defines commands that cleans a line single pointing

##################################################################

def check_casa(project_dict): 
    version = project_dict['casa_version']
    version = version[0:3]
    check_casa = "\nimport re \n \nif (re.search('%s', casadef.casa_version))  == None: \n    sys.exit('ERROR: PLEASE USE THE SAME VERSION OF CASA THAT YOU USED FOR GENERATING THE SCRIPT: %s')\n\n" % (version, version)
    return check_casa

def get_vislist(project_dict):
    if project_dict['project_type'] == 'Imaging':
        vislist = "\nimport glob \n \nvislist=glob.glob('*.ms.split.cal')\n\n"
    else:
        import os
        os.chdir(project_dict['project_path'])
        os.chdir('Imaging')
        if os.path.isdir('calibrated.ms') == True:
            vislist = "\nvislist = ['calibrated.ms']\n\n"
        else:
            vislist = "\nimport glob \n \nvislist=glob.glob('*.ms.split.cal')\n\n"
    return vislist

def pointing_table():
    pointing = "\nfor vis in vislist:\n    tb.open( vis + '/POINTING',\n    nomodify = False)\n    a = tb.rownumbers()\n    tb.removerows(a)\n    tb.close()\n\n"
    return pointing

def concat_setup():
    concat = "\nconcatvis='calibrated.ms'\n\nrmtables(concatvis)\nos.system('rm -rf ' + concatvis + '.flagversions')\nconcat(vis=vislist,concatvis=concatvis)\n\n"
    return concat

def split_science():
    split = "sourcevis='calibrated_source.ms'\nrmtables(sourcevis)\nos.system('rm -rf ' + sourcevis + '.flagversions')\n\nsplit(vis=concatvis,\n      intent='*TARGET*', # split off the target sources\n      outputvis=sourcevis,\n      datacolumn='data')\n\n" 
    return split

def checksplit():
    checksplit="vishead(vis=sourcevis)\n"
    return checksplit

def finalvis():
    finalvis = "finalvis='calibrated_final.ms'\n"
    return finalvis

def plotspw():
   plotspw = "plotms(vis=finalvis, xaxis='channel', yaxis='amplitude',\n       ydatacolumn='data',\n       avgtime='1e8', avgscan=True, avgchannel='2', # you should only lightly average over frequency\n       iteraxis='spw' )\n\n"
   return plotspw

def plotamp():
    plotamp = "plotms(vis=finalvis,yaxis='amp',xaxis='channel',\n      avgchannel='2',avgtime='1e8',avgscan=True,iteraxis='spw') \n"
    return plotamp

def contvis():
    contvis = "contvis='calibrated_final_cont.ms'\n"
    return contvis

def splitcont():
    splitcont = "rmtables(contvis) \nos.system('rm -rf ' + contvis + '.flagversions')\nsplit(vis=finalvis,\n      spw=contspws,\n      outputvis=contvis,\n"
    return splitcont

def splitcont2():
    splitcont2 = "rmtables(contvis) \nos.system('rm -rf ' + contvis + '.flagversions')\nsplit2(vis=finalvis,\n      spw=contspws,\n      outputvis=contvis,\n"
    return splitcont2

def flags():
    flags = "flagmanager(vis=finalvis,mode='save',\n            versionname='before_cont_flags')\n"
    return flags

def flagdata():
    flagdata = "flagdata(vis=finalvis,mode='manual',\n          spw=flagchannels,flagbackup=False)\n\n"
    return flagdata

def plotuv():
    plotuv = "plotms(vis=contvis,xaxis='uvdist',yaxis='amp',coloraxis='spw')\n"
    return plotuv 

def flagrestore():
    flagrestore = "flagmanager(vis=finalvis,mode='restore',\n            versionname='before_cont_flags')\n"
    return flagrestore

def contimagename():
    imname = "contimagename = 'calibrated_final_cont_image'\n"
    return imname

def rmtables():
    rmtables = "for ext in ['.flux','.image','.mask','.model','.pbcor','.psf','.residual','.flux.pbcoverage']:\n    rmtables(contimagename+ext)\n\n"
    return rmtables

def rmtablesline():
    rmtablesline = "for ext in ['.flux','.image','.mask','.model','.pbcor','.psf','.residual','.flux.pbcoverage']:\n    rmtables(lineimagename+ext)\n\n"
    return rmtablesline

def mosaic_cont_clean():
    clean = "clean(vis=contvis,\n      imagename=contimagename,\n      field=field,\n      phasecenter=phasecenter,\n      mode='mfs',\n      psfmode='clark',\n      imsize = imsize,\n      cell= cell,\n      weighting = weighting,\n      robust = robust,\n      niter = niter,\n      threshold = threshold,\n      interactive = True,\n      imagermode = imagermode)\n"
    return clean

def single_cont_clean():
    clean = "clean(vis=contvis,\n      imagename=contimagename,\n      field=field,\n      mode='mfs',\n      psfmode='clark',\n      imsize = imsize,\n      cell= cell,\n      weighting = weighting,\n      robust = robust,\n      niter = niter,\n      threshold = threshold,\n      interactive = True,\n      imagermode = imagermode)\n"
    return clean

def mosaic_cont_clean_mask():
    clean = "clean(vis=contvis,\n      imagename=contimagename,\n      field=field,\n      phasecenter=phasecenter,\n      mode='mfs',\n      psfmode='clark',\n      imsize = imsize,\n      cell= cell,\n      weighting = weighting,\n      robust = robust,\n      niter = niter,\n      threshold = threshold,\n      interactive = True,\n      imagermode = imagermode,\n      mask = 'contDirtyMask')\n"
    return clean

def single_cont_clean_mask():
    clean = "clean(vis=contvis,\n      imagename=contimagename,\n      field=field,\n      mode='mfs',\n      psfmode='clark',\n      imsize = imsize,\n      cell= cell,\n      weighting = weighting,\n      robust = robust,\n      niter = niter,\n      threshold = threshold,\n      interactive = True,\n      imagermode = imagermode,\n      mask = 'contDirtyMask')\n"
    return clean

def selfcal():
    selfcal = "contvis = 'calibrated_final_cont.ms'\n\
contimagename = 'calibrated_final_cont_image'\n\n\
refant = 'DV09' # reference antenna.\n\n\
spwmap = [0,0,0] # mapping self-calibration solutions to individual spectral windows. Generally an array of n zeroes, where n is the number of spectral windows in the data sets.\n\n\
# shallow clean on the continuum\n\n\
for ext in ['.flux','.image','.mask','.model','.pbcor','.psf','.residual','.flux.pbcoverage']:\n\
    rmtables(contimagename + '_p0'+ ext)\n\n\
clean(vis=contvis,\n\
      imagename=contimagename + '_p0',\n\
      field=field,\n\
#      phasecenter=phasecenter, # uncomment if mosaic.\n\
      mode='mfs',\n\
      psfmode='clark',\n\
      imsize = imsize, \n\
      cell= cell, \n\
      weighting = weighting, \n\
      robust=robust,\n\
      niter=niter, \n\
      threshold=threshold, \n\
      interactive=True,\n\
      usescratch=True, # needed for 4.3 and 4.4 (and maybe 4.5)\n\
      imagermode=imagermode)\n\n\
#>>> Note number of iterations performed.\n\n\
# per scan solution\n\
rmtables('pcal1')\n\
gaincal(vis=contvis,\n\
        caltable='pcal1',\n\
        field=field,\n\
        gaintype='T',\n\
        refant=refant, \n\
        calmode='p',\n\
        combine='spw', \n\
        solint='inf',\n\
        minsnr=3.0,\n\
        minblperant=6)\n\n\
# Check the solution\n\
plotcal(caltable='pcal1',\n\
        xaxis='time',\n\
        yaxis='phase',\n\
        timerange='',\n\
        iteration='antenna',\n\
        subplot=421,\n\
        plotrange=[0,0,-180,180])\n\n\
# apply the calibration to the data for next round of imaging\n\
applycal(vis=contvis,\n\
         field=field,\n\
         spwmap=spwmap, \n\
         gaintable=['pcal1'],\n\
         gainfield='',\n\
         calwt=F, \n\
         flagbackup=F)\n\n\
# clean deeper\n\
for ext in ['.flux','.image','.mask','.model','.pbcor','.psf','.residual','.flux.pbcoverage']:\n\
    rmtables(contimagename + '_p1'+ ext)\n\n\
clean(vis=contvis,\n\
      field=field,\n\
#      phasecenter=phasecenter, # uncomment if mosaic.\n\
      imagename=contimagename + '_p1',\n\
      mode='mfs',\n\
      psfmode='clark',\n\
      imsize = imsize, \n\
      cell= cell, \n\
      weighting = weighting, \n\
      robust=robust,\n\
      niter=niter, \n\
      threshold=threshold, \n\
      interactive=True,\n\
      usescratch=True, # needed for 4.3 and 4.4 (and maybe 4.5)\n\
      imagermode=imagermode)\n\n\
# Note number of iterations performed.\n\n\
# shorter solution\n\
rmtables('pcal2')\n\
gaincal(vis=contvis,\n\
        field=field,\n\
        caltable='pcal2',\n\
        gaintype='T',\n\
        refant=refant, \n\
        calmode='p',\n\
        combine='spw', \n\
        solint='30.25s', # solint=30.\n\25s gets you five 12m integrations, while solint=50.5s gets you five 7m integration\n\
        minsnr=3.0,\n\
        minblperant=6)\n\n\
# Check the solution\n\
plotcal(caltable='pcal2',\n\
        xaxis='time',\n\
        yaxis='phase',\n\
        timerange='',\n\
        iteration='antenna',\n\
        subplot=421,\n\
        plotrange=[0,0,-180,180])\n\n\
# apply the calibration to the data for next round of imaging\n\
applycal(vis=contvis,\n\
         spwmap=spwmap, \n\
         field=field,\n\
         gaintable=['pcal2'],\n\
         gainfield='',\n\
         calwt=F, \n\
         flagbackup=F)\n\n\
# clean deeper\n\
for ext in ['.flux','.image','.mask','.model','.pbcor','.psf','.residual','.flux.pbcoverage']:\n\
    rmtables(contimagename + '_p2'+ ext)\n\n\
clean(vis=contvis,\n\
      imagename=contimagename + '_p2',\n\
      field=field,\n\
#      phasecenter=phasecenter, # uncomment if mosaic.  \n\
      mode='mfs',\n\
      psfmode='clark',\n\
      imsize = imsize, \n\
      cell= cell, \n\
      weighting = weighting, \n\
      robust=robust,\n\
      niter=niter, \n\
      threshold=threshold, \n\
      interactive=True,\n\
      usescratch=True, # needed for 4.3 and 4.4 (and maybe 4.5)\n\
      imagermode=imagermode)\n\n\
#>>> Note number of iterations performed.\n\n\
# shorter solution\n\
rmtables('pcal3')\n\
gaincal(vis=contvis,\n\
        field=field,\n\
        caltable='pcal3',\n\
        gaintype='T',\n\
        refant=refant, \n\
        calmode='p',\n\
        combine='spw', \n\
        solint='int',\n\
        minsnr=3.0,\n\
        minblperant=6)\n\n\
# Check the solution\n\
plotcal(caltable='pcal3',\n\
        xaxis='time',\n\
        yaxis='phase',\n\
        timerange='',\n\
        iteration='antenna',\n\
        subplot=421,\n\
        plotrange=[0,0,-180,180])\n\n\
# apply the calibration to the data for next round of imaging\n\
applycal(vis=contvis,\n\
         spwmap=spwmap,\n\
         field=field,\n\
         gaintable=['pcal3'],\n\
         gainfield='',\n\
         calwt=F, \n\
         flagbackup=F)\n\n\
# do the amplitude self-calibration.\n\
for ext in ['.flux','.image','.mask','.model','.pbcor','.psf','.residual','.flux.pbcoverage']:\n\
    rmtables(contimagename + '_p3'+ ext)\n\n\
clean(vis=contvis,\n\
      imagename=contimagename + '_p3',\n\
      field=field,\n\
#      phasecenter=phasecenter, # uncomment if mosaic.     \n\
      mode='mfs',\n\
      psfmode='clark',\n\
      imsize = imsize, \n\
      cell= cell, \n\
      weighting = weighting, \n\
      robust=robust,\n\
      niter=niter, \n\
      threshold=threshold, \n\
      interactive=True,\n\
      usescratch=True, # needed for 4.3 and 4.4 (and maybe 4.5)\n\
      imagermode=imagermode)\n\n\
#>>> Note number of iterations performed.\n\n\
rmtables('apcal')\n\
gaincal(vis=contvis,\n\
        field=field,\n\
        caltable='apcal',\n\
        gaintype='T',\n\
        refant=refant,\n\
        calmode='ap',\n\
        combine='spw',\n\
        solint='inf',\n\
        minsnr=3.0,\n\
        minblperant=6,\n\
#        uvrange='>50m', # may need to use to exclude extended emission\n\
        gaintable='pcal3',\n\
        spwmap=spwmap,\n\
        solnorm=True)\n\n\
plotcal(caltable='apcal',\n\
        xaxis='time',\n\
        yaxis='amp',\n\
        timerange='',\n\
        iteration='antenna',\n\
        subplot=421,\n\
        plotrange=[0,0,0.2,1.8])\n\n\
applycal(vis=contvis,\n\
         spwmap=[spwmap,spwmap], # select which spws to apply the solutions for each table\n\
         field=field,\n\
         gaintable=['pcal3','apcal'],\n\
         gainfield='',\n\
         calwt=F,\n\
         flagbackup=F)\n\n\
# Make amplitude and phase self-calibrated image.\n\
for ext in ['.flux','.image','.mask','.model','.pbcor','.psf','.residual','.flux.pbcoverage']:\n\
    rmtables(contimagename + '_ap'+ ext)\n\n\
clean(vis=contvis,\n\
      imagename=contimagename + '_ap',\n\
      field=field, \n\
#      phasecenter=phasecenter, # uncomment if mosaic.  \n\
      mode='mfs',\n\
      psfmode='clark',\n\
      imsize = imsize, \n\\n\
      cell= cell, \n\
      weighting = weighting, \n\
      robust=robust,\n\
      niter=niter, \n\
      threshold=threshold, \n\
      interactive=True,\n\
      usescratch=True, # needed for 4.3 and 4.4 (and maybe 4.5)\n\
      imagermode=imagermode)\n\n\
#>>> Note final RMS and number of clean iterations. Compare the RMS to\n\
#>>> the RMS from the earlier, pre-selfcal image.\n\n\
# Save results of self-cal in a new ms\n\
split(vis=contvis,\n\
      outputvis=contvis+'.selfcal',\n\
      datacolumn='corrected')\n"
    return selfcal

def mosaic_line_clean():
    lineclean = "clean(vis=linevis,\n      imagename=lineimagename,\n      field=field,\n      spw=spw,\n      phasecenter=phasecenter,\n      mode='velocity',\n      start=start,\n      width=width,\n      nchan=nchan,\n      outframe=outframe,\n      veltype=veltype,\n      restfreq=restfreq,\n      imsize = imsize,\n      cell= cell,\n      weighting = weighting,\n      robust = robust,\n      niter = niter,\n      threshold = threshold,\n      interactive = True,\n      imagermode = imagermode)\n"
    return lineclean

def single_line_clean():
    lineclean = "clean(vis=linevis,\n      imagename=lineimagename,\n      field=field,\n      spw=spw,\n      mode='velocity',\n      start=start,\n      width=width,\n      nchan=nchan,\n      outframe=outframe,\n      veltype=veltype,\n      restfreq=restfreq,\n      imsize = imsize,\n      cell= cell,\n      weighting = weighting,\n      robust = robust,\n      niter = niter,\n      threshold = threshold,\n      interactive = True,\n      imagermode = imagermode)\n"
    return lineclean

def pbcor():
    pbcor = "myimages = glob.glob('*.image')\n\
rmtables('*.pbcor')\n\n\
for image in myimages:\n\
    impbcor(imagename=image, pbimage=image.replace('.image','.flux'), outfile = image.replace('.image','.pbcor'))\n\n"
    return pbcor

def fits():
    fits = "myimages = glob.glob('*.image')\n\
for image in myimages:\n\
    exportfits(imagename=image, fitsimage=image+'.fits',overwrite=True)\n\n\
myimages = glob.glob('*.pbcor')\n\
for image in myimages: \n\
    exportfits(imagename=image, fitsimage=image+'.fits',overwrite=True)\n\n\
myimages = glob.glob('*.flux')\n\
for image in myimages:\n\
    exportfits(imagename=image, fitsimage=image+'.fits',overwrite=True)\n\n"
    return fits

