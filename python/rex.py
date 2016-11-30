#---------------------------------------------------------------------------------------------------
# Python Module File to provide a tool to execute a sequence of commands on a machine remotely. This
# is entirely based on ssh access and would need passwordless login to be set up so it would be
# convenient.
#
# Author: C.Paus                                                                      (Oct 19, 2016)
#---------------------------------------------------------------------------------------------------
import os,sys,re,string,socket
import subprocess

DEBUG = 0

#---------------------------------------------------------------------------------------------------
"""
Class:  Rex(host='submit.mit.edu',user='paus')
Allows to execute a command, or string of commands remotely.
"""
#---------------------------------------------------------------------------------------------------
class Rex:
    "Remote execution tool."

    #-----------------------------------------------------------------------------------------------
    # constructor
    #-----------------------------------------------------------------------------------------------
    def __init__(self,host='submit.mit.edu',user='cmsprod'):

        self.host = host
        self.user = user

        self.sshBase = 'ssh -x %s@%s '%(self.user,self.host)
        self.scpBase = '%s@%s'%(self.user,self.host)

    def getInternalRC(self,output):
        # find the return code from the command executed at the remote site
    
        irc = -99 # default means it failed
        lines = output.split('\n')    
    
        # very carefully extracting the internal return code
        if len(lines) > 1:
            lastLine = lines[-2]
            f = lastLine.split(':')
            if len(f) > 1:
                if f[0] == 'IRC':
                    lines = lines[:-2] # overwite output removing the IRC line
                    output = "\n".join(lines)
                    irc = int(f[1])
    
        return (irc,output)
    
    def executeAction(self,action):
        # execute the defined action and return irc - remote return code
        #                                       rc  - local return code
        #                                       out - standard output
        #                                       err - standard error
        
        list = self.sshBase.split(' ')
        list.append(action)
        list.append('\n echo IRC:$?') # this will make sure that we know the internal return code
    
        # show what we do
        if DEBUG>1:
            print ' CMD String: ' + " ".join(list)
            print ' CMD List: '
            print list
        
        p = subprocess.Popen(list,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=False)
        (out, err) = p.communicate()
        rc = p.returncode
        (irc, out) = self.getInternalRC(out) # get the internal retrun code and clean the output
    
        if irc != 0:
            print " ERROR on remote end: %d"%(int(irc))
            print " "
            print " " + err
                
        return (irc,rc,out,err)

    def executeLongAction(self,action):
        # execute the defined action and return irc - remote return code
        #                                       rc  - local return code
        #                                       out - standard output
        #                                       err - standard error
        
        # generate a script file
        scriptFile = 'rex.%d'%(os.getpid())
        with open(scriptFile,'w') as fH:
            fH.write('#!/bin/bash\n%s\n'%(action))

        # make executable
        os.system("chmod 755 " + scriptFile)

        # transfer script file to the remote place
        os.system("scp -q " + scriptFile + " " + self.scpBase + ":")
        
        # execute the reomte script
        (irc,rc,out,err) = self.executeAction("./" + scriptFile)

        # remove executable script from remote site
        self.executeAction("rm -f " + scriptFile)

        # remove executable script locally once we are done
        os.system("rm -f " + scriptFile)

        return (irc,rc,out,err)

    def executeLocalAction(self,action):
        # execute the defined action and return rc  - return code
        #                                       out - standard output
        #                                       err - standard error
        
        # show what we do
        if DEBUG>1:
            print ' CMD String: ' + action
        
        p = subprocess.Popen(action,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        (out, err) = p.communicate()
        rc = p.returncode
    
        if rc != 0 and DEBUG > 0:
            print " ERROR on remote end: %d"%(int(rc))
            print " "
            print " " + err
                
        return (rc,out,err)

    def executeLocalLongAction(self,action):
        # execute the defined action and return rc  - local return code
        #                                       out - standard output
        #                                       err - standard error
        
        # generate a script file
        scriptFile = 'rex.%d'%(os.getpid())
        with open(scriptFile,'w') as fH:
            fH.write('#!/bin/bash\n%s\n'%(action))

        # make executable
        os.system("chmod 755 " + scriptFile)

        # execute the script
        (rc,out,err) = self.executeLocalAction("./" + scriptFile)

        # remove executable script locally once we are done
        os.system("rm -f " + scriptFile)

        return (rc,out,err)

#===================================================================================================
# M A I N [for testing only]
#===================================================================================================
#if __name__ == "__main__":
#    rex = Rex()
#
# -- standard short remote
#
#    (irc,rc,out,err) = rex.executeAction("ls -l cms/logs\n ls -l cms/logs/filefi/0?*\n ls -lhrt")
#    print " "
#    print "==== SUMMARY ===="
#    print " "
#    print " Output\n" + out
#    print " "
#    print " Return code on remote end: %d"%(int(irc))
#    print " "
#    if err != "":
#        print " Error\n" + err
#        print " "
#
# -- long
#
#    (irc,rc,out,err) = rex.executeLongAction("ls -l cms/logs\nls -l cms/logs/filefi/0?*\nls -lhrt")
#    print " "
#    print "==== SUMMARY ===="
#    print " "
#    print " Output\n" + out
#    print " "
#    print " Return code on remote end: %d"%(int(irc))
#    print " "
#    if err != "":
#        print " Error\n" + err
#        print " "
#
# -- local
#    (rc,out,err) = rex.executeLocalAction("ls -l cms/logs\n ls -l cms/logs/filefi/0?*\n ls -lhrt")
## also works
##    (rc,out,err) = rex.executeLocalAction("ls -l cms/logs; ls -l cms/logs/filefi/0?*; ls -lhrt")
#    print " "
#    print "==== LOCAL SUMMARY ===="
#    print " "
#    print " Output\n" + out
#    print " "
#    print " Return code: %d"%(int(rc))
#    print " "
#    if err != "":
#        print " Error\n" + err
#        print " "
