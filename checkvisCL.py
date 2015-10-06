# checkvis.py
# Author: Erica Lastufka
# Date: 19 Feb 2014

# script to check that plots in ms correspond with plots in weblog
# 	- run in directory that also contains your ms with command: execfile('checkvis.py')
# suggestions for improvements welcome!


#get list of ms files

import glob

vislist=glob.glob('*.ms')
print "The ms is/are: "
print '\n'.join(vislist)

def pause():
    print('When you are done with the graphics window,')
    print('quit that window, and')
    user_check=raw_input('press enter to continue script\n')

for num in vislist:
#get fields 
    msmd.open(num)

    targeta=msmd.fieldsforintent('*TARGET*', True)    
    phasea=msmd.fieldsforintent('*PHASE*', True)
    ampa=msmd.fieldsforintent('*AMP*', True)
    bandpassa=msmd.fieldsforintent('*BANDPASS*', True)

    print("Your science target is: " + str(targeta)) 
    print("Your phase calibrator is: " + str(phasea)) 
    print("Your bandpass calibrator is: " + str(bandpassa)) 
    print("Your flux/amplitude calibrator is: " + str(ampa))

    correct=raw_input('Is this correct? (Y/N)' )

    while correct == 'N':

        taskname = 'vishead'
        default()  
        mode = 'get' 
        hdkey = 'field'
        vis=num
        print vis
        hdvalue=vishead()

        print "Please indicate if the following field is a science target (T), phase calibrator (P), amplitude (A), or bandpass calibrator (B)."

    #can get this from 'intent' field I think?
        for var in hdvalue[0]:
    #get user input
            reply= raw_input(var+' :')
    #save user input
            if reply == 'T': #if more than one? 
                target = var
            elif reply == 'P':
                phase = var
            elif reply == 'A':
                amp = var
            elif reply == 'B':
                bandpass = var
            else:
                print 'You should have learned the alphabet by now. Pick a valid choice: '
                var = var
        correct=raw_input('Is this correct? (Y/N)' )

   
    uv= raw_input('UV range for science target plots (found in weblog)? ')
    uvr='<'+uv+'m'

    # time to average over? default 1e8
    avgtime= raw_input('Time interval to use in averaging? Press enter for default 1e8 s') or '1e8'

    pdf=raw_input('Assemble plots in document inspect_[ms name].pdf (Y) or proceed manually (N)?')

