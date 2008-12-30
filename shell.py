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

import sys

sys.path.append('client')
sys.path.append('lib')

import clr
# Reference the WPF assemblies
clr.AddReferenceByName("PresentationFramework, Version=3.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35")
clr.AddReferenceByName("PresentationCore, Version=3.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35")
clr.AddReference('WindowsBase')
clr.AddReference('System.Xml')

import wpf

from System import TimeSpan

def main():
    window = wpf.Window()
    window.Title = 'SilverShell'
    
    wpf.FocusManager.SetIsFocusScope(window, True)
    
    app = wpf.Application()
    app.MainWindow = window
       
    def OnLoad(sender, e):
        from silvershell.shell import SilverShell
    
        ss = SilverShell()    
        window.Content = ss.GetVisualRoot()
        window.Show()
        
        ss.start()        

    app.Startup += OnLoad
    
    app.Run()
    
if __name__ == '__main__':
    main()
    
    