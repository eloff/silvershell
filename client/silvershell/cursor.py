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

# All the trouble I have to go to in order to get a
# customizable (or even visible) cursor in a TextBox...

import sys

from System import TimeSpan
from System.Windows.Threading import DispatcherTimer

from silvershell.prefs import Preferences
from silvershell import utils

import wpf

class Cursor(object):
    def __init__(self, tbx, bounding_sv):
        self.tbx = tbx
        self.bounding_sv = bounding_sv # TODO: use to hide cursor when it is out of bounds
        
        self.initialize()
        
        self.tbx.GotFocus += self.OnGotFocus
        self.tbx.LostFocus += self.OnLostFocus
        self.tbx.LayoutUpdated += self.OnUpdateCursor
        if sys.platform == 'cli':
            rv = wpf.get_root_visual()
            rv.LocationChanged += self.OnLocationChanged
            rv.Deactivated += self.OnLostFocus
            rv.Activated += self.OnGotFocus
    
    def initialize(self):
        self._can_update = False
        
        p = self.popup = wpf.Popup()
        if sys.platform == 'cli':
            p.PlacementTarget = wpf.get_root_visual()
            p.Placement = wpf.PlacementMode.Relative
            
        self.cursor = wpf.Rectangle()
        sz = wpf.measure_string('|', Preferences.FontFamily, Preferences.FontSize)
        self.cursor.Width = 2
        self.cursor.Height = sz.Height
        self.cursor.Fill = wpf.brush('#ffffff')
        
        p.Child = self.cursor
        
        self.sb = wpf.Storyboard()
                
        self.sb.AutoReverse = True
        self.sb.RepeatBehavior = wpf.RepeatBehavior.Forever
        
        anim = Preferences.CursorAnimation
        
        if sys.platform == 'silverlight':
            wpf.Storyboard.SetTarget(anim, self.cursor)
        
        self.sb.Children.Add(anim)
        
        self.popup.Opened += self.OnPopupOpened
        
    def Dispose(self):
        self._can_update = False
        self.sb.Stop()
        self.popup.IsOpen = False
        self.tbx.LostFocus -= self.OnLostFocus
        self.tbx.GotFocus -= self.OnGotFocus        
        self.tbx.LayoutUpdated -= self.OnUpdateCursor
        if sys.platform == 'cli':
            rv = wpf.get_root_visual()
            rv.LocationChanged -= self.OnLocationChanged
            rv.Deactivated -= self.OnLostFocus
            rv.Activated -= self.OnGotFocus
        del self.tbx
        del self.popup
        del self.sb
        
    def update(self):
        self.OnUpdateCursor()
        
    def hide(self):
        self.sb.Stop()
        self.popup.IsOpen = False

    def show(self):        
        self.popup.IsOpen = True
        self.update()
                
    def OnPopupOpened(self, sender, e):
        if sys.platform == 'silverlight':
            self.sb.Begin()
        else:
            self.sb.Begin(self.cursor)
            
    def OnLocationChanged(self, sender, e):
        self.update()
        p = self.popup
        # Dirty hack to force popup to move
        p.IsOpen = False
        p.IsOpen = True
        
    def OnGotFocus(self, sender, e):
        self._can_update = True
        self.show()
        
    def OnLostFocus(self, sender, e):
        self.hide()
        self._can_update = False
        
    def OnUpdateCursor(self, *ignore):
        if self._can_update:
            p = self.popup
            offset = wpf.get_position(self.tbx)            
            pos, end, line = utils.get_current_line(self.tbx)
            sz = wpf.measure_string(self.tbx.Text[end-len(line):pos], self.tbx.FontFamily, self.tbx.FontSize)
        
            x = offset.X + sz.Width
            y = offset.Y + self.tbx.Text[:pos].count('\n') * sz.Height
            
            if x != p.HorizontalOffset:
                p.HorizontalOffset = x
            if y != p.VerticalOffset:
                p.VerticalOffset = y
            
            # Check if the cursor is out of bounds or if the textbox is hidden
            
            cursor_pos = wpf.Point(x, y)
            bounds = wpf.Rect(wpf.get_position(self.bounding_sv), wpf.Size(self.bounding_sv.ViewportWidth, self.bounding_sv.ViewportHeight))
            if bounds.Contains(wpf.Point(cursor_pos.X, cursor_pos.Y + self.cursor.ActualHeight/2)) and bounds.Contains(offset):
                if not p.IsOpen:
                    self.show()
            else:
                if p.IsOpen:
                    self.hide()
            
        
    
        
        
        