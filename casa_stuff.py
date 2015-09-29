#######################################
# casa_stuff.py
# Erica Lastufka 08/20/2015 

#Description: Script to be run in CASA by list_imparameters.py since CASA and subprocess can't do individual commands
#######################################

vislist=glob.glob('*.ms.split.cal')
if not vislist:
    vislist=['calibrated.ms'] # in case of a manual reduction that was combined in Combination/calibrated
for vis in vislist:
    listfile=str(vis)+'.listobs.txt'
    listobs(vis=vis, spw='', intent='*TARGET*',listfile=listfile, overwrite=T, verbose=F)
vis=vislist[0]
msmd.open(vis)
nspws= msmd.spwsforintent(intent=("*TARGET*"))
sfields = msmd.fieldsforintent(intent=("*TARGET*"), asnames=False)
msmd.close() 
cell = au.pickCellSize(vis, spw='', npix=5, intent='OBSERVE_TARGET#ON_SOURCE', imsize=True, maxBaselinePercentile=95, cellstring=True, roundcell=2)
print nspws
print sfields
print cell

