import time
import datetime

def header():
    header1 = "#>>> ======================================================================================#\n\
#>>>                          CUSTOM IMAGING SCRIPT                                       #\n\
#>>> =====================================================================================#\n\
#>>> \n"
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    gendate = '#>>> Generated at ' + st + ' local time by <script_generator.py>\n'

    header2 = "#>>> \n\
#>>> Lines beginning with '#>>>' are instructions to the data imager\n\
#>>> and will be removed from the script delivered to the PI. If you \n\
#>>> would like to include a comment that will be passed to the PI, begin\n\
#>>> the line with a single '#', i.e., standard python comment syntax.\n\
#>>>\n\
#>>> Helpful tip: Use the commands %cpaste or %paste to copy and paste\n\
#>>> indented sections of code into the casa command line.\n\
#>>>\n\
#>>> If you believe any part of this script has been generated in error\n\
#>>> or find a conflict with the values given in the ALMA OT, please contact\n\
#>>> elastufk@nrao.edu\n\
#>>>\n\
#>>>--------------------------------------------------------------------------------------#\n\
#>>>                     Data Preparation                                                 #\n\
#>>> -------------------------------------------------------------------------------------#\n\
#>>>\n\
#>>> Below are some example commands for combining your data. All of\n\
#>>> these commands will not be relevant for all datasets, so think about\n\
#>>> what would be best for your data before running any commands. For\n\
#>>> more information, see the NA Imaging Guide\n\
#>>> (https://staff.nrao.edu/wiki/bin/view/NAASC/NAImagingScripts).\n\
#>>>\n\
#>>> These commands should be run prior to undertaking any imaging.\n\
#>>>>\n\
#>>> The NA Imaging team is working on generating best\n\
#>>> practices for this step. Suggestions are welcome!  Please send to\n\
#>>> akepley@nrao.edu and she'll forward them on to the NA Imaging team.\n\n\
########################################\n\
# Check CASA version \n"

    header = header1 + gendate + header2
    return header

def header():
    header1 = "#>>> ======================================================================================#\n\
#>>>                          TEMPLATE IMAGING SCRIPT                                       #\n\
#>>> =====================================================================================#\n\
#>>> \n"
#    ts = time.time()
#    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
#    gendate = '#>>> Generated at ' + st + ' local time by <script_generator.py>\n'
#
    gendate = '#>>> Updated: Tue Dec  1 14:10:46 EST 2015\n'
    header2 = "#>>> \n\
#>>> Lines beginning with '#>>>' are instructions to the data imager\n\
#>>> and will be removed from the script delivered to the PI. If you \n\
#>>> would like to include a comment that will be passed to the PI, begin\n\
#>>> the line with a single '#', i.e., standard python comment syntax.\n\
#>>>\n\
#>>> Helpful tip: Use the commands %cpaste or %paste to copy and paste\n\
#>>> indented sections of code into the casa command line.\n\
#>>>\n\
#>>>--------------------------------------------------------------------------------------#\n\
#>>>                     Data Preparation                                                 #\n\
#>>> -------------------------------------------------------------------------------------#\n\
#>>>\n\
#>>> Below are some example commands for combining your data. All of\n\
#>>> these commands will not be relevant for all datasets, so think about\n\
#>>> what would be best for your data before running any commands. For\n\
#>>> more information, see the NA Imaging Guide\n\
#>>> (https://staff.nrao.edu/wiki/bin/view/NAASC/NAImagingScripts).\n\
#>>>\n\
#>>> These commands should be run prior to undertaking any imaging.\n\
#>>>>\n\
#>>> The NA Imaging team is working on generating best\n\
#>>> practices for this step. Suggestions are welcome!  Please send to\n\
#>>> akepley@nrao.edu and she'll forward them on to the NA Imaging team.\n\n\
########################################\n\
# Check CASA version \n"

    header = header1 + header2
    return header
