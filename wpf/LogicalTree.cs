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
using System.Collections;
using System.Windows;
using System.Windows.Controls;
using System.Reflection;
using System.Collections.Generic;
using System.Windows.Markup;
using System.Linq;

namespace _wpf
{
    public static partial class wpf
    {
        public static class LogicalTree
        {
            public static IEnumerable<UIElement> Walk(UIElement el)
            {
                return Walk(el, Int32.MaxValue);
            }

            public static IEnumerable<UIElement> Walk(UIElement el, int depth)
            {
                var stack = new Queue<_Pair<UIElement, int>>();
                stack.Enqueue(Pair(el, depth));
                while (stack.Count > 0)
                {
                    var args = stack.Dequeue();
                    el = args.First;
                    depth = args.Second;
                    if (el != null)
                    {
                        yield return el;

                        object content;
                        if (depth != 0 && TryGetContent(el, out content))
                        {
                            depth--;
                            if (content is UIElement)
                                stack.Enqueue(Pair((UIElement)content, depth));
                            else
                            {
                                var l = content as IList;
                                if (l != null && l.Count > 0 && l[0] is UIElement)
                                {
                                    foreach (object o in l)
                                        stack.Enqueue(Pair((UIElement)o, depth));
                                }
                            }
                        }
                    }
                }
            }

            public static UIElement NextSibling(FrameworkElement el)
            {
                bool is_next = false;
                var parent = el.Parent as UIElement;
                if (parent != null)
                    foreach (UIElement child in Walk(parent, 1))
                    {
                        if (is_next)
                            return child;
                        if (ReferenceEquals(child, el))
                            is_next = true;
                    }

                return null;
            }

            public static UIElement PrevSibling(FrameworkElement el)
            {
                UIElement prev = null;
                bool is_prev = false;
                var parent = el.Parent as UIElement;
                if (parent != null)
                    foreach (UIElement child in Walk(parent, 1))
                    {
                        if (ReferenceEquals(child, el))
                        {
                            is_prev = true;
                            break;
                        }
                        prev = child;
                    }

                return is_prev ? prev : null;
            }

            public static bool TryGetContent(DependencyObject el, out object content)
            {
                Type ty = el.GetType();
                object[] attrs = ty.GetCustomAttributes(typeof(ContentPropertyAttribute), true);
                if (attrs.Length != 0)
                {
                    string content_property = ((ContentPropertyAttribute)attrs[0]).Name;
                    PropertyInfo prop = ty.GetProperty(content_property);
                    content = prop.GetValue(el, null);
                    return true;
                }
                content = null;
                return false;
            }

            public static void SetContent(DependencyObject el, DependencyObject content)
            {
                Type ty = el.GetType();
                object[] attrs = ty.GetCustomAttributes(typeof(ContentPropertyAttribute), true);
                if (attrs.Length != 0)
                {
                    string content_property = ((ContentPropertyAttribute)attrs[0]).Name;
                    PropertyInfo prop = ty.GetProperty(content_property);
                    if (Array.IndexOf(prop.PropertyType.GetInterfaces(), typeof(IList)) != -1)
                    {
                        IList col = (IList)prop.GetValue(el, null);
                        col.Clear();
                        if (content != null)
                            col.Add(content);
                    }
                    else
                        prop.SetValue(el, content, null);
                }
                else
                    throw new ArgumentException("Element has no content.", "el");
            }

            public static void SetContent(DependencyObject el, IEnumerable<DependencyObject> content)
            {
                var it = content.GetEnumerator();
                if (it.MoveNext())
                {
                    var child = it.Current;
                    if (!it.MoveNext())
                    {
                        SetContent(el, child);
                        return;
                    }
                }
                else
                {
                    RemoveAllChildren(el);
                    return;
                }

                object children;
                if (TryGetContent(el, out children) && children is IList)
                {
                    IList col = (IList)children;
                    col.Clear();
                    foreach (DependencyObject child in content)
                        col.Add(child);
                    return;
                }

                throw new ArgumentException("Element has no content, or does not support multiple children.", "el");
            }

            public static void Unlink(FrameworkElement el)
            {
                object content;
                if (el.Parent != null && TryGetContent(el.Parent, out content))
                {
                    if (content is IList)
                        ((IList)content).Remove(el);
                    else
                        SetContent(el.Parent, (FrameworkElement)null);
                }
            }

            public static void RemoveAllChildren(DependencyObject el)
            {
                object content;
                if (TryGetContent(el, out content))
                {
                    if (content is IList)
                        ((IList)content).Clear();
                    else
                        SetContent(el, (FrameworkElement)null);
                }
            }

            public static object GetFirstChild(DependencyObject el)
            {
                object content;
                if (TryGetContent(el, out content))
                {
                    if (content is IEnumerable)
                    {
                        IEnumerator it = ((IEnumerable)content).GetEnumerator();
                        if (it.MoveNext())
                            return it.Current;
                    }
                }
                return content;
            }

            public static object GetFirstChild(DependencyObject el, Func<object, bool> predicate)
            {
                object content;
                if (TryGetContent(el, out content))
                {
                    if (content is IEnumerable)
                    {
                        return ((IEnumerable<object>)content).FirstOrDefault(predicate);
                    }
                    else if (predicate(content))
                        return content;
                }
                return null;
            }

            public static object GetFirstChildOfType(DependencyObject el, Type ty)
            {
                return GetFirstChild(el, c => c.GetType() == ty);
            }

            public static object GetFirstDescendant(UIElement el, Func<UIElement, bool> predicate)
            {
                foreach (UIElement d in Walk(el))
                    if (predicate(d))
                        return d;

                return null;
            }

            public static object GetFirstDescendantOfType(UIElement el, Type ty)
            {
                return GetFirstDescendant(el, c => c.GetType() == ty);
            }

            public static DependencyObject GetFirstAncestor(FrameworkElement el, Func<DependencyObject, bool> predicate)
            {
                do
                {
                    var parent = el.Parent;
                    if (predicate(parent))
                        return parent;

                    el = parent as FrameworkElement;
                } while (el != null);

                return null;
            }

            public static object GetFirstAncestorOfType(FrameworkElement el, Type ty)
            {
                return GetFirstAncestor(el, c => c.GetType() == ty);
            }

            public static DependencyObject Clone(DependencyObject obj)
            {
                throw new NotImplementedException();
            }
        }
    }
}
