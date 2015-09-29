#! /bin/env python
# -*- coding: iso-8859-1 -*-

"""
This script gets an OUS heirarchy from Felix's webpage and outputs a
helpdesk template and stuff to copy and paste into the google spreadsheets
(v2) now checks against the QA0 pass EBs on Felix's other website so only
QA0 pass ASDMs are returned.

"""

# --------------------------------------------------------------------------------------------------
def readdatafromweb(dataurl,dataurl2, ousid):
# --------------------------------------------------------------------------------------------------
   """
      This function reads the text file from the given url and creates a dictionary
   """
   import urllib2 

   response = urllib2.urlopen(dataurl)
   html     = response.read().splitlines()
   response = None
   datadict = {'mous':ousid}     
   ousid2=ousid.replace("___","://").replace("_","/")
   
   for line in html:
      line=line.split()
      #print line[0],line[1],line[2],line[3],line[4]
      if line[4]==ousid:
         #print "found MOUS"
         #print line[0]
         datadict['code']=line[0]
         datadict['sgous']=line[2] 
         datadict['gous']=line[3]
         datadict['mous']= line[4]
         if datadict.has_key('sbuids'):
            datadict['sbuids'].append(line[9])
         else:
            datadict['sbuids']=[line[9]]
         if datadict.has_key('sbnames'):
            datadict['sbnames'].append(line[10])
         else:
            datadict['sbnames']=[line[10]]
            
   response2 = urllib2.urlopen(dataurl2)
   html2     = response2.read().splitlines()
   response2 = None

   for line2 in html2:
      line2=line2.split("|")
      if line2[0]==ousid2:
         if datadict.has_key('ebuids'):
            datadict['ebuids'].append(line2[1])
         else:
            datadict['ebuids']=[line2[1]]

   # We want to uniquify the SB names (and the EB names although there should nothing to be done there
   datadict['sbnames'] = list(set(datadict['sbnames']))
   datadict['sbuids'] = list(set(datadict['sbuids']))
   datadict['ebuids'] = list(set(datadict['ebuids']))

   return datadict

 
# --------------------------------------------------------------------------------------------------
def returnemailtext(datadict):
# --------------------------------------------------------------------------------------------------
   """
      Write out the helpdesk email text with the input of the data dictionary
   """

   gousstr = datadict['gous'].replace("___","://").replace("_","/")
   mousstr = datadict['mous'].replace("___","://").replace("_","/")
   if len(datadict['sbnames'])==1:
      sbnamestr=" "+datadict['sbnames'][0].replace('"','')
   else:
      sbnamestr="s "+",".join(datadict['sbnames'][0:-1])+" and "+datadict['sbnames'][-1]
   if len(datadict['sbuids'])==1:
      sbuidstr=" "+datadict['sbuids'][0].replace("___","://").replace("_","/")
   else:
      sbuidstr="s "+",".join(datadict['sbuids'][0:-1])+" and "+datadict['sbuids'][-1]
   if len(datadict['ebuids'])==1:
      ebuidstr=" "+datadict['ebuids'][0].replace("___","://").replace("_","/")
   else:
      ebuidstr=" "+",".join(datadict['ebuids'][0:-1]).replace("___","://").replace("_","/")+" and "+datadict['ebuids'][-1].replace("___","://").replace("_","/")
   

   emailtext= """

Dear data-imager,

thank you for accepting the imaging assignment described below. You will be notified by another HelpDesk ticket when the data is staged in your lustre area.
We would appreciate if you could have a look at the visibilities and the weblog within 2 working days after the data is staged. The DRM will then contact you to ask you whether there are obvious issues with the dataset that would need data re-processing or a re-assignment of the dataset to the pipeline-working group. The deadline for completing the assignment is two weeks from the date you are provided with the correct data set. 
Data imaging instructions may be found at:
https://safe.nrao.edu/wiki/bin/view/ALMA/Cycle1and2ImagingReduction
The imaging template to follow can be found at:
https://staff.nrao.edu/wiki/bin/view/NAASC/NAImagingScripts

Dear DA,  data-imager has been assigned imaging of the MOUS described below. Please stage the corresponding pipeline products in a lustre area.

Project code: %s
GOUS: %s
MOUS: %s
SBName: %s
SBuid: %s
ASDMs: %s


Good Luck!

Arielle, Jen and Mark


"""%(datadict['code'],gousstr,mousstr,sbnamestr,sbuidstr,ebuidstr)
   

   #print datadict

   return emailtext



# --------------------------------------------------------------------------------------------------
def main(arguments):
# --------------------------------------------------------------------------------------------------
   """
      get the data for the given ous and call the email creating function
   """
   import sys
   arguments=arguments.split()

   dataurl="http://www.eso.org/~fstoehr/project_ous_eb_hierarchy.txt"
   dataurl2="http://www.eso.org/~fstoehr/ous_eb_qa0status.txt"
   
   if len(arguments)==0:
      print "usage:   python get_hierarchy_v2.py <member ous id with slashes>"
      print """
"""
      sys.exit(1)

   #ousid=arguments[0].replace("___","://").replace("_","/")
   ousid=arguments[0].replace("://","___").replace("/","_")
   
   datadict = readdatafromweb(dataurl, dataurl2, ousid)
   print returnemailtext(datadict)


# --------------------------------------------------------------------------------------------------
if __name__=='__main__':
   import sys
   main(" ".join(sys.argv[1:]))

