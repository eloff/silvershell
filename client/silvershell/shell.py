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
import itertools

import wpf

from silvershell.stream import TextBoxStream
from silvershell.engine import SilverShellEngine
from silvershell import utils
from silvershell.prefs import Preferences
from silvershell.intellisense import Intellisense
from silvershell.cursor import Cursor

class SilverShell(object):
    def __init__(self):
        self.engine = SilverShellEngine()
        
        self.initialize()
        
        self.engine.namespace['canvas'] = self.canvas
        self.engine.write_banner()
        
        self.engine.Reset += self.OnEngineReset
        Preferences.Changed += self.OnPreferencesChanged
    
    def initialize(self):
        prefs = Preferences
        
        self.ignore_text_changed = False
        
        g = self.root = wpf.Grid()
        
        cd = wpf.ColumnDefinition()
        cd.Width = wpf.GridLength(1, wpf.GridUnitType.Star)
        g.ColumnDefinitions.Add(cd)
        cd = wpf.ColumnDefinition()
        cd.Width = wpf.GridLength(0, wpf.GridUnitType.Auto)
        g.ColumnDefinitions.Add(cd)        
        
        self.canvas = wpf.Create(wpf.Canvas, Grid_Row=0, Grid_Column=1, Background=wpf.brush(wpf.Colors.White), Margin=wpf.Thickness(5,0,0,0))
        g.Children.Add(self.canvas)
        
        self.sv = wpf.Create(wpf.ScrollViewer, Grid_Row=0, Grid_Column=0, Padding=wpf.Thickness(5))
        g.Children.Add(self.sv)
        
        g.Children.Add(wpf.Create(wpf.GridSplitter, Grid_Row=0, Grid_Column=1, Width=5,
                                  HorizontalAlignment=wpf.HorizontalAlignment.Left,
                                  VerticalAlignment=wpf.VerticalAlignment.Stretch, Background=wpf.brush(wpf.Colors.MidnightBlue)))
        
        prefs.apply_to(g, 'BackgroundImage', 'Background')
        prefs.apply_to(self.sv, 'BackgroundMask', 'Background') 
        
        g = self.sv.Content = wpf.Grid()
        
        rd = wpf.RowDefinition()
        rd.Height = wpf.GridLength(0, wpf.GridUnitType.Auto)
        g.RowDefinitions.Add(rd)
        rd = wpf.RowDefinition()
        rd.Height = wpf.GridLength(1, wpf.GridUnitType.Auto)
        g.RowDefinitions.Add(rd)
                    
        cd = wpf.ColumnDefinition()
        cd.Width = wpf.GridLength(0, wpf.GridUnitType.Auto)
        g.ColumnDefinitions.Add(cd)
        cd = wpf.ColumnDefinition()
        cd.Width = wpf.GridLength(1, wpf.GridUnitType.Star)
        g.ColumnDefinitions.Add(cd)
        
        self.buffer = wpf.TextBox()
        self.prompt = wpf.TextBox()
        self.ps = wpf.TextBlock()
        self.ps.Text = sys.ps1
        
        self.buffer.AcceptsReturn = self.prompt.AcceptsReturn = True
        self.buffer.TextWrapping = wpf.TextWrapping.Wrap
        self.buffer.IsReadOnly = True
        
        if sys.platform == 'silverlight':
            self.prompt.SelectionForeground = self.buffer.SelectionForeground = wpf.brush('#000000')
            self.prompt.SelectionBackground = self.buffer.SelectionBackground = wpf.brush('#00ffff')
        else:
            self.ps.Margin = wpf.Thickness(2,0,0,0)
            
        prefs.apply_style_to(self.buffer, 'TextBoxStyle')
        prefs.apply_style_to(self.prompt, 'TextBoxStyle')       
        
        for tbx in (self.buffer, self.prompt, self.ps):
            prefs.apply_to(tbx, 'FontSize')
            prefs.apply_to(tbx, 'FontFamily')
            prefs.apply_to(tbx, 'FontWeight')
            prefs.apply_to(tbx, 'Foreground')
            
        wpf.Grid.SetColumn(self.buffer, 0)
        wpf.Grid.SetColumnSpan(self.buffer, 2)
        wpf.Grid.SetRow(self.buffer, 0)
        g.Children.Add(self.buffer)
        
        wpf.Grid.SetColumn(self.ps, 0)
        wpf.Grid.SetRow(self.ps, 1)
        g.Children.Add(self.ps)
        
        wpf.Grid.SetColumn(self.prompt, 1)
        wpf.Grid.SetRow(self.prompt, 1)
        g.Children.Add(self.prompt)
        
        pnl = wpf.Create(wpf.StackPanel, Grid_Row=0, Grid_Column=1,
                         Orientation=wpf.Orientation.Vertical,
                         HorizontalAlignment=wpf.HorizontalAlignment.Right,
                         VerticalAlignment=wpf.VerticalAlignment.Top)
        
        btn = wpf.Create(wpf.Button, Content='Preferences')
        prefs.apply_style_to(btn, 'ButtonStyle')
        btn.Click += self.OnPreferencesClick
        pnl.Children.Add(btn)
        
        btn = wpf.Create(wpf.Button, Content=('Background Thread' if prefs.BackgroundExecution else 'UI Thread'))
        prefs.apply_style_to(btn, 'ButtonStyle')
        btn.Click += self.OnChangeThread
        pnl.Children.Add(btn)
        
        g.Children.Add(pnl)
        
        self.redirect_stdstreams()
        
        self.cursor = Cursor(self.prompt, self.sv)
        
        self.intellisense = Intellisense(self.engine, self.prompt) # Must come before other KeyDown handlers
        if sys.platform == 'cli':
            self.prompt.PreviewKeyDown += self.OnKeyDown
        else:
            self.prompt.KeyDown += self.OnKeyDown
            
        self.prompt.TextChanged += self.OnTextChanged
        
    def Dispose(self):
        self.cursor.Dispose()
        self.intellisense.Dispose()
        
    def redirect_stdstreams(self):        
        self.engine.strm = sys.stdout = TextBoxStream(self.buffer)
        #sys.stderr = sys.stdout # comment this out to see exceptions at system console
        
    def start(self):
        self.ps.Text = sys.ps1
        self.prompt.Text = ''
        self.prompt.Focus()
        
    def scroll_to_bottom(self):
        self.sv.UpdateLayout()
        if self.sv.ViewportHeight:
            self.sv.ScrollToVerticalOffset(self.sv.ScrollableHeight)
            
    def fix_paste(self):
        l = []
        for line in self.prompt.Text.splitlines():
            if line.startswith((sys.ps1, sys.ps2)):
                line = line[4:]
            
            l.append(line)
            
        self.prompt.Text = '\n'.join(l)
        self.prompt.SelectionStart = len(self.prompt.Text)
            
    def indent(self):
        pos, end, line = self.get_current_line()
        # Don't insert indentation unless we're at the beginning of the line
        if not self.prompt.Text[end-len(line):pos].strip():
            self.prompt.Text = self.prompt.Text[:pos] + ' '*4 + self.prompt.Text[pos:]
            self.prompt.SelectionStart = pos+4
        
    def get_current_line(self):
        return utils.get_current_line(self.prompt)
    
    def history(self, delta=None):
        pos, end, line = self.get_current_line()
        # Don't insert a history item unless we're at an empty line, or the line is located in history
        if delta is not None and line.strip() and line.lstrip() not in self.engine.history:
            return False
        else:
            # Preserve the indentation
            indent = line[:-len(line.lstrip())] if line.strip() else line
            start = end - len(line)
            if delta is None:
                try:
                    history = self.engine.history.find(line)
                except ValueError:
                    return True
            else:
                history = self.engine.history.go(delta)
                
            line = indent + history 
            self.prompt.Text = self.prompt.Text[:start] + line + self.prompt.Text[end:]
            self.prompt.SelectionStart = start + len(line)
            return True  
        
    def clear_prompt(self):
        self.prompt.Text = ''
        self.ps.Text = sys.ps1
        self.scroll_to_bottom()
        self.cursor.update()
        
    def continue_prompt(self):
        self.ignore_text_changed = True
        self.ps.Text += '\n' + sys.ps2
        pos = self.prompt.SelectionStart
        self.prompt.Text = self.prompt.Text[:pos] + '\n' + ' '*4 + self.prompt.Text[pos:]
        self.prompt.SelectionStart = pos + 5
        self.scroll_to_bottom()
        self.ignore_text_changed = False
        
    def interpret(self):
        if not self.engine.run(self.prompt.Text):
            self.clear_prompt()
        else:
            self.continue_prompt()
            
    def OnEngineReset(self, sender, e):
        sys.stdout.reset()
        self.engine.namespace['canvas'] = self.canvas
        self.start()
        
    def OnKeyDown(self, sender, e):
        if e.Key == wpf.Key.Enter:
            self.interpret()
            e.Handled = True # we insert the newline ourselves
        elif e.Key == wpf.Key.Up:
            e.Handled = self.history(-1)
        elif e.Key == wpf.Key.Down:
            e.Handled = self.history(1)
        elif e.Key == wpf.Key.Tab:
            if wpf.Keyboard.Modifiers & wpf.ModifierKeys.Shift:
                e.Handled = self.history()
            else:
                e.Handled = self.intellisense.complete()
                if not e.Handled:
                    self.indent()            
                    e.Handled = True
            
    def OnTextChanged(self, sender, e):
        if not self.ignore_text_changed:
            num_lines = self.prompt.Text.count('\n') + 1
            ps_lines = self.ps.Text.count('\n') + 1
            if num_lines != ps_lines:
                self.ps.Text = '\n'.join(itertools.islice(itertools.chain(
                    self.ps.Text.splitlines(), itertools.repeat(sys.ps2)), num_lines))
                
                if num_lines > ps_lines:
                    # Maybe a paste, so we have to remove prompts and normalize newlines
                    self.fix_paste()
                
    def OnPreferencesClick(self, sender, e):
        Preferences.show()
        
    def OnChangeThread(self, sender, e):
        if sender.Content == 'UI Thread':
            sender.Content = 'Background Thread'
            self.engine.use_background_thread()
        else:
            sender.Content = 'UI Thread'
            self.engine.use_ui_thread()  
        
    def OnPreferencesChanged(self, sender, e):
        parent = self.root.Parent
        self.Dispose()
        self.initialize()
        wpf.LogicalTree.SetContent(parent, self.root)
        self.engine.reset()
        
    def GetVisualRoot(self):
        return self.root
    
    