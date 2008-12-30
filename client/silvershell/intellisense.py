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
import re

from System.Collections.Generic import List
from System.Windows.Threading import DispatcherTimer
from System import TimeSpan, Double

from silvershell.prefs import Preferences
from silvershell import utils

import wpf

class Intellisense(object):
    def __init__(self, engine, tbx):
        self.tbx = tbx        
        self.tbx.TextChanged += self.OnTextChanged
        self.tbx.LostFocus += self.OnLostFocus
        if sys.platform == 'cli':
            wpf.get_root_visual().Deactivated += self.OnLostFocus
        # Must come before other handlers
        if sys.platform == 'cli':
            self.tbx.PreviewKeyDown += self.OnKeyDown
        else:
            self.tbx.KeyDown += self.OnKeyDown 
        
        self.engine = engine
        
        self.re_obj = re.compile(r'(?P<obj>(?:[a-z_][a-z0-9_]*?\.)*)(?P<current>[a-z_][a-z0-9_]*?)?$', re.IGNORECASE)
        
        self.initialize()
        
    def initialize(self):
        self._prefix = ''
        self._show_calltip = None
        self.filterCompletions = False
        
        p = self.popup = wpf.Popup()
        if sys.platform == 'cli':
            p.PlacementTarget = wpf.get_root_visual()
            p.Placement = wpf.PlacementMode.Relative
        else:
            # Popup must be in tree in Silverlight
            grid = wpf.get_root_visual()
            grid.Children.Add(self.popup)
        
        self.calltip = Preferences.CallTip
        self.calltip_lbl = self.calltip.FindName('CallTipLabel')
        if not self.calltip_lbl:
            raise ValueError, 'No element named "CallTipLabel" in Preferences.CallTip'
        
        self.member_list = Preferences.MemberList
        self.member_lbx = self.member_list.FindName('MemberListBox')
        if not self.member_lbx:
            raise ValueError, 'No element named "MemberListBox" in Preferences.MemberList'
        
        self.member_lbx.SelectionChanged += self.OnSelectionChanged
        
    def Dispose(self):
        self.popup.IsOpen = False
        self.tbx.LostFocus -= self.OnLostFocus
        del self.tbx
        del self.popup
        
    def show(self, child):
        p = self.popup
        p.Child = child
        child.MaxHeight = Double.PositiveInfinity
        
        pos, end, line = utils.get_current_line(self.tbx)        
        self._prefix = self.tbx.Text[end-len(line):pos]
        
        wpf.on_first_layout(child, self.OnFirstLayout)
        
        p.IsOpen = True
        
    def hide(self):
        if self.popup.IsOpen:
            self.popup.IsOpen = False
        
    def complete(self):
        pos, end, line = utils.get_current_line(self.tbx)
            
        completion = self.find_completion(line[:pos])
        if completion is not None:
            self.tbx.Text = self.tbx.Text[:pos] + completion + self.tbx.Text[pos:]
            self.tbx.SelectionStart = pos + len(completion)
            return True
        
        return False
    
    def get_completions(self, s):
        m = self.re_obj.search(s)
        if m is not None:
            obj, current = m.group('obj', 'current')
            
            if obj:
                try:
                    o = eval(obj.rstrip('.'), self.engine.namespace)
                except:
                    return List[str](), 0, current or ''
                
                completions = List[str](dir(o))
            else:
                completions = List[str](self.engine.namespace.keys())
                
            completions.Sort()
            
            if not current:
                return completions, 0, ''
            
            i = completions.BinarySearch(current)
            if i < 0: # Partial match
                i = ~i
                
            return completions, i, current
        else:
            return List[str](), 0, current
            
    def find_completion(self, s):
        completions, i, current = self.get_completions(s)
        if completions:
            try:
                if completions[i] == current:
                    i += 1 # If the user wants a completion, it must be because this is also a prefix of something else
                    
                if not completions[i].startswith(current):
                    return
            except (ValueError, IndexError):
                return # i is past the end of the list, there are no matches            
            
            i += 1
            if i < completions.Count and completions[i].startswith(current):
                return
            
            return completions[i-1][len(current):] # Only one match!
        
    def update_member_list(self, line):
        lbx = self.member_lbx
        l = list(lbx.Items)
        m = self.re_obj.search(line)
        if m is not None:
            current = m.group('current')
            if current is None:
                if not m.group('obj'):
                    self.hide()
                    return # No match
                    
                current = '__zzzzzzz' # Go to after the __members__
                
            items = self.member_lbx.ItemsSource
            i = items.BinarySearch(current)
            if i < 0:
                i = ~i
                
            if i >= items.Count:
                i = items.Count-1
                
            if items[i].startswith(current):
                self.member_lbx.SelectedIndex = i
            else:
                self.member_lbx.SelectedIndex = -1
                
            self.member_lbx.ScrollIntoView(items[i])
        else:
            self.hide()
            
    def show_calltip(self, line):
        m = self.re_obj.search(line)
        if m is not None:
            obj = m.group()
            try:
                o = eval(obj, self.engine.namespace)
            except:
                pass
            else:                                   
                if callable(o):
                    self._show_calltip = o
                    tip = utils.get_calltip(o, self.OnGetCallTip)
                    
    def show_member_list(self, line, filter_completions=False):        
        if filter_completions:
            completions = False
            m = self.re_obj.search(line)
            if m is not None:
                current = m.group('current')
                if current is not None:
                    completions = List[str]([c for c in filter_completions if c.startswith(current)])
        else:
            completions = self.get_completions(line)[0]
        
        if completions:
            if len(completions) > Preferences.MaxCompletions:
                self.filterCompletions = completions
                self._prefix = ''
                return # Too many to show for now
                
            self.member_lbx.ItemsSource = completions
            self.show(self.member_list)
            
    def complete_from_member_list(self):
        if self.member_lbx.SelectedItem:
            pos, end, line = utils.get_current_line(self.tbx)
        
            start = end-len(line)
            s = ''.join(self._prefix.rpartition('.')[:2]) + self.member_lbx.SelectedItem 
            self.tbx.Text = self.tbx.Text[:start] + s + self.tbx.Text[pos:]
            self.tbx.SelectionStart = start + len(s)
            
            self.hide()
            return True
        else:
            self.hide()
            return False
        
    def OnGetCallTip(self, obj, tip):
        if self._show_calltip is obj and tip:
            self.calltip_lbl.Text = tip
            self.show(self.calltip)
        
    def OnKeyDown(self, sender, e):
        if self.popup.IsOpen and self.popup.Child is self.member_list:
            if e.Key in (wpf.Key.Tab, wpf.Key.Enter):
                e.Handled = self.complete_from_member_list()
            elif e.Key == wpf.Key.Down:
                e.Handled = True
                if self.member_lbx.SelectedIndex == -1:
                    i = ~self.member_lbx.ItemsSource.BinarySearch('__zzzzzzz')
                    if i == self.member_lbx.Items.Count:
                        i -= 1
                        
                    self.member_lbx.SelectedIndex = i
                elif self.member_lbx.SelectedIndex < self.member_lbx.Items.Count - 1:
                    self.member_lbx.SelectedIndex += 1
                else:
                    return
                
                self.member_lbx.ScrollIntoView(self.member_lbx.SelectedItem)                
            elif e.Key == wpf.Key.Up:
                e.Handled = True
                if self.member_lbx.SelectedIndex > 0:
                    self.member_lbx.SelectedIndex -= 1
                    self.member_lbx.ScrollIntoView(self.member_lbx.SelectedItem)
                
    
    def OnTextChanged(self, sender, e):
        completions = self.filterCompletions
        self.filterCompletions = False
        pos, end, line = utils.get_current_line(self.tbx)
        
        if self.popup.IsOpen and self._prefix not in line:
            self.hide()
        
        if pos > 0:
            start = end - len(line)
            if self.tbx.Text[pos-1] == '.' and pos > 1:
                if self.tbx.Text[pos-2].isalnum() or self.tbx.Text[pos-2] == '_':
                    self.show_member_list(line[:pos-start])                                                    
            elif self.tbx.Text[pos-1] == '(':
                self.hide()
                self.show_calltip(line[:pos-start-1])
            elif self.tbx.Text[pos-1] == ')':
                self._show_calltip = None
                self.hide()
            elif '.' in line:
                if completions:
                    self.show_member_list(line[:pos-start], completions)
                elif self.popup.IsOpen and self.popup.Child is self.member_list:
                    self.update_member_list(line[:pos-start])
                
    def OnLostFocus(self, sender, e):
        self.hide()
        
    def OnFirstLayout(self, sender, e):
        p = self.popup
        if p.IsOpen:
            child = p.Child
            rv = wpf.get_root_visual()
            pos, end, line = utils.get_current_line(self.tbx)
            offset = wpf.get_position(self.tbx)   
            sz = wpf.measure_string(self._prefix, self.tbx.FontFamily, self.tbx.FontSize)
            desired_sz = wpf.measure(child)
            
            p.VerticalOffset = offset.Y + (self.tbx.Text[:pos].count('\n')+1) * sz.Height
            if p.VerticalOffset > rv.ActualHeight/2:
                # Display above the line
                p.VerticalOffset -= desired_sz.Height + sz.Height
                if p.VerticalOffset < 10:
                    child.MaxHeight = desired_sz.Height - (10 - p.VerticalOffset)
                    p.VerticalOffset = 10
            elif p.VerticalOffset + desired_sz.Height + 10 > rv.ActualHeight:
                child.MaxHeight = rv.ActualHeight - p.VerticalOffset - 10
            
            p.HorizontalOffset = offset.X + sz.Width
            if p.HorizontalOffset + desired_sz.Width > rv.ActualWidth-10:
                # Display further left
                p.HorizontalOffset = rv.ActualWidth - 10 - desired_sz.Width
                
            if p.Child is self.member_lbx:
                start = end - len(line)
                self.update_member_list(line[:pos-start])
        
    def OnSelectionChanged(self, sender, e):
        obj = wpf.get_focused()
        if obj is not self.tbx:
            # Surprise, surprise this event is too early to be useful...
            # FIXME: Must be a less hackish way to get this working
            t = DispatcherTimer()
            t.Interval = TimeSpan.FromSeconds(0.1)
            
            def OnTick(sender, e):
                self.complete_from_member_list()
                self.tbx.Focus()
                t.Stop()
            
            t.Tick += OnTick
            t.Start()
            
            
            
                
    