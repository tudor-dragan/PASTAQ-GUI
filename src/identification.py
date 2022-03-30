import os
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys

""" terminal:
    cd desktop/MSFragger-3.4
    java -Xmx32g -jar MSFragger-3.4.jar "C:/Users/kaitl/Desktop/closed_fragger.params" "C:/Users/kaitl/Downloads/mgf/1_3.mgf"
    cd C:/Users/kaitl/AppData/Local/Apps/ProteoWizard 3.0.22085.aa65186 64-bit
    idconvert "C:/Users/kaitl/Downloads/mgf/1_3.pepXML"
"""


# find mfragger directory to get jar file
def find_ms():
    ms_path = "C:/Users/kaitl/Desktop/MSFragger-3.4"  # hardcoded location
    return ms_path


# find proteowizard directorz to execute idconvert
def find_proteo():
    proteo = "C:/Users/kaitl/AppData/Local/Apps/ProteoWizard 3.0.22085.aa65186 64-bit"  # hardcoded location
    return proteo


# msfragger places pepxml in same directory with same name
def make_pep_path(mgf):
    return mgf.replace(".mgf", ".pepxml")


# idconvert places mzid in same directory with same name
def make_mzid_path(mzid):
    return mzid.replace(".mgf", ".mzID")


def hardprocess(mgf):
    # check if mzid is already in same directory
    if os.path.exists(make_mzid_path(mgf)):
        print("mzid already there")
        return make_mzid_path(mgf)

    ms = find_ms()

    msfragger = subprocess.run(
        ["java", "-Xmx32g", "-jar", "MSFragger-3.4.jar", "C:/Users/kaitl/Desktop/closed_fragger.params", mgf],
        cwd=ms,
        capture_output=True
    )
    pep = make_pep_path(mgf)

    proteo = find_proteo()
    idconvert = subprocess.run(['idconvert', pep, "-o", os.path.dirname(mgf)], cwd=proteo, capture_output=True)

    pep = Path(pep)  # delete intermediary pepxml
    pep.unlink()

    mzid = make_mzid_path(mgf)
    print(mzid)
    return mzid
