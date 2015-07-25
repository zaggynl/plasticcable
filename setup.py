from distutils.core import setup
import py2exe, sys
from glob import glob
data_files = [("Microsoft.VC90.CRT", glob(r'C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
setup(data_files=data_files)
sys.path.append("C:\Users\joe\Downloads\plasticcable-master\plasticcable-master\dist\Microsoft.VC90.CRT")
setup(console=['plasticcable_cli.py', 'plasticcable_gui.py'])

