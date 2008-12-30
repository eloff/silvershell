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

from System import TimeSpan

import clr

import wpf
       
def startup():
    wpf.Application.Current.RootVisual = wpf.Grid()
    
    from silvershell.shell import SilverShell
    ss = SilverShell()
    wpf.Application.Current.RootVisual.Children.Add(ss.GetVisualRoot())
    
    def OnLoad(sender, e):
        ss.start()
        
    wpf.on_first_layout(wpf.Application.Current.RootVisual, OnLoad)
    
startup()
