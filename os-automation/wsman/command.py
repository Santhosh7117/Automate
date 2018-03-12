# Copyright (c) 2006 Red Hat, Inc. All rights reserved. This copyrighted material
# is made available to anyone wishing to use, modify, copy, or
# redistribute it subject to the terms and conditions of the GNU General
# Public License v.2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Author: Greg Nichols
#
# Overview:
#    The Command class is a wrapper for shell commands that performs
#    validation and error checking.  Example usage can be seen in the
#    __main__ self test function at the end of this file.


import os,re, commands, subprocess, string, sys, datetime


class Command:
    
    def __init__(self, command):
        """ Creates a Command object that wraps the shell command
            via the supplied string, similar to os.system.   The
            constuctor does not actually execute the command.
        """
        self.command = command
        self.regex = None
        self.singleLine = True
        self.regexGroup = None
        self.output = None
        self.errors = None
        self.returnValue = 0
        self.signal = 0
        self.pipe = None
        
    def _run(self):
        # commandPipe = popen2.Popen3(self.command, capturestderr=True)
        self.pipe = subprocess.Popen(self.command, shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,)
        (output, errors) = self.pipe.communicate()
        if output:
            self.output = output.splitlines()
        if errors:
            self.errors = errors.splitlines()
        self.signal = 0
        self.returnValue = 0
        if self.pipe.returncode < 0:
            self.signal = self.pipe.returncode
        else:
            self.returnValue = self.pipe.returncode
        
    def start(self):
        self.pipe = subprocess.Popen(self.command, shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,)
                
    def _checkErrors(self):
            
        if self.errors and len(self.errors) > 0:
            raise V7CommandErrorOutput(self)
        self._checkReturnValue()

    def _checkReturnValue(self):
        if self.returnValue != 0 or self.signal != 0:
            # if error returned, show stdout whether echo or run was called
            if self.output:
                for line in self.output:
                    sys.stdout.write( line )
                    sys.stdout.write("\n")
                sys.stdout.flush()
            if self.returnValue != 0:
                raise V7CommandErrorReturned(self, self.returnValue)
            if self.signal != 0:
                raise V7CommandErrorKilled(self, self.signal)
    
    def run(self):
        """ This method runs the command to produce an action.  Any output
            to stdout is not echoed to the caller. """
        self._run()
        self._checkErrors()
        return 0
        
    
    def echo(self, ignoreErrors=False):
        """ output is equivalent to run, except that the commands' output
            is echo'd on stdout. """
        self._run()
        if not ignoreErrors:
            self._checkErrors()
        self.printOutput()
        return 0
    
    def echoIgnoreErrors(self):
        return self.echo(ignoreErrors=True)
        
    def printOutput(self):
        if self.output:
            for line in self.output:
                sys.stdout.write( line )
                sys.stdout.write("\n")
            sys.stdout.flush()
        
    def printErrors(self):
        if self.errors:
            for line in self.errors:
                sys.stderr.write( line )
                sys.stderr.write("\n")
            sys.stderr.flush()
    
            
    def _getString(self, regex=None, regexGroup=None, singleLine=True, returnList=False, ignoreErrors=False):
        """
        Get the string from the command's output.  With default parameters
        it returns the command's single line of output as a string.
        
        If singleLine is True, and multiple lines are found in the output,
        V7CommandException is raised.
        
        The regex parameter allows the output to be searched for a regular
        expression match.  If no regexGroup is supplied, the entire pattern
        match is returned.   The regexGroup parameter allows named
        substrings of the match to be returned if regex has named groups
        via the "(?P<name>)" syntax.   If no match is found,
        V7CommandException is raised.
        """
        self.regex = regex
        self.singleLine = singleLine
        self.regexGroup = regexGroup
        
        self._run()
        
        if self.singleLine:
            if self.output and len(self.output) > 1:
               raise V7CommandException(self, "Found %u lines of output, expected 1" % len(self.output))
            
            if self.output:
                line = self.output[0].strip()
                if not self.regex:
                    return line
                # otherwise, try the regex
                pattern = re.compile(self.regex)
                match = pattern.match(line)
                if match:
                    if self.regexGroup:
                        return match.group(self.regexGroup)
                    # otherwise, no group, return the whole line
                    return line
                
                # no regex match try a grep-style match
                if not self.regexGroup:
                    match = pattern.search(line)
                    if match:
                        return match.group()
                
            # otherwise
            raise V7CommandException(self, "no match for regular expression %s" % self.regex)
            
        
        #otherwise, multi-line or single-line regex
        if not self.regex:
            raise V7CommandError(self, "no regular expression set for multi-line command")
        pattern = re.compile(self.regex)
        result = None
        if returnList:
            result = list()
        if self.output:
            for line in self.output:
                if self.regexGroup:
                    match = pattern.match(line)
                    if match:
                        if self.regexGroup:
                            if returnList:
                                result.append(match.group(self.regexGroup))
                            else:
                                return match.group(self.regexGroup)
                else:
                    # otherwise, return the matching line
                    match = pattern.search(line)
                    if match:
                        if returnList:
                            result.append(match.group())
                        else:
                            return match.group()
            if result:
                return result
            
        # otherwise
        raise V7CommandException(self, "no match for regular expression %s" % self.regex)
    
    def getStringList(self, regex=None, regexGroup=None, ignoreErrors=False):
        """ like getString, except return a complete list of matches on multiple lines."""
        result = self._getString(regex, regexGroup, singleLine=False, returnList=True)
        if not ignoreErrors:
            self._checkErrors()
        return result
    
    def getString(self, regex=None, regexGroup=None, singleLine=True,  ignoreErrors=False):
        """ like getString, except return a complete list of matches on multiple lines."""
        result = self._getString(regex, regexGroup, singleLine, returnList=False)
        if not ignoreErrors:
            self._checkErrors()
        return result
        
    
    def getInteger(self, regex=None, regexGroup=None, singleLine=True):
        """
        getInteger is the same as getString, except the output is required to
        be an Integer.
        """
        value = self.getString(regex, regexGroup, singleLine)
        return string.atoi(value)
    
    def getPID(self):
        if self.pipe:
            return self.pipe.pid
        raise V7CommandException(self.command, "call to getPID() before start()")
    
    def readline(self):
        if self.pipe:
            return self.pipe.stdout.readline()
        raise V7CommandException(self.command, "call to readline() before start()")
    
    def poll(self):
        if self.pipe:
            return self.pipe.poll()
        # otherwise, command never started
        raise V7CommandException(self.command, "call to poll() before start()")
                