#    print "You may need to adjust range/colour axis manually. Also note that colorization by antenna does not show up in pdf output, probably due to a plotms bug in CASA 4.2.2."

    vis=num

    if pdf == 'Y': 

    #get # of spw's
        # spws= msmd.spwsforintent(intent=("*TARGET*")) # casa apparently can't do this in 4.2.2 anymore, but there are always 4 spws anyway
        spws=[0,1,2,3]#len(spws)
        msmd.close()               

        for n in spws:
            #calibrated amplitude vs frequency, PHASE calibrator one plot for each spw
            # Have to check colorize on display and manually tell it to color; also have to change x axis when looking through different spws
            for phase in phasea:
	        AFPfile='aAmpvFreqPhase' + str(phase) + str(n) + str(num)+ '.png'
	 	title= 'Amp:corrected vs. Frequency, Phase calibrator, spw' + str(n)
	       	plotms(vis=vis, field=phase,yaxis='amp', xaxis='freq', avgtime=avgtime,coloraxis='ant1',spw=str(n),avgscan=T,avgantenna=T, plotfile=AFPfile, showgui=False, title = title)  
  
           #Calibrated amplitude vs frequency for BANDPASS calibrator all antennas and correlations, coloured by antenna. 
	    for bandpass in bandpassa:
        	AFBfile='bAmpvFreqBand' + str(bandpass)+ str(n) + str(num)+'.png'
	 	title= 'Amp:corrected vs. Frequency, Bandpass calibrator, spw' + str(n)
        	plotms(vis=vis, field=bandpass,yaxis='amp', xaxis='freq', avgtime=avgtime,avgscan=T,avgantenna=T,spw=str(n),coloraxis='ant1', plotfile=AFBfile, showgui=False, title=title)

            #phase vs frequency for PHASE calibrator
	    for phase in phasea:
            	PFPfile='cPhasevFreqPhase' + str(phase) + str(n) + str(num)+'.png'
	 	title= 'Phase:corrected vs. Frequency, Phase calibrator, spw' + str(n)
           	plotms(vis=vis, field=phase, yaxis='phase', xaxis='freq', avgtime=avgtime, coloraxis='ant1', spw=str(n), avgscan=T, avgantenna=T, plotrange=[0,0,-100,100], plotfile=PFPfile, showgui=False, title=title)

            #phase vs frequency for BANDPASS calibrator
	    for banpass in bandpassa:
            	PFBfile='dPhasevFreqBand' + str(bandpass) + str(n) + str(num)+'.png'
	 	title= 'Phase:corrected vs. Frequency, Bandpass calibrator, spw' + str(n)
            	plotms(vis=vis, field=bandpass, yaxis='phase', xaxis='freq', avgtime=avgtime, coloraxis='ant1',spw=str(n), avgscan=T, avgantenna=T, plotrange=[0,0,-100,100],plotfile=PFBfile, showgui=False, title=title)
 
            #amp vs uvdist
	    for amp in ampa:
	        AUVfile='eAmpvUVdist' + str(amp) + str(n) + str(num)+'.png'
	 	title= 'Amp:corrected vs. UVdist, spw' + str(n)
	        plotms(vis=vis, field=amp,yaxis='amp', xaxis='uvdist', avgchannel='1e6', spw=str(n),coloraxis='corr', plotfile=AUVfile, showgui=False, title=title)
    
            #amp vs time for all:
            ATfile='fAmpvTime' + str(n) + str(num)+'.png'
	    title= 'Amp:corrected vs. Time, spw' + str(n)
            plotms(vis=vis, yaxis='amp', xaxis='time', spw=str(n),coloraxis='field', avgchannel='100', plotfile=ATfile, showgui=False, title=title)

            # phase v time all:
            PTfile='gPhasevTime' + str(n) + str(num)+'.png'
	    title= 'Phase:corrected vs. UVdist, spw' + str(n)
            plotms(vis=vis, yaxis='phase', xaxis='time', spw=str(n),coloraxis='field',avgchannel='100',plotrange=[0,0,-100,100], avgantenna=T, plotfile=PTfile, showgui=False, title=title)
            
            # science target, amp v frequency
	    for target in targeta:
            	AFTfile='hAmpvFreqTarget' + str(target) + str(n) + str(num)+'.png'
	 	title= 'Amp:corrected vs. Freq,' +str(target)+', spw' + str(n)
            	plotms(vis=vis,  field=target, yaxis='amp', xaxis='freq', uvrange=uvr, spw=str(n), avgtime=avgtime, avgscan=T, avgantenna=T, plotfile=AFTfile, showgui=False, coloraxis='spw', title=title)
            
            # science target phase v frequency
	    for target in targeta:
            	PFTfile='iPhasevFreq' + str(target)  + str(n) + str(num)+'.png'
	 	title= 'Phase:corrected vs. Freq,' +str(target)+', spw' + str(n)
            	plotms(vis=vis, field=target, yaxis='phase',  xaxis='freq', uvrange=uvr, spw=str(n), avgtime=avgtime, avgscan=T, avgantenna=T, plotrange=[0,0,-100,100], plotfile=PFTfile, showgui=False, coloraxis='spw', title=title)
            
            # science target amp v UVdist
	    for target in targeta:
            	AUVTfile='jAmpvUVdistTarget' + str(target) + str(n) + str(num)+'.png'
	 	title= 'Amp:corrected vs. UVdist,' +str(target)+', spw' + str(n)
            	plotms(vis=vis, field=target, yaxis='amp', xaxis='uvdist', spw=str(n), plotfile=AUVTfile, showgui=False, coloraxis= 'spw', title=title)
            
        #dump everything in a pdf, one per ms 
        logname = 'inspect_' + num.replace('','')[:-10] + '.pdf'
        cmd = 'convert -compress jpeg `ls *split.cal.png` ' + logname
        os.system(cmd)
        # get rid of *.png files
        os.system('rm *split.cal.png')
        
    else:
        #manually
        spws=raw_input('spws of interest? String please.')
        if not spws:
            spws= msmd.spwsforintent(intent=("*TARGET*")) # casa apparently can't do this in 4.2.2 anymore, but there are always 4 spws anyway
        #spws=[0,1,2,3]#len(spws)
            msmd.close() 
        #calibrated amplitude vs frequency - have to check colorize on display and manually tell it to color; also have to change x axis when looking through different spws
        ans=raw_input('Plot amp v frequency for phase calibrator? (Y/N)')
        if ans == 'Y':
	    for phase in phasea:
            	plotms(vis=vis, field=phase,yaxis='amp', xaxis='freq', avgtime=avgtime,coloraxis='ant1',iteraxis='spw',avgscan=T,avgantenna=T, ydatacolumnn= 'corrected', spw=spws)
            	pause()

        #Calibrated amplitude vs frequency for BANDPASS calibrator all antennas and correlations, coloured by antenna.
        ans=raw_input('Plot amp v frequency for bandpass calibrator? (Y/N)')
        if ans == 'Y':
	    for bandpass in bandpassa:            
		plotms(vis=vis, field=bandpass,yaxis='amp', xaxis='freq', avgtime=avgtime,avgscan=T,avgantenna=T,iteraxis='spw',coloraxis='ant1', ydatacolumnn= 'corrected', spw=spws)
        	pause()

        #phase vs frequency for  phase calibrator
        ans=raw_input('Plot phase v frequency for phase calibrator? (Y/N)')
        if ans == 'Y':
	    for phase in phasea:
            	plotms(vis=vis, field=phase, yaxis='phase', xaxis='freq', avgtime=avgtime, coloraxis='ant1', iteraxis='spw', avgscan=T, avgantenna=T, plotrange=[0,0,-100,100], ydatacolumnn= 'corrected', spw=spws)
            	pause()

        #phase vs frequency for bandpass calibrator
        ans=raw_input('Plot phase v frequency for bandpass calibrator? (Y/N)')
        if ans == 'Y':
	    for bandpass in bandpassa:            
		plotms(vis=vis, field=bandpass, yaxis='phase', xaxis='freq', avgtime=avgtime, coloraxis='ant1', iteraxis='spw', avgscan=T, avgantenna=T, plotrange=[0,0,-100,100], ydatacolumnn= 'corrected', spw=spws)
            	pause()
    
        #amp vs uvdist
        ans=raw_input('Plot amp v UV distance? (Y/N)')
        if ans == 'Y':
	    for amp in ampa:
     	       plotms(vis=vis, field=amp,yaxis='amp', xaxis='uvdist', avgchannel='1e6', iteraxis='spw',coloraxis='corr', ydatacolumnn= 'corrected', spw=spws)
     	       pause()
    
        #amp vs time for all:
        ans=raw_input('Plot amp v time? (Y/N)')
        if ans == 'Y':
	    for amp in ampa:
      	      plotms(vis=vis, yaxis='amp', xaxis='time', iteraxis='spw',coloraxis='field', avgchannel='100', ydatacolumnn= 'corrected')
       	      pause() 

        # phase v time all:
        ans=raw_input('Plot phase v time? (Y/N)')
        if ans == 'Y':
	    for phase in phasea:
      	      plotms(vis=vis, yaxis='phase', xaxis='time', iteraxis='spw',coloraxis='field',avgchannel='100',  avgantenna=T, plotrange=[0,0,-100,100], ydatacolumnn= 'corrected')
      	      pause()
    
        #science target
        ans=raw_input('Plot amp v frequency for science target? (Y/N)')
        if ans == 'Y':
	    for target in targeta:
            	plotms(vis=vis,  field=target, yaxis='amp', xaxis='freq', uvrange=uvr, iteraxis='spw', avgtime=avgtime, avgscan=T, avgantenna=T, ydatacolumnn= 'corrected', spw=spws)   
            	pause()

        ans=raw_input('Plot phase v frequency for science target? (Y/N)')
        if ans == 'Y':    
	    for target in targeta:            
		plotms(vis=vis, field=target, yaxis='phase',  xaxis='freq', uvrange=uvr, iteraxis='spw', avgtime=avgtime, avgscan=T, avgantenna=T, plotrange=[0,0,-100,100], ydatacolumnn= 'corrected', spw=spws)
            	pause()
            
        ans=raw_input('Plot amp v UV distance for science target? (Y/N)')
        if ans == 'Y':
	    for target in targeta:
           	plotms(vis=vis, field=target, yaxis='amp', xaxis='uvdist', iteraxis='spw', ydatacolumnn= 'corrected', spw=spws)

    

