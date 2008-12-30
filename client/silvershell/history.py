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

from silvershell import utils

class History(object):
    def __init__(self):
        self.history = ['']

        self.reset_cursor()

    def append(self, line):
        if line != self.history[-1]:
            self.history.append(line)

        self.reset_cursor()

    def reset_cursor(self):
        self.cursor = 0
        
    def __contains__(self, line):
        return line in self.history
        
    def go(self, delta):
        if (delta < 0 and self.cursor > -len(self.history)) or (delta > 0 and self.cursor < 0):
            self.cursor += delta
            
        return self.history[self.cursor]
    
    def find(self, line):
        needle = line.strip()
        for line in reversed(self.history):
            if line.startswith(needle):
                return line
            
        raise ValueError, 'Could not find matching history item.'
    