# You can edit these settings and save them, they 
# will be applied immediately and remembered for next time.
# This will reset the interpreter.

# ******************************************************************************* #
# If changing these settings makes the interpreter unrecoverable, you             #
# can reset to defaults by right clicking and using the silverlight configuration #
# dialog to clear persistent storage for this website.                            #
# ******************************************************************************* #

import sys
import wpf
from silvershell import utils

# Execute code on UI thread or on background thread
BackgroundExecution = False
# Show CLR tracebacks?
ExceptionDetail = False
# Settings this higher will display more members in the completion list, but will hurt performance
# If the completion list takes too long too show, set this lower.
MaxCompletions = 100

# Setting any of these preferences to None will result in them not being applied

FontSize = 14
FontFamily = wpf.FontFamily('Courier New')
FontWeight = wpf.FontWeights.Bold
Foreground = wpf.brush('#ffff00')
BackgroundMask = wpf.brush('#1a000000')
BackgroundImage = wpf.image_brush('/silverlight.jpg')

TextBoxStyle = utils.load_xaml('''
<Style TargetType="TextBox"
    xmlns="%%(client_ns)s"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    
    <Setter Property="Background" Value="Transparent" />
    <Setter Property="Padding" Value="0" />
    <Setter Property="BorderThickness" Value="0" />
    <Setter Property="Template">
        <Setter.Value>
            <ControlTemplate TargetType="TextBox">
                <Border x:Name="%s" Background="{TemplateBinding Background}" Padding="{TemplateBinding Padding}" />
            </ControlTemplate>
        </Setter.Value>
    </Setter>
</Style>
''' % ('ContentElement' if sys.platform == 'silverlight' else 'PART_ContentHost'))

if sys.platform == 'silverlight':
    ButtonStyle = utils.load_xaml('''
    <Style TargetType="Button"
        xmlns="%(client_ns)s"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:vsm="clr-namespace:System.Windows;assembly=System.Windows">
        
        <Setter Property="FontSize" Value="14" />
        <Setter Property="FontWeight" Value="Bold" />
        <Setter Property="Foreground" Value="Yellow" />
        <Setter Property="Background" Value="Transparent" />
        <Setter Property="Padding" Value="0" />
        <Setter Property="BorderThickness" Value="0" />
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="Button">
                    <TextBlock x:Name="RootElement" Text="{TemplateBinding Content}" TextDecorations="Underline">
                        <vsm:VisualStateManager.VisualStateGroups>
                            <vsm:VisualStateGroup x:Name="CommonStates">
                                <vsm:VisualStateGroup.Transitions>
                                    <vsm:VisualTransition To="MouseOver" GeneratedDuration="0:0:0.25" />
                                </vsm:VisualStateGroup.Transitions>
                                <vsm:VisualState x:Name="Normal" />
                                <vsm:VisualState x:Name="MouseOver">
                                    <Storyboard>
                                        <ColorAnimation Storyboard.TargetName="RootElement" Storyboard.TargetProperty="(Control.Foreground).(SolidColorBrush.Color)" To="Cyan" Duration="0" />
                                    </Storyboard>
                                </vsm:VisualState>
                                <vsm:VisualState x:Name="Pressed" />
                                <vsm:VisualState x:Name="Disabled" />
                            </vsm:VisualStateGroup>
                            <vsm:VisualStateGroup x:Name="FocusStates">
                                <vsm:VisualState x:Name="Focused" />
                                <vsm:VisualState x:Name="Unfocused" />
                            </vsm:VisualStateGroup>
                        </vsm:VisualStateManager.VisualStateGroups>
                    </TextBlock>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>
    ''')
else:
    ButtonStyle = utils.load_xaml('''
    <Style TargetType="Button"
        xmlns="%(client_ns)s"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:vsm="clr-namespace:System.Windows;assembly=System.Windows">
        
        <Setter Property="FontSize" Value="14" />
        <Setter Property="FontWeight" Value="Bold" />
        <Setter Property="Foreground" Value="Yellow" />
        <Setter Property="Background" Value="Transparent" />
        <Setter Property="Padding" Value="0" />
        <Setter Property="BorderThickness" Value="0" />
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="Button">
                    <TextBlock x:Name="PART_ContentHost" Text="{TemplateBinding Content}" TextDecorations="Underline" />
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>
    ''')

# These preferences are mandatory, setting them to None is an error

CallTip = utils.load_xaml('''
<Border 
    xmlns="%(client_ns)s"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    Background="Black"
    BorderThickness="2"
    Padding="5"
    >
    <Border.BorderBrush>
        <LinearGradientBrush StartPoint="0.5,0" EndPoint="0.5,1">
            <GradientStop Color="#B2FFFFFF" Offset="0"/>
            <GradientStop Color="#66FFFFFF" Offset="0.325"/>
            <GradientStop Color="#1EFFFFFF" Offset="0.325"/>
            <GradientStop Color="#51FFFFFF" Offset="1"/>
        </LinearGradientBrush>
    </Border.BorderBrush>
    
    <ScrollViewer VerticalScrollBarVisibility="Auto" BorderThickness="0" Margin="0">
        <TextBlock x:Name="CallTipLabel" TextAlignment="Left" Foreground="White" />
    </ScrollViewer>
</Border>
''')

MemberList = utils.load_xaml('''
<Border 
    xmlns="%(client_ns)s"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
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
    
    <ListBox x:Name="MemberListBox" MaxHeight="240" />
</Border>
''')

CursorAnimation = utils.load_xaml('''
<ColorAnimationUsingKeyFrames 
    xmlns="%(client_ns)s"
    BeginTime="0"
    Storyboard.TargetProperty="(Shape.Fill).(SolidColorBrush.Color)"
    >
    <DiscreteColorKeyFrame Value="Transparent" KeyTime="0:0:0" />
    <LinearColorKeyFrame Value="Yellow" KeyTime="0:0:0.35" />
    <DiscreteColorKeyFrame Value="Yellow" KeyTime="0:0:0.6" />
</ColorAnimationUsingKeyFrames>
''')
