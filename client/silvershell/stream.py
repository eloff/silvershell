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

import wpf

from silvershell import utils

class TextBoxStream(object):
    def __init__(self, tbx):
        self.tbx = tbx
        
        self._prepend_newline = False
        
        self.DataWritten = self.tbx.TextChanged
        
    def write(self, s):
        if s:
            if wpf.Dispatcher.CheckAccess():
                s = self.fix_newlines(s)
                self.tbx.Text += s
            else:
                utils.io_dispatch(self.write, s)
                
    def fix_newlines(self, s):
        # Normalize newlines
        s = s.replace('\r\n', '\n').replace('\r', '\n')
        
        if self._prepend_newline:
            prefix = '\n'
            self._prepend_newline = False
        else:
            prefix = ''
        
        if s[-1] == '\n':
            self._prepend_newline = True
            s = s[:-1]
            
        return prefix + s 
    
    def reset(self):
        self.tbx.Text = ''
        self._prepend_newline = False
