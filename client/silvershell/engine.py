# Copyright 2008 Eloff Enterprises
#
# Licensed under the BSD License (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://silvershell.googlecode.com/files/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.
#
# Originally developed by Daniel Eloff.

import clr

clr.AddReference('IronPython')
clr.AddReference('Microsoft.Scripting')
clr.AddReference('Microsoft.Scripting.Core')

import sys

from event import Event

import System
from Microsoft.Scripting import SourceCodeKind, SourceCodePropertiesUtils, ScriptCodeParseResult
from Microsoft.Scripting.Hosting import ExceptionOperations
from System.Windows import Application
from System.Threading import ThreadPool

import wpf

import silvershell
from silvershell.history import History
from silvershell.prefs import Preferences

class SilverShellEngine(object):
    if sys.platform == 'silverlight':
        Engine = Application.Current.Runtime.GetEngine('py')
    else:
        from IronPython.Hosting import Python
        Engine = Python.CreateEngine()
        
    def __init__(self):
        self.namespace = {}
        self.namespace['wpf'] = wpf
        self.namespace['reset'] = self.reset
        self.history = History()
        self.background_execution = Preferences.BackgroundExecution
        
        self.Reset = Event()
        
    def write_banner(self):
        self.strm.write("%s (%s) on %s (.NET %s)\n" % (self.Engine.Setup.DisplayName, self.Engine.LanguageVersion.ToString(),
                                                        sys.platform.upper(), System.Environment.Version.ToString()))
        self.strm.write('SilverShell %s by %s. Type reset() to Clear.\n' % (silvershell.__version__, silvershell.__author__))
        
    def reset(self):
        ''' Resets the buffers and interpreter namespace. '''
        self.namespace = {}
        self.namespace['wpf'] = wpf
        self.namespace['reset'] = self.reset
        self.background_execution = Preferences.BackgroundExecution
        self.Reset(self, System.EventArgs())
        self.write_banner()
        
    def use_background_thread(self):
        print 'Switching execution to background thread.'
        self.background_execution = True
    
    def use_ui_thread(self):
        print 'Switching execution to main user-interface thread.'
        self.background_execution = False
    
    def allow_incomplete(self, lines):
        if not lines[-1].strip():
            lines[-1] = ''
            return True
        
        return False
    
    def is_complete(self, code, allow_incomplete):
        cmd = self.Engine.CreateScriptSourceFromString(code + '\n', SourceCodeKind.InteractiveCode)
        props = cmd.GetCodeProperties(self.Engine.GetCompilerOptions())
        if SourceCodePropertiesUtils.IsCompleteOrInvalid(props, allow_incomplete):
            return props != ScriptCodeParseResult.Empty
        else:
            return False
        
    def write_input(self, lines):
        self.strm.write(sys.ps1 + lines[0] + '\n')
        self.history.append(lines[0].lstrip())
        for line in lines[1:]:
            self.strm.write(sys.ps2 + line + '\n')
            self.history.append(line.lstrip())
    
    def run(self, code):
        lines = code.splitlines()
        if not lines:
            self.strm.write(sys.ps1 + '\n')
            return
        
        if self.is_complete(code, self.allow_incomplete(lines)):
            self.write_input(lines)
            
            args = (code, len(lines) > 1)
            if self.background_execution:
                ThreadPool.QueueUserWorkItem(self._run, args)
            else:
                self._run(args)
            
            return False
        else:
            return True
        
    def _run(self, args):
        code, multiline = args
        try:
            if multiline:
                self.run_multiline(code)
            else:
                self.run_singleline(code)
        except:
            self.handle_exception(sys.exc_info()[1])    
        
    def run_singleline(self, code):
        try:
            ret = eval(code, self.namespace)
        except SyntaxError:
            self.run_multiline(code)
        else:
            if ret is not None:
                self.strm.write(repr(ret) + '\n')
                if wpf.Dispatcher.CheckAccess():
                    self.namespace['_'] = ret

    def run_multiline(self, code):
        exec code in self.namespace
        
    def handle_exception(self, e):
        self.print_exception(e.clsException)
        
    def print_exception(self, clsException):
        exc_service = self.Engine.GetService[ExceptionOperations]()

        traceback = exc_service.FormatException(clsException)        
       
        lines = [line for line in traceback.splitlines() if 'in <string>' not in line and 'silvershell\\' not in line]
        if len(lines) == 2:
            lines = lines[1:]       
        
        sys.stderr.write('\n'.join(lines))
        if Preferences.ExceptionDetail:
            sys.stderr.write('\nCLR Exception: ')
            sys.stderr.write(clsException.ToString())
        
        sys.stderr.write('\n')
