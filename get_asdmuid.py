#! /bin/env python
# -*- coding: iso-8859-1 -*-

"""
EL adapted from get_hierarchy_v3.py to get all asdms associated with project

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
   print datadict     
   ousid2=ousid.replace("___","://").replace("_","/")
   
   for line in html:
      line=line.split()
      #print line[0],line[1],line[2],line[3],line[4]
      if line[4]==ousid:
         #print "found project"
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
   #datadict['sbnames'] = list(set(datadict['sbnames']))
   #datadict['sbuids'] = list(set(datadict['sbuids']))
   datadict['ebuids'] = list(set(datadict['ebuids']))
  
   #print datadict['ebuids']
   return datadict['ebuids']


# --------------------------------------------------------------------------------------------------
def main(mous_code):
# --------------------------------------------------------------------------------------------------
   """
      get the data for the given ous and call the email creating function
   """
   import sys
   #=SB_name.split() # SB_name can be either string or string vector

   dataurl="http://www.eso.org/~fstoehr/project_ous_eb_hierarchy.txt"
   dataurl2="http://www.eso.org/~fstoehr/ous_eb_qa0status.txt"
   
   if len(mous_code)==0:
      print "usage:   python get_hierarchy_v2.py <member ous id with slashes>"
      print """
"""
      sys.exit(1)
   
   # uid://A001/X144/X6d -> uid/A001/X ... uid___A001_X144_X75
   #ousid=arguments[0].replace("___","://").replace("_","/")
   #ousid=mous_code.replace("://","___").replace("/","_")
   #ousid=mous_code.replace("___","___").replace("/","_")
   print mous_code
   datadict = readdatafromweb(dataurl, dataurl2, mous_code)
   print datadict
   return datadict


# --------------------------------------------------------------------------------------------------
if __name__=='__main__':
   import sys
   main(" ".join(sys.argv[1:]))

