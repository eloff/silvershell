import sys
import clr
clr.AddReferenceToFile('_wpf.dll')
if sys.platform == 'silverlight':
    clr.AddReferenceToFile('System.Windows.Controls.dll')
    # Silverlight Toolkit, if available
    try:
        clr.AddReferenceToFile('Microsoft.Windows.Controls.dll')
        clr.AddReferenceToFile('Microsoft.Windows.Controls.Input.dll')
        from Microsoft.Windows.Controls import *
    except IOError:
        pass

from System import Uri, UriKind
from System.Windows.Controls.Primitives import *
from System.Windows.Media import *
from System.Windows.Documents import *
from System.Windows.Shapes import *
from System.Windows.Input import *
from System.Windows.Media.Animation import *
from System.Windows.Media.Imaging import BitmapImage
from System.Windows.Interop import *
from System.Windows import *
from System.Windows.Controls import *
from _wpf import *

def Create(ty, *children, **attrs):
    obj = ty()
    for attr, val in attrs.iteritems():
        klass, attr = attr.rpartition('_')[::2]
        if klass:
            getattr(globals()[klass], 'Set' + attr)(obj, val)
        else:
            setattr(obj, attr, val)
            
    if children:
        LogicalTree.SetContent(obj, children)
            
    return obj


    
        