def header_brief():
    header1 = "#>>> ======================================================================================#\n\
#>>>                          CUSTOM IMAGING SCRIPT                                       #\n\
#>>> =====================================================================================#\n\
#>>> \n"
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    gendate = '#>>> Generated at ' + st + ' local time by <script_generator.py>\n'

    header2 = "#>>> \n\
#>>> If you believe any part of this script has been generated in error\n\
#>>> or find a conflict with the values given in the ALMA OT, please contact\n\
#>>> elastufk@nrao.edu\n\
#>>>\n\
#>>>--------------------------------------------------------------------------------------#\n\
#>>>                     Data Preparation                                                 #\n\
#>>> -------------------------------------------------------------------------------------#\n\
########################################\n\
# Check CASA version \n"

    header = header1 + gendate + header2
    return header

def glob_list():
    glob_list = "########################################\n\
# Getting a list of ms files to image\n"
    return glob_list

def pointing():
    pointing = "########################################\n\
# Removing pointing table \n\n\
# This step removes the pointing table from the data to avoid\n\
# a bug with mosaics in CASA 4.2.2\n\n\
# DO NOT DO THIS FOR CASA 4.5 AND GREATER! DELETING THE POINTING TABLE\n\
# WILL CAUSE ISSUES FOR OTF MOSAICS."
    return pointing

def combine():
    combine = "########################################\n\
# Combining Measurement Sets from Multiple Executions\n\
# If you have multiple executions, you will want to combine the \n\
# scheduling blocks into a single ms using concat for ease of imaging \n\
# and self-calibration. Each execution of the scheduling block will \n\
# generate multiple spectral windows with different sky frequencies, \n\
# but the same rest frequency, due to the motion of the Earth. Thus, \n\
# the resulting concatentated file will contain n spws, where n is \n\
# (#original science spws) x (number executions).  In other words, the \n\
# multiple spws associated with a single rest frequency will not be \n\
# regridded to a single spectral window in the ms. \n "
    return combine

def combine_warning():
    combine_warning = "\n\
#>>> DO NOT DO THIS IF YOU HAVE MANUALLY CALIBRATED YOUR DATA. THE\n\
#>>> COMBINATION HAS ALREADY BEEN DONE AS PART OF THE MANUAL\n\
#>>> CALIBRATION."
    return combine_warning

def combine_header():
    combine = "########################################\n\
# Combining Measurement Sets from Multiple Executions\n"
    return combine

def split():
    split = "###################################\n\
# Splitting off science target data\n\n"
    return split

def split_single():
    split_single = "#>>> Uncomment following line for single executions\n"
    return split_single

def split_multiple():
    split_multiple = "#>>> Uncomment following line for multiple executions\n"
    return split_multiple

def vishead():
    vishead = "#>>> INCLUDE vishead OUTPUT FOR SCIENCE TARGET AND SPW IDS HERE.\n\n\
#>>> Doing the split.  If multiple data sets were rescaled using\n\
#>>> scriptForFluxCalibration.py, need to get datacolumn='corrected'\n"
    return vishead

def check_split():
    check_split = "# Check that split worked as desired.\n"
    return check_split

def regrid():
    regrid = "###############################################################\n\
# Regridding spectral windows [OPTIONAL]\n\n\
#>>> The spws associated with a common rest frequency can be regridded to\n\
#>>> a single spectral window during cleaning or using the cvel\n\
#>>> command. The NA imaging team strongly recommends the first option,\n\
#>>> unless the lines shift too much between executions to identify an\n\
#>>> common channel range for continuum subtraction. The code below uses\n\
#>>> cvel to regrid multiple spws associated with a single rest frequency\n\
#>>> into a single spw. You will want to use the same regridding\n\
#>>> parameters later when you clean to avoid clean regridding the image\n\
#>>> a second time.\n\n"
    return regrid

def regrid_header():
    regrid = "###############################################################\n\
# Regridding spectral windows [OPTIONAL]\n\n"
    return regrid

def backup():
    backup = "############################################\n\
# Rename and backup data set\n\n"
    return backup

