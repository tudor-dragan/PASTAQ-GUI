import sys
from cx_Freeze import setup, Executable

#build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# base="Win32GUI" should be used only for Windows GUI app
#base = None
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(
    name="PASTAQ-GUI",
    version="1.0",
    description="GUI for PASTAQ",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py")],
    install_requires=[
        'pastaq',
        'PyQt5',
    ],
)
