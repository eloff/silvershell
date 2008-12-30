/*
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
 */

using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Controls.Primitives;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using IronPython.Runtime;

[assembly: PythonModule("_wpf", typeof(_wpf.wpf))]
namespace _wpf
{
    public static partial class wpf
    {
        public static readonly Dispatcher Dispatcher = new ContentControl().Dispatcher;

        public static Color html_to_color(string s)
        {
            int pos = 0;
            s = s.TrimStart(new[] {'#'});
            byte alpha = 0xff;
            if (s.Length == 8)
            {
                alpha = byte.Parse(s.Substring(0, 2), NumberStyles.AllowHexSpecifier);
                pos = 2;
            }
            else if (s.Length != 6)
                throw new ArgumentException("Expected a 6-8 digit hexadecimal color code.", "s");

            return Color.FromArgb(alpha, byte.Parse(s.Substring(pos, 2), NumberStyles.AllowHexSpecifier),
                                  byte.Parse(s.Substring(pos + 2, 2), NumberStyles.AllowHexSpecifier),
                                  byte.Parse(s.Substring(pos + 4, 2), NumberStyles.AllowHexSpecifier));
        }

        public static SolidColorBrush brush(string color)
        {
            return brush(html_to_color(color));
        }

        public static SolidColorBrush brush(Color color)
        {
            return new SolidColorBrush { Color = color };
        }

        public static ImageBrush image_brush(string path)
        {
#if SILVERLIGHT
            return new ImageBrush { ImageSource = new BitmapImage(new Uri(path, UriKind.RelativeOrAbsolute)) };
#else
            BitmapImage img = new BitmapImage();
            img.BeginInit();
            img.StreamSource = new MemoryStream(File.ReadAllBytes(path.TrimStart(new[] {'\\', '/'})));
            img.EndInit();
            return new ImageBrush { ImageSource = img };
#endif
        }

        private static readonly Size _infsize = new Size(Double.MaxValue, Double.MaxValue);

        public static Size measure(FrameworkElement el)
        {
            el.Measure(_infsize);
            return el.DesiredSize;
        }

        public static Size measure_string(string s, FontFamily font_family, double font_size)
        {
            TextBlock t = new TextBlock { Text = s, FontFamily = font_family, FontSize = font_size };
#if SILVERLIGHT
            Size sz = new Size(t.ActualWidth, t.ActualHeight);
#else
            Size sz = measure(t);
#endif
            return s.Length != 0 ? sz : new Size(0, sz.Height);
        }

        public static UIElement get_root_visual()
        {
#if SILVERLIGHT
            return Application.Current.RootVisual;
#else
            return Application.Current.MainWindow;
#endif
        }

        private static readonly Point _origin = new Point(0, 0);

        public static Point get_position(UIElement el)
        {
            return get_position(el, _origin);
        }

        public static Point get_position(UIElement el, Point refPoint)
        {
            UIElement rv = get_root_visual();
            return rv == null ? refPoint : el.TransformToVisual(rv).Transform(refPoint);
        }

        public static object get_focused()
        {
#if SILVERLIGHT
            return FocusManager.GetFocusedElement();
#else
            return FocusManager.GetFocusedElement(get_root_visual());
#endif
        }

        public static object get_style(object key)
        {
            if (Application.Current.Resources.Contains(key))
                return Application.Current.Resources[key];

            throw new KeyNotFoundException("No resource by that key.");
        }

        public static bool toggle_visibility(UIElement el)
        {
            bool is_visible = el.Visibility == Visibility.Visible;
            el.Visibility = (is_visible) ? Visibility.Collapsed : Visibility.Visible;
            return !is_visible;
        }

        public static void on_first_layout(FrameworkElement el, EventHandler handler)
        {
            EventHandler _handle_once = null;
            _handle_once = (sender, e) =>
            {
                handler(sender, e);
                el.LayoutUpdated -= _handle_once;
            };

            el.LayoutUpdated += _handle_once;
        }

#if SILVERLIGHT
        public static void dock_popup(Popup popup, Dock dock1)
        {
            dock_popup(popup, dock1, 0, null, 0);
        }

        public static void dock_popup(Popup popup, Dock dock1, double offset1)
        {
            dock_popup(popup, dock1, offset1, null, 0);
        }

        public static void dock_popup(Popup popup, Dock dock1, double offset1, Dock? dock2)
        {
            dock_popup(popup, dock1, offset1, dock2, 0);
        }

        public static void dock_popup(Popup popup, Dock dock1, double offset1, Dock? dock2, double offset2)
        {
            FrameworkElement rv = (FrameworkElement)get_root_visual();

            Action<Dock, double> _dock = (dock, offset) =>
            {
                if (dock == Dock.Left)
                    popup.HorizontalOffset = offset;
                else if (dock == Dock.Top)
                    popup.VerticalOffset = offset;
                else
                {
                    Size sz = measure((FrameworkElement)popup.Child);
                    if (dock == Dock.Right)
                        popup.HorizontalOffset = rv.ActualWidth - offset - sz.Width;
                    else // Bottom
                        popup.VerticalOffset = rv.ActualHeight - offset - sz.Height;
                }
            };

            Action _dock_popup = () =>
            {
                _dock((Dock)dock1, offset1);
                if (dock2 != null)
                    _dock((Dock)dock2, offset2);
            };

            rv.SizeChanged += (sender, e) => _dock_popup();
            _dock_popup();
        }

        public static void center_popup(Popup popup)
        {
            FrameworkElement rv = (FrameworkElement)get_root_visual();
            Size sz = measure((FrameworkElement)popup.Child);
            popup.VerticalOffset = (rv.ActualHeight - sz.Height)/2;
            popup.HorizontalOffset = (rv.ActualWidth - sz.Width)/2;
        }
#endif
        // These really help with data binding scenarios

        public struct _Pair<T0, T1>
        {
            public readonly T0 First;
            public readonly T1 Second;

            public _Pair(T0 first, T1 second)
            {
                First = first;
                Second = second;
            }
        }

        public static _Pair<T0, T1> Pair<T0, T1>(T0 first, T1 second)
        {
            return new _Pair<T0, T1>(first, second);
        }
    }
}
