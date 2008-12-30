from nt import urandom
import posixpath as path

__all__ = ['linesep', 'name', 'urandom', 'path']

linesep = '\n'
name = 'silverlight'

def _get_constants():
    gvars = globals()
    for name in ('curdir', 'pardir', 'extsep', 'sep', 'altsep'):
        gvars[name] = getattr(path, name)
        
_get_constants()
del _get_constants
