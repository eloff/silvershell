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
clr.AddReference('System.Core')

import wpf

from System import Action, Array
from System.Windows.Markup import XamlReader
from System.Threading import ThreadPool, WaitCallback, Monitor

import sys
from cStringIO import StringIO

from System.Windows import Application

if sys.platform == 'silverlight':
    xaml_client_ns = 'http://schemas.microsoft.com/client/2007'
else:
    xaml_client_ns = 'http://schemas.microsoft.com/winfx/2006/xaml/presentation'
    from System.Xml import XmlReader
    from System.IO import StringReader
    
def load_xaml(xaml):
    xaml %= {'client_ns' : xaml_client_ns}
    
    if sys.platform == 'silverlight':
        return XamlReader.Load(xaml)
    else:
        return XamlReader.Load(XmlReader.Create(StringReader(xaml)))

def get_calltip(obj, callback):
    if sys.platform == 'silverlight' and isinstance(obj, type) and issubclass(obj, wpf.Control):
        callback(obj, None) # FIXME: ipy bug #19855
            
    ThreadPool.QueueUserWorkItem(_get_calltip, (obj, callback))
    
_lock = object()

def io_dispatch(func, s):
    Monitor.Enter(_lock)
    try:
        dispatch(func, s)
    finally:
        Monitor.Exit(_lock)

def dispatch(func, *args):    
    action = Action.__getitem__(*[object]*len(args))
    wpf.Dispatcher.BeginInvoke(action(func), Array[object](args))
    
def _get_calltip(args):
    obj, callback = args
    
    Monitor.Enter(_lock)
    stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        help(obj)
        tip = sys.stdout.getvalue().strip().replace('\r\n', '\r').replace('\r', '\n')
        dispatch(callback, obj, tip)
    finally:
        sys.stdout = stdout
        Monitor.Exit(_lock)

def get_current_line(tbx):
    pos = tbx.SelectionStart + tbx.SelectionLength
    if pos > 0:
        i = 0
        for line in tbx.Text.splitlines():
            i += len(line) + 1
            if i > pos:
                return pos, i-1, line
        
        if i == pos:
            return pos, i, ''
            
    return 0, 0, ''

def html_to_color(s):
    s = s.lstrip('#')
    c = []
    if len(s) == 6:
        c.append(0xff) # add alpha channel at full opacity
    
    c.extend(int(s[i:i+2], 16) for i in xrange(0, len(s), 2))
    return wpf.Color.FromArgb(*c)