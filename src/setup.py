import sys
from cx_Freeze import setup, Executable

build_exe_options = {"include_msvcr": True}
bdist_msi_options = {"target_name": "PASTAQ-GUI.msi"}

# base="Win32GUI" should be used only for Windows GUI app
#base = None
#if sys.platform == "win32":
#    base = "Win32GUI"

setup(
    name="PASTAQ-GUI",
    version="1.0",
    description="GUI for PASTAQ",
    options={"build_exe": build_exe_options, "bdist_msi": bdist_msi_options},
    executables=[Executable("src/app.py")],
    install_requires=[
        'pastaq',
        'PyQt5',
    ],
)