def im_template():
    im_template = "#>>> Please do not modify the final name of the file\n\
#>>> ('calibrated_final.ms'). The packaging process requires a file with\n\
#>>> this name.\n\n\
#>>>--------------------------------------------------------------------------------------#\n\
#>>>                             Imaging Template                                         #\n\
#>>>--------------------------------------------------------------------------------------#\n\
#>>>\n\
#>>> The commands below serve as a guide to best practices for imaging\n\
#>>> ALMA data. It does not replace careful thought on your part while\n\
#>>> imaging the data. You can remove or modify sections as necessary\n\
#>>> depending on your particular imaging case (e.g., no\n\
#>>> self-calibration, continuum only.) Please read the NA Imaging Guide\n\
#>>> (https://staff.nrao.edu/wiki/bin/view/NAASC/NAImagingScripts) for\n\
#>>> more information.\n\
#>>>\n\
#>>> Before imaging, you should use the commands the first section of\n\
#>>> this script to prep the data for imaging.  The commands in both\n\
#>>> sections should be able to be run as as standard Python\n\
#>>> script. However, the cleaning in this script is done interactively\n\
#>>> making the final product somewhat dependent on the individual doing\n\
#>>> the clean -- please clean conservatively (i.e., don't box every\n\
#>>> possible source). The final data products are the cleaned images\n\
#>>> (*.image), the primary beam corrected images (*.pbcor), and the\n\
#>>> primary beams (*.flux). These images should be converted to fits at\n\
#>>> the end of the script (see example at the end of this file).\n\
#>>>\n\
#>>> This script (and the associated guide) are under active\n\
#>>> development. Please contact Amanda Kepley (akepley@nrao.edu) if you\n\
#>>> have any suggested changes or find any bugs that are almost\n\
#>>> certainly there.\n\n\
##################################################\n\
# Create an Averaged Continuum MS\n\n\
#>>> Continuum images can be sped up considerably by averaging the data\n\
#>>> together to reduce overall volume.Since the sensitivity of a\n\
#>>> continuum image depends on its bandwidth, continuum images are\n\
#>>> typically made by including as much bandwidth as possible in the\n\
#>>> data while excluding any line emission. The following plotms command\n\
#>>> pages through the spectral windows in a project allowing you to\n\
#>>> identify channel ranges within spectral windows that do not include\n\
#>>> *strong* line emission. You will form a continuum image by averaging\n\
#>>> the line-free spws and/or channel ranges within spws. In most cases,\n\
#>>> you will not need to create an image to select line channels,\n\
#>>> although you can suggest this to the PI as a possible path for\n\
#>>> future exploration in the README file for cases where there is\n\
#>>> wide-spread line emission.\n\
#>>>\n\
#>>> For a project with continuum target sensitivities, it is worth\n\
#>>> checking the OT to see what continuum bandwidth the PI was\n\
#>>> anticipating. In many cases, the continuum-only windows will be\n\
#>>> specified in the OT, in general these have the broadest bandwidths\n\
#>>> (~2GHz) with a small number of channels (128).  However, other\n\
#>>> windows may be combined with these designated continuum windows to\n\
#>>> increase the continuum sensitivity. In general, it is not necessary\n\
#>>> to include narrow spectral windows (<250MHz) in the continuum image.\n\n"
    return im_template

def im_template_header():
    im_template = "#>>>--------------------------------------------------------------------------------------#\n\
#>>>                             Imaging Template                                         #\n\
#>>>--------------------------------------------------------------------------------------#\n\n\
##################################################\n\
# Create an Averaged Continuum MS\n\n"
    return im_template

def casa_warning():
    casa_warning = "#>>> In CASA 4.4 and higher, the behavior of the avgchannel parameter\n\
#>>> has changed. Now when you plot binned channels, plotms displays\n\
#>>> the 'bin' number rather than the average channel number of each\n\
#>>> bin. Amanda is trying to get this behavior changed back to\n\
#>>> something more sensible\n\n\
#>>> If you don't see any obvious lines in the above plot, you may to try\n\
#>>> to set avgbaseline=True with uvrange (e.g., <100m). Limiting the\n\
#>>> uvrange to the short baselines greatly improves the visibility of\n\
#>>> lines with extended emission.\n"
    return casa_warning

