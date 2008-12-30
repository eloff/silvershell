from System import Uri, UriKind
from System.Windows import Application
from System.Security.Cryptography import SHA1

__all__ = ['curdir', 'pardir', 'extsep', 'sep', 'altsep', 'normcase', 'isabs', 'join',
           'split', 'splitext', 'basename', 'dirname', 'getsize', 'exists',
           'isfile', 'normpath']

curdir = '.'
pardir = '..'
extsep = '.'
sep = '/'
altsep = None

def normcase(s):
    """Normalize case of pathname."""
    return s.lower()

def isabs(s):
    """Test whether a path is absolute."""
    return s.startswith('/')

def join(a, *p):
    """Join two or more pathname components, inserting '/' as needed"""
    path = a
    for b in p:
        if b.startswith('/'):
            path = b
        elif path == '' or path.endswith('/'):
            path +=  b
        else:
            path += '/' + b
    return path

def split(p):
    """Split a pathname.  Returns tuple "(head, tail)" where "tail" is
    everything after the final slash.  Either part may be empty."""
    i = p.rfind('/') + 1
    head, tail = p[:i], p[i:]
    if head and head != '/'*len(head):
        head = head.rstrip('/')
    return head, tail

def splitext(p):
    """Split the extension from a pathname.  Extension is everything from the
    last dot to the end.  Returns "(root, ext)", either part may be empty."""
    i = p.rfind('.')
    if i<=p.rfind('/'):
        return p, ''
    else:
        return p[:i], p[i:]
    
def getsize(p):
    return Application.GetResourceStream(Uri(p, UriKind.Relative)).Length
   
def basename(p):
    """Returns the final component of a pathname"""
    return split(p)[1]

def dirname(p):
    """Returns the directory component of a pathname"""
    return split(p)[0]

def commonprefix(m):
    "Given a list of pathnames, returns the longest common leading component"
    if not m: return ''
    s1 = min(m)
    s2 = max(m)
    n = min(len(s1), len(s2))
    for i in xrange(n):
        if s1[i] != s2[i]:
            return s1[:i]
    return s1[:n]

def exists(p):
    '''Test whether a path exists. Only works for files.'''
    return Application.GetResourceStream(Uri(p, UriKind.Relative)) is not None

isfile = exists

def normpath(path):
    """Normalize path, eliminating double slashes, etc."""
    if path == '':
        return '.'
    initial_slashes = path.startswith('/')
    # POSIX allows one or two initial slashes, but treats three or more
    # as single slash.
    if (initial_slashes and
        path.startswith('//') and not path.startswith('///')):
        initial_slashes = 2
    comps = path.split('/')
    new_comps = []
    for comp in comps:
        if comp in ('', '.'):
            continue
        if (comp != '..' or (not initial_slashes and not new_comps) or
             (new_comps and new_comps[-1] == '..')):
            new_comps.append(comp)
        elif new_comps:
            new_comps.pop()
    comps = new_comps
    path = '/'.join(comps)
    if initial_slashes:
        path = '/'*initial_slashes + path
    return path or '.'

