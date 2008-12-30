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
using System.Net;
using System.Windows.Media;

namespace _wpf
{
    public static partial class wpf
    {
        public static class Colors
        {
            public static Color AliceBlue = Color.FromArgb(0xff, 0xf0, 0xf8, 0xff);
            public static Color Black = Color.FromArgb(0xff, 0x00, 0x00, 0x00);
            public static Color Blue = Color.FromArgb(0xff, 0x00, 0x00, 0xff);
            public static Color Brown = Color.FromArgb(0xff, 0xa5, 0x2a, 0x2a);
            public static Color Chartreuse = Color.FromArgb(0xff, 0x7f, 0xff, 0x00);
            public static Color Coral = Color.FromArgb(0xff, 0xf7, 0xff, 0x50);
            public static Color CornflowerBlue = Color.FromArgb(0xff, 0x64, 0x95, 0xed);
            public static Color Crimson = Color.FromArgb(0xff, 0xdc, 0x14, 0x3c);
            public static Color Cyan = Color.FromArgb(0xff, 0x00, 0xff, 0xff);
            public static Color DarkBlue = Color.FromArgb(0xff, 0x00, 0x00, 0x8b);
            public static Color DarkCyan = Color.FromArgb(0xff, 0x00, 0x8b, 0x8b);
            public static Color DarkGray = Color.FromArgb(0xff, 0xa9, 0xa9, 0xa9);
            public static Color DarkOrange = Color.FromArgb(0xff, 0xff, 0x8c, 0x00);
            public static Color DarkTurquoise = Color.FromArgb(0xff, 0x00, 0xce, 0xd1);
            public static Color DarkViolet = Color.FromArgb(0xff, 0x94, 0x00, 0xd3);
            public static Color DarkSeaGreen = Color.FromArgb(0xff, 0x8f, 0xbc, 0x8f);
            public static Color DarkSlateBlue = Color.FromArgb(0xff, 0x48, 0x3d, 0x8b);
            public static Color DarkSlateGray = Color.FromArgb(0xff, 0x2f, 0x4f, 0x4f);
            public static Color DimGrey = Color.FromArgb(0xff, 0x69, 0x69, 0x69);
            public static Color Gainsboro = Color.FromArgb(0xff, 0xdc, 0xdc, 0xdc);
            public static Color Gold = Color.FromArgb(0xff, 0xff, 0xd7, 0x00);
            public static Color Goldenrod = Color.FromArgb(0xff, 0xda, 0xa5, 0x20);
            public static Color Gray = Color.FromArgb(0xff, 0x80, 0x80, 0x80);
            public static Color Green = Color.FromArgb(0xff, 0x00, 0x80, 0x00);
            public static Color GreenYellow = Color.FromArgb(0xff, 0xad, 0xff, 0x2f);
            public static Color Indigo = Color.FromArgb(0xff, 0x4b, 0x00, 0x82);
            public static Color Lavender = Color.FromArgb(0xff, 0xe6, 0xe6, 0xfa);
            public static Color LemonChiffon = Color.FromArgb(0xff, 0xff, 0xfa, 0xcd);
            public static Color LightBlue = Color.FromArgb(0xff, 0xad, 0xd8, 0xe6);
            public static Color LightGray = Color.FromArgb(0xff, 0xd3, 0xd3, 0xd3);
            public static Color LightGreen = Color.FromArgb(0xff, 0x90, 0xee, 0x90);
            public static Color LightSeaGreen = Color.FromArgb(0xff, 0x20, 0xb2, 0xaa);
            public static Color LightSkyBlue = Color.FromArgb(0xff, 0x87, 0xce, 0xfa);
            public static Color LightSlateGray = Color.FromArgb(0xff, 0x77, 0x88, 0x99);
            public static Color LightSteelBlue = Color.FromArgb(0xff, 0xb0, 0xc4, 0xde);
            public static Color Lime = Color.FromArgb(0xff, 0x00, 0xff, 0x00);
            public static Color LimeGreen = Color.FromArgb(0xff, 0x32, 0xcd, 0x32);
            public static Color MediumAquamarine = Color.FromArgb(0xff, 0x66, 0xcd, 0xaa);
            public static Color MediumSeaGreen = Color.FromArgb(0xff, 0x3c, 0xb3, 0x71);
            public static Color MediumSpringGreen = Color.FromArgb(0xff, 0x00, 0xfa, 0x9a);
            public static Color MediumTurquoise = Color.FromArgb(0xff, 0x48, 0xd1, 0xcc);
            public static Color MidnightBlue = Color.FromArgb(0xff, 0x19, 0x19, 0x70);
            public static Color Olive = Color.FromArgb(0xff, 0x80, 0x80, 0x00);
            public static Color Orange = Color.FromArgb(0xff, 0xff, 0xa5, 0x00);
            public static Color OrangeRed = Color.FromArgb(0xff, 0xff, 0x45, 0x00);
            public static Color PaleGreen = Color.FromArgb(0xff, 0x98, 0xfb, 0x98);
            public static Color PaleTurquoise = Color.FromArgb(0xff, 0xaf, 0xee, 0xee);
            public static Color Pink = Color.FromArgb(0xff, 0xff, 0xc0, 0xcb);
            public static Color Plum = Color.FromArgb(0xff, 0xdd, 0xa0, 0xdd);
            public static Color Purple = Color.FromArgb(0xff, 0x80, 0x00, 0x80);
            public static Color Red = Color.FromArgb(0xff, 0xff, 0x00, 0x00);
            public static Color RoyalBlue = Color.FromArgb(0xff, 0x41, 0x69, 0xe1);
            public static Color SeaGreen = Color.FromArgb(0xff, 0x2e, 0x8b, 0x57);
            public static Color Silver = Color.FromArgb(0xff, 0xc0, 0xc0, 0xc0);
            public static Color SkyBlue = Color.FromArgb(0xff, 0x87, 0xce, 0xeb);
            public static Color SpringGreen = Color.FromArgb(0xff, 0x00, 0xff, 0x7f);
            public static Color SteelBlue = Color.FromArgb(0xff, 0x46, 0x82, 0xb4);
            public static Color Teal = Color.FromArgb(0xff, 0x00, 0x80, 0x80);
            public static Color Thistle = Color.FromArgb(0xff, 0xd8, 0xbf, 0xd8);
            public static Color Transparent = Color.FromArgb(0x00, 0xff, 0xff, 0xff);
            public static Color Turquoise = Color.FromArgb(0xff, 0x40, 0xe0, 0xd0);
            public static Color Violet = Color.FromArgb(0xff, 0xee, 0x82, 0xee);
            public static Color White = Color.FromArgb(0xff, 0xff, 0xff, 0xff);
            public static Color Yellow = Color.FromArgb(0xff, 0xff, 0xff, 0x00);
            public static Color YellowGreen = Color.FromArgb(0xff, 0x9a, 0xcd, 0x32);
        }
    }
}