def split_versions():
    split_versions = "# IF YOU ARE USING CASA VERSION 4.4 OR GREATER TO IMAGE, UNCOMMENT THE FOLLOWING. DELETE IF NOT APPROPRRIATE.\n\
# split2(vis=finalvis,\n\
#      spw=contspws,      \n\
#      outputvis=contvis,\n\
#      width=[128,128,3840,3840], # number of channels to average together. change to appropriate value for each spectral window in contspws (use listobs or vishead to find) and make sure to use the native number of channels per SPW (that is, not the number of channels left after flagging any lines)\n\
#      datacolumn='data')\n\
\n\
# IF YOU ARE USING CASA VERSION 4.3 AND BELOW TO IMAGE, UNCOMMENT THE FOLLOWING. DELETE IF NOT APPROPRIATE.\n\
# split(vis=finalvis,\n\
#       spw=contspws,      \n\
#       outputvis=contvis,\n\
#       width=[128,128,3840,3840], # number of channels to average together. change to appropriate value for each\n\
spectral window in contspws (use listobs or vishead to find) and make sure to use the native number of channels per SPW (that is, not the number of channels left after flagging any lines)\n\
#       datacolumn='data')\n\
\n\
# Note: There is a bug in split that does not average the data\n\
# properly if the width is set to a value larger than the number of\n\
# channels in an SPW. Specifying the width of each spw (as done above)\n\
# is necessary for producing properly weighted data.\n"
    return split_versions

def source_param():
    source_param = "# #############################################\n\
# Image Parameters\n\n\
#>>> You're now ready to image. Review the science goals in the OT and\n\
#>>> set the relevant imaging parameters below. \n\n\
# source parameters\n\
# ------------------\n\n"
    return source_param

def source_param_header():
    source_param = "# #############################################\n\
# Image Parameters\n\n"
    return source_param

def cellcalc():
    cellcalc = "#>>> Generally, you want 5-8 cells (i.e., pixels) across the narrowest\n\
#>>> part of the beam. You can estimate the beam size using the following\n\
#>>> equation: 206265.0/(longest baseline in wavelengths).  To determine\n\
#>>> the longest baseline, use plotms with xaxis='uvwave' and\n\
#>>> yaxis='amp'. Divide the estimated beam size by five to eight to get\n\
#>>> your cell size. It's better to error on the side of slightly too\n\
#>>> many cells per beam than too few. Once you have made an image,\n\
#>>> please re-assess the cell size based on the beam of the image. You can\n\
#>>> check your cell size using  au.pickCellSize('calibrated_final.ms'). Note\n\
#>>> however, that this routine does not take into account the projection of\n\
#>>> the baseline onto the sky, so the plotms method described above is overall\n\
#>>> more accurate.\n\n\
#>>> To determine the image size (i.e., the imsize parameter), first you\n\
#>>> need to figure out whether the ms is a mosaic by either looking out\n\
#>>> the output from listobs/vishead or checking the spatial setup in the OT. For\n\
#>>> single fields, an imsize equal to the size of the primary beam is\n\
#>>> usually sufficient. The ALMA 12m primary beam in arcsec scales as\n\
#>>> 6300 / nu[GHz] and the ALMA 7m primary beam in arcsec scales as\n\
#>>> 10608 / nu[GHz], where nu[GHz] is the sky frequency. However, if\n\
#>>> there is significant point source and/or extended emission beyond\n\
#>>> the edges of your initial images, you should increase the imsize to\n\
#>>> incorporate more emission. For mosaics, you can get the imsize from\n\
#>>> the spatial tab of the OT. The parameters 'p length' and 'q length'\n\
#>>> specify the dimensions of the mosaic. If you're imaging a mosaic,\n\
#>>> pad the imsize substantially to avoid artifacts.\n\n\
#>>> Note that for a single field you can check your image size using\n\
#>>> au.pickCellSize('calibrated_final.ms', imsize=True)\n"
    return cellcalc

def velparam():
    velparam = "# velocity parameters\n\
# -------------------\n\n\
# Use the following plotMS command to determine an appropriate start velocity and number of channels.\n\
# Otherwise the default will be to make the entire image cube.\n\n"
    return velparam

def veltype():
    veltype = "#>>> Note on veltype: We recommend keeping veltype set to radio,\n\
#>>> regardless of the velocity frame listed the object in the OT. If the\n\
#>>> sensitivity is defined using a velocity width, then the 'radio'\n\
#>>> definition of the velocity frame is used regardless of the velocity\n\
#>>> definition in the 'source parameters' tab of the OT.\n\n"
    return veltype

def imcontrol():
    imcontrol = "# imaging control\n\
# ----------------\n\n\
# The cleaning below is done interactively, so niter and threshold can\n\
# be controlled within clean.\n\n"
    return imcontrol

def im_cont():
    im_cont = "#############################################\n\
# Imaging the Continuuum\n\n\
# Set the ms and continuum image name.\n\n"
    return im_cont

def im_cont_header():
    im_cont = "#############################################\n\
# Imaging the Continuuum\n\n"
    return im_cont

def cont_rms():
    cont_rms = "#>>> If interactively cleaning (interactive=True), then note number of\n\
#>>> iterations at which you stop for the PI. This number will help\n\
#>>> the PI replicate the delivered images. Do not clean empty\n\
#>>> images. Just click the red X to stop the interactive and note the\n\
#>>> RMS.\n\n\
#>>> Note RMS for PI. \n\n\
# If you'd like to redo your clean, but don't want to make a new mask\n\
# use the following commands to save your original mask. This is an optional step.\n\
#contmaskname = 'cont.mask'\n\
##rmtables(contmaskname) # if you want to delete the old mask\n\
#os.system('cp -ir ' + contimagename + '.mask ' + contmaskname)\n\n"
    return cont_rms

def contsub():
    contsub = "########################################\n\
# Continuum Subtraction for Line Imaging\n\n\
#>>> If you have observations that include both line and strong (>3 sigma\n\
#>>> per final line image channel) continuum emission, you need to\n\
#>>> subtract the continuum from the line data. You should not continuum\n\
#>>> subtract if the line of interest is in absorption.\n\n"
    return contsub

def contsub_header():
    contsub = "########################################\n\
# Continuum Subtraction for Line Imaging\n\n"
    return contsub

def im_line():
    im_line = "##############################################\n\
# Image line emission \n\n\
#>>> If you did an mstransform/cvel, use the same velocity parameters in\n\
#>>> the clean that you did for the regridding. If you did not do an\n\
#>>> mstransform and have multiple executions of a scheduling block,\n\
#>>> select the spws with the same rest frequency using the spw parameter\n\
#>>> (currently commented out below). DO NOT INCLUDE SPWS WITH DIFFERENT\n\
#>>> REST FREQUENCIES IN THE SAME RUN OF CLEAN: THEY WILL SLOW DOWN\n\
#>>> IMAGING CONSIDERABLY.\n\n"
    return im_line

def im_line_header():
    im_line = "##############################################\n\
# Image line emission \n\n"
    return im_line

def line_cvel():
    line_cvel = "#>>> To specify a spws from multiple executions that had not been regridded using cvel, use\n\
#>>>       import numpy as np\n\
#>>>       spw = str.join(',',map(str,np.arange(0,n,nspw)))\n\
#>>>\n\
#>>> where n is the total number of windows x executions and nspw is the\n\
#>>> number of spectral windows per execution. Note that the spectral\n\
#>>> windows need to have the same order in all data sets for this code\n\
#>>> to work. Add a constant offset (i.e., +1,+2,+3) to the array\n\
#>>> generated by np.arange to get the other sets of windows.\n\n\
# If necessary, run the following commands to get rid of older clean\n\
# data.\n\n\
#clearcal(vis=linevis)\n\
#delmod(vis=linevis)\n"
    return line_cvel

def line_rms():
    line_rms = "#>>> If interactively cleaning (interactive=True), then note number of\n\
#>>> iterations at which you stop for the PI. This number will help the\n\
#>>> PI replicate the delivered images. Do not clean empty\n\
#>>> images. Just click the red X to stop the interactive and note the\n\
#>>> RMS.\n\n\
# If you'd like to redo your clean, but don't want to make a new mask\n\
# use the following commands to save your original mask. This is an\n\
# optional step.\n\
# linemaskname = 'line.mask'\n\
## rmtables(linemaskname) # uncomment if you want to overwrite the mask.\n\
# os.system('cp -ir ' + lineimagename + '.mask ' + linemaskname)\n\n"
    return line_rms    

def pbcor():
    pbcor = "##############################################\n\
# Apply a primary beam correction\n\n"
    return pbcor

def export():
    export = "##############################################\n\
# Export the images\n\n"
    return export

def analysis():
    analysis = "##############################################\n\
# Analysis\n\n\
# For examples of how to get started analyzing your data, see \n\
#     http://casaguides.nrao.edu/index.php?title=TWHydraBand7_Imaging_4.2\n\n"
    return analysis
