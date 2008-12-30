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
import os

from event import Event

from System import EventArgs
from System.IO import FileNotFoundException, FileMode, FileAccess, StreamWriter, StreamReader
from System.IO.IsolatedStorage import IsolatedStorageFile, IsolatedStorageFileStream

import silvershell
from silvershell import utils

import wpf

class Preferences(object):
    def __init__(self):
        self.current_preferences = {}
        
        self.Changed = Event()
        
        self.loaded = False
        
    def initialize(self):
        p = self.root = wpf.Popup()
        
        p.Child = utils.load_xaml('''
            <Border 
                xmlns="%(client_ns)s"
                Background="Black"
                BorderThickness="2"
                >
                <Border.BorderBrush>
                    <LinearGradientBrush StartPoint="0.5,0" EndPoint="0.5,1">
                        <GradientStop Color="#B2FFFFFF" Offset="0"/>
                        <GradientStop Color="#66FFFFFF" Offset="0.325"/>
                        <GradientStop Color="#1EFFFFFF" Offset="0.325"/>
                        <GradientStop Color="#51FFFFFF" Offset="1"/>
                    </LinearGradientBrush>
                </Border.BorderBrush>
            </Border>''')
        
        self.prefs = wpf.TextBox()
        self.prefs.AcceptsReturn = True
        self.prefs.TextWrapping = wpf.TextWrapping.Wrap
        self.prefs.VerticalScrollBarVisibility = wpf.ScrollBarVisibility.Auto
        self.prefs.FontSize = 14
        self.prefs.FontFamily = wpf.FontFamily('Courier New')
        self.prefs.FontWeight = wpf.FontWeights.Bold
        
        g = self.grid = self.root.Child.Child = wpf.Grid()
        g.Background = wpf.brush('#ffffff')
        
        rd = wpf.RowDefinition()
        rd.Height = wpf.GridLength(1, wpf.GridUnitType.Star)
        g.RowDefinitions.Add(rd)
        rd = wpf.RowDefinition()
        rd.Height = wpf.GridLength(0, wpf.GridUnitType.Auto)
        g.RowDefinitions.Add(rd)
            
        cd = wpf.ColumnDefinition()
        cd.Width = wpf.GridLength(0, wpf.GridUnitType.Auto)
        g.ColumnDefinitions.Add(cd)
        cd = wpf.ColumnDefinition()
        cd.Width = wpf.GridLength(1, wpf.GridUnitType.Star)
        g.ColumnDefinitions.Add(cd)
        cd = wpf.ColumnDefinition()
        cd.Width = wpf.GridLength(1, wpf.GridUnitType.Star)
        g.ColumnDefinitions.Add(cd)
        cd = wpf.ColumnDefinition()
        cd.Width = wpf.GridLength(0, wpf.GridUnitType.Auto)
        g.ColumnDefinitions.Add(cd)
        
        m = wpf.Thickness(5)
        
        b = wpf.Button()
        b.Margin = m
        b.Content = 'Restore Defaults'
        b.Click += self.OnRestoreDefaultsClick
        
        wpf.Grid.SetColumn(b, 0)
        wpf.Grid.SetRow(b, 1)
        g.Children.Add(b)
        
        b = wpf.Button()
        b.Margin = m
        b.Content = 'Apply & Save'
        b.Width = 120
        b.HorizontalAlignment = wpf.HorizontalAlignment.Center
        b.Click += self.OnApplyAndSaveClick
        
        wpf.Grid.SetColumn(b, 1)
        wpf.Grid.SetRow(b, 1)
        g.Children.Add(b)
        
        b = wpf.Button()
        b.Margin = m
        b.Content = 'Load Theme'
        b.Width = 120
        b.HorizontalAlignment = wpf.HorizontalAlignment.Center
        #b.Click += self.OnLoadThemeClick
        
        wpf.Grid.SetColumn(b, 2)
        wpf.Grid.SetRow(b, 1)
        g.Children.Add(b)
        
        b = wpf.Button()
        b.Margin = m
        b.Content = 'Close'
        b.Click += self.OnCloseClick
        
        wpf.Grid.SetColumn(b, 3)
        wpf.Grid.SetRow(b, 1)
        g.Children.Add(b)
        
        wpf.Grid.SetColumn(self.prefs, 0)
        wpf.Grid.SetRow(self.prefs, 0)
        wpf.Grid.SetColumnSpan(self.prefs, 4)
        g.Children.Add(self.prefs)
              
        # Center popup
        if sys.platform == 'silverlight':
            p.Opened += self.OnPopupOpened
        else:
            p.PlacementTarget = wpf.get_root_visual()
            p.Placement = wpf.PlacementMode.Center
        
    def show(self):
        self.root.Child.Width = wpf.get_root_visual().ActualWidth - 140
        self.root.Child.Height = wpf.get_root_visual().ActualHeight - 100
        self.root.Child.UpdateLayout()
        self.root.IsOpen = True
        
    def hide(self):
        self.root.IsOpen = False
        
    def load(self):
        self.initialize()
        store = IsolatedStorageFile.GetUserStoreForApplication()
        try:
            if store.FileExists('preferences.py'):
                strm = store.OpenFile('preferences.py', FileMode.Open, FileAccess.Read)
                try:
                    strm = StreamReader(strm)
                    self.prefs.Text = strm.ReadToEnd()
                    self.execute()
                finally:
                    strm.Close()
            else:
                self.load_defaults()                
        finally:
            store.Dispose()
            
    def execute(self):
        new_prefs = {}
        exec self.prefs.Text in new_prefs
        self.current_preferences = new_prefs
        self.loaded = True
        self.Changed(self, EventArgs())
            
    def execute_and_save(self):
        self.execute()
        
        store = IsolatedStorageFile.GetUserStoreForApplication()
        try:
            strm = store.CreateFile('preferences.py')
            try:
                strm = StreamWriter(strm)
                strm.Write(self.prefs.Text)
            finally:
                strm.Close()
        finally:
            store.Dispose()
    
    def load_defaults(self):
        f = open(os.path.join(os.path.dirname(__file__.replace('\\', '/')), silvershell.PREFERENCES))
        try:
            code = f.read()
        finally:
            f.close()
            
        self.prefs.Text = code
        self.execute()
        self.delete_preferences()
        
    def delete_preferences(self):
        store = IsolatedStorageFile.GetUserStoreForApplication()
        try:
            if store.FileExists('preferences.py'):
                store.DeleteFile('preferences.py')
        finally:
            store.Dispose()            
       
    def apply_to(self, obj, pref, attr=None):
        value = getattr(self, pref, None)
        if value is not None:
            setattr(obj, attr or pref, value)
        
    def apply_style_to(self, obj, pref):
        self.apply_to(obj, pref, 'Style')
        
    def __getattr__(self, attr):
        if not self.loaded:
            self.load()
            
        if attr in self.current_preferences:
            return self.current_preferences[attr]
        
        raise AttributeError, attr
    
    def OnRestoreDefaultsClick(self, sender, e):
        self.load_defaults()
    
    def OnApplyAndSaveClick(self, sender, e):
        self.execute_and_save()
    
    def OnCloseClick(self, sender, e):
        self.hide()        
       
    def OnPopupOpened(self, sender, e):
        wpf.center_popup(self.root)
        
if sys.platform == 'silverlight':
    Preferences = Preferences()
else:
    # The API is so different for isolated storage in WPF, that it makes no sense to use it
    from System.IO import File
    
    save_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), r'..\..\data'))
    pref_file = os.path.join(save_dir, 'preferences.py')
    
    class WPFPreferences(Preferences):
        def load(self):
            self.initialize()
            if File.Exists(pref_file):
                f = open(pref_file, 'rb')
                try:
                    self.prefs.Text = f.read().replace('\r\n', '\n').replace('\r', '\n')
                    self.execute()
                finally:
                    f.close()
            else:
                self.load_defaults()
        
        def execute_and_save(self):
            self.execute()
            
            f = open(pref_file, 'wb')
            try:
                f.write(self.prefs.Text)
            finally:
                f.close()
            
        def delete_preferences(self):
            if File.Exists(pref_file):
                File.Delete(pref_file)
            
    Preferences = WPFPreferences()
        