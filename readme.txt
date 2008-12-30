To run the silverlight version, run Chiron /W from this directory 
and then point your browser at http://localhost:2060/index.html

There are some issues with Firefox, and I haven't tested on a Mac.
These issues will be addressed sometime in the next year, but 
in the meantime I'll graciously accept patches.

The WPF version can be started by opening a command prompt and running:
silvershell> .\ipyw shell.py

IronPython is included to help you get started, but you'll probably want to use the
same version you develop with. To do that you'll need to build _wpf.dll using the
included project. The included version is source drop 43741, main branch, simply
because this is currently the version I develop with.