# V7 Command Exceptions:
# These exceptions are organized in a type hierarch to allow different levels of exceptions
# to be caught and handled:
#
#    V7CommandException                - all exceptions raised by Command
#        V7CommandError                - commands that either returned non-zero, or were killed
#            V7CommandErrorReturned    - commands that returned non-zero
#            V7CommandErrorKilled      - commands that were killed via signal
#        V7CommandErrorOutput          - commands that had output on stderr

    
class V7CommandException(Exception):
    def __init__(self, command, message):
        self.message = message
        self.command = command
    
    def __str__(self):
        return "\"%s\" %s" % (self.command.command, self.message)
    
    # BaseException.message has been deprecated since Python 2.6.  To prevent
    # DeprecationWarning from popping up over this pre-existing attribute, use
    # a new property that takes lookup precedence.
    def _get_message(self): return self.__message
    def _set_message(self, value): self.__message = value
    message = property(_get_message, _set_message)

class V7CommandErrorOutput(V7CommandException):
    def __init__(self, command):
        V7CommandException.__init__(self, command, "has output on stderr")
        
class V7CommandError(V7CommandException):
    def __init__(self, command, message):
        V7CommandException.__init__(self, command, message)
    
    
class V7CommandErrorReturned(V7CommandError):
    def __init__(self, command, returnValue):
        V7CommandError.__init__(self, command, "returned %d" % returnValue)
        
class V7CommandErrorKilled(V7CommandError):
    def __init__(self, command, signal):
        V7CommandError.__init__(self, command, "signal %d" % signal)
        
def unitTest():
    result = True
    try:
        # positive test: run
        command = Command("ls -a")
        print "ls -a:"
        command.run()
        
        # positive test: simple match
        year = "%u" % datetime.date.today().year
        command = Command("date")
        print "is it %s" % year
        print command.getString(year)
        
        # positive test: regex on single line
        command = Command("date")
        print "day of the week via date: %s" %  command.getString(regex="^(?P<day>[MTWF][a-z]).*$", regexGroup="day")
        
        # positive test: regex on multiline
        command = Command("who")
        print "a device via who: %s" % command.getString(regex="^(?P<user>[a-z]+) (?P<device>[a-z/]+[0-9]*)[ \t]*(?P<date>2\d+-\d+-\d+).*$", regexGroup="device", singleLine=False)
        
        #positive test: integer - simple match
        command = Command("du .")
        print "simple du: %u" % command.getInteger(regex="\d+", singleLine=False)
       
       #positive test: integer
        command = Command("df .")
        print "blocks via df: %u" % command.getInteger(regex="^[ \t]+(?P<blocks>[0-9]+[ \t]+).*$", regexGroup="blocks", singleLine=False)
        
    except V7CommandException, e:
        print "Error: positive test failed:"
        print command.command
        print e
        result = False
        
    # negative test: fail simple match
    try:
        print "is it 1999?:"
        command = Command("date")
        command.getString(regex="1999")
        print "Error: invalid string match should raise exception"
        result = False
    except V7CommandException, e:
        print e
        
    # negative test: return value
    try:
        print "negative test: return value:"
        command = Command("exit 1")
        print "call exit(1)"
        command.echo()
        print "Error: non-zero return value should raise exception"
        result = False
    except V7CommandException, e:
        print e
        print "passed"
        
    # negative test: killed subprocess
    # disabling this test - to test it, use "killall sleep" while the unit test has paused.
    if False:
        try:
            print "negative test: killed subprocess:"
            sleep = Command("sleep 10")
            print "call sleep 10"
            sleep.echo()
            print "Error: killed process should raise exception"
            result = False
        except V7CommandException, e:
            print e
            sleep.printErrors()
            print "passed"
    
    # negative test: expect single line, get multiple
    try:
        print "negative test: more than one line of output"
        command = Command("who")
        print "who: %s" % command.getString()
        print "Error: multi-line output when one line is expected should raise exception"
        result = False
    except V7CommandException, e:
        print e
        
    # negative test: output on stderr
    try:
        print "negative test: output on stderr"
        command = Command("echo \"boguserror\" >&2; echo \"boguserror\"")
        print "error echo: %s" % command.getString(regex="boguserror", singleLine=False)
        print "Error: output on stderr should raise exception"
        result = False
    except V7CommandException, e:
        print e
        
    return result
    
if __name__ == "__main__":
    if not unitTest():
        print "command.py unit test FAILED"
        exit(1)
    print "command.py unit test passed"
    exit(0)
