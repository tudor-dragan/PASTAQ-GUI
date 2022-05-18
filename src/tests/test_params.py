import os, sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QSpinBox, QAbstractSpinBox
from PyQt5.QtWidgets import QWidget, QLineEdit, QDoubleSpinBox, QCheckBox
from PyQt5.QtWidgets import QPushButton, QFileDialog, QScrollArea, QComboBox, QLabel, QMainWindow
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QHBoxLayout, QGroupBox, QGridLayout

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from parameter import *
from files import EditFileDialog, FileProcessor
from app import MainWindow

import pytest

#
# FIXTURES (these are functions that are run before tests for setup purposes)
#

@pytest.fixture
def init_ParamsWidget():
    widget = ParametersWidget()

#
# UNIT TESTS
#

# test if the tooltip is correctly set
def test_init_button_params():
    button = init_button_params("test_label", "test_tooltip")
    print(button.toolTip)
    assert button.toolTip() == "test_tooltip"

def test_ParameterItem():
    # a test here
    assert True

# tests to see if path gets correctly updated for multiple files when there is matching stems between the files
def test_multiple_id_files_if_match():
    file = {'raw_path': 'C:/Users/tudor/Downloads/1_3.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/tudor/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    new_file = {'raw_path': 'C:/Users/tudor/Downloads/1_3.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/tudor/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    edit_file_dialog = EditFileDialog()
    edit_file_dialog.mzid_paths = ['C:/Users/tudor/Downloads/1_3.mzid']
    multiple_id_files(file, new_file, edit_file_dialog)
    assert new_file["ident_path"] == 'C:/Users/tudor/Downloads/1_3.mzid'
    
# tests to see if path does not get changed if paths dont match
def test_multiple_id_files_if_no_match():
    file = {'raw_path': 'C:/Users/tudor/Downloads/1_3.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/tudor/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    new_file = {'raw_path': 'C:/Users/tudor/Downloads/1_3.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/tudor/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    edit_file_dialog = EditFileDialog()
    edit_file_dialog.mzid_paths = ['C:/Users/tudor/Downloads/abcd.mzid']
    multiple_id_files(file, new_file, edit_file_dialog)
    assert new_file["ident_path"] == 'C:/Users/tudor/Downloads/s174pfZefF5L.mzid'

# test to see if the path of a single file gets changed
def test_single_id_file():
    path = 'C:/Users/tudor/Downloads/1_3.mzid'
    new_file = {'raw_path': 'C:/Users/tudor/Downloads/D-10.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/tudor/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    single_id_file(path, new_file)
    assert new_file['ident_path'] == path
    assert os.getcwd().replace('\\', '/') == os.path.dirname(path)

# test if the name of the parameter is correctly set
def test_init_label():
    label = init_label("test_text")
    assert label.text() == "test_text"

def test_init_button():
    button = init_button("test_text", lambda a : a + 10, "test_tooltip")
    assert button.toolTip() == "test_tooltip"

def test_ParametersWidget_components():
    widget = ParametersWidget()
    assert len(widget.findChildren(QScrollArea)) == 2

def test_FileProcessor():
    widget = ParametersWidget()
    assert isinstance(widget.get_file_processor(), FileProcessor)

def test_ParametersWidget_add_new_file(tmp_path):
    widget = ParametersWidget()
    dir = tmp_path / "mydir"
    dir.mkdir()
    f1 = dir / "myfile.mzXML"
    f2 = dir / "myfile2.mzXML"
    # TODO add a fixture to create the files in a temporary directory
    file_paths = [f1.as_posix(), f2.as_posix()]
    widget.add_new_file(file_paths)
    assert len(widget.input_files) == 2
    assert widget.input_files[0]['raw_path'] == f1.as_posix()
    assert widget.input_files[1]['raw_path'] == f2.as_posix()

def test_ParametersWidget_examine_edit_files():
    assert True

def test_ParametersWidget_update_input_files():
    widget = ParametersWidget()
    widget.input_files = [{'raw_path': 'C:/Users/tudor/Downloads/1_3.mzXML', 'reference': False}]
    widget.update_input_files(widget.input_files)
    assert widget.input_files_table.rowCount() == 1

def test_ParametersWidget_remove_file():
    widget = ParametersWidget()
    widget.input_files = [{'raw_path': 'C:/Users/tudor/Downloads/1_3.mzXML', 'reference': False}, {'raw_path': 'C:/Users/tudor/Downloads/1_4.mzXML', 'reference': False}, {'raw_path': 'C:/Users/tudor/Downloads/1_5.mzXML', 'reference': False}]
    widget.update_input_files(widget.input_files)
    widget.input_files_table.selectRow(0)
    widget.remove_file()
    assert widget.input_files_table.rowCount() == 2



# put test_ in front to make it a test
def input_files_tab():
    window = MainWindow()
    #window.show()
    window.open_project()

    #this will click the add file button in the gui but unfortunately i cant figure out how to select a file
    qtbot.mouseClick(window.parameters_container.input_files_tab.findChildren(QPushButton)[0], Qt.LeftButton)
    #qtbot.mouseClick(window.findChildren(QFileDialog)[0].browseButton, Qt.LeftButton)
    qtbot.keyClicks(window.findChildren(QFileDialog)[0], 'proj')
    return


