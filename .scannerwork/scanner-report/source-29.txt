import os, sys

# This is done for importing from a parent directory
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from parameter import *
from buttons import init_button_params
from files import EditFileDialog, FileProcessor

import pytest

#
# FIXTURES (these are functions that are run before tests for setup purposes)
#

#
# UNIT TESTS
#

# test if the tooltip is correctly set
def test_init_button_params():
    button = init_button_params("test_label", "test_tooltip")
    print(button.toolTip)
    assert button.toolTip() == "test_tooltip"

# tests to see if path gets correctly updated for multiple files when there is matching stems between the files
def test_multiple_id_files_if_match():
    file = {'raw_path': 'C:/Users/Downloads/1_3.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    new_file = {'raw_path': 'C:/Users/Downloads/1_3.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    edit_file_dialog = EditFileDialog()
    edit_file_dialog.mzid_paths = ['C:/Users/Downloads/1_3.mzid']
    multiple_id_files(file, new_file, edit_file_dialog)
    assert new_file["ident_path"] == 'C:/Users/Downloads/1_3.mzid'
    
# tests to see if path does not get changed if paths dont match
def test_multiple_id_files_if_no_match(tmp_path):
    file = {'raw_path': 'C:/Users/Downloads/1_3.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    new_file = {'raw_path': 'C:/Users/Downloads/1_3.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    dir = tmp_path / "mydir"
    dir.mkdir()
    mzid_file = dir / "myfile.mzid"
    edit_file_dialog = EditFileDialog()
    edit_file_dialog.mzid_paths = [mzid_file.as_posix()]
    multiple_id_files(file, new_file, edit_file_dialog)
    assert new_file["ident_path"] == 'C:/Users/Downloads/s174pfZefF5L.mzid'

# test to see if the path of a single file gets changed
def test_single_id_file(tmp_path):
    dir = tmp_path / "mydir"
    dir.mkdir()
    file = dir / "myfile.mzid"
    new_file = {'raw_path': 'C:/Users/Downloads/D-10.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}
    single_id_file(file.as_posix(), new_file)
    assert new_file['ident_path'] == file.as_posix()
    assert os.getcwd().replace('\\', '/') == os.path.dirname(file.as_posix())

# test if the name of the parameter is correctly set
def test_init_label():
    label = init_label("test_text")
    assert label.text() == "test_text"

# test to see if tooltip is the right one
def test_init_button():
    button = init_button("test_text", lambda a : a + 10, "test_tooltip")
    assert button.toolTip() == "test_tooltip"

# test to see if the file processor is available to the parameters tab
def test_FileProcessor():
    widget = ParametersWidget()
    assert isinstance(widget.get_file_processor(), FileProcessor)

# test to see if a new file gets added correctly
def test_ParametersWidget_add_new_file(tmp_path):
    widget = ParametersWidget()
    dir = tmp_path / "mydir"
    dir.mkdir()
    f1 = dir / "myfile.mzXML"
    f2 = dir / "myfile2.mzXML"
    file_paths = [f1.as_posix(), f2.as_posix()]
    widget.add_new_file(file_paths)
    assert len(widget.input_files) == 2
    assert widget.input_files[0]['raw_path'] == f1.as_posix()
    assert widget.input_files[1]['raw_path'] == f2.as_posix()

# test to see if files get updated correctly
def test_ParametersWidget_examine_edit_files():
    efd = files.EditFileDialog()
    widget = ParametersWidget()
    efd.group = "group 1"
    input_files = [{'raw_path': 'C:/Users/Downloads/1_3.mzXML', 'reference': False, 'group': '', 'ident_path': 'C:/Users/Downloads/s174pfZefF5L.mzid', 'stem': 'D-10'}]
    widget.input_files = input_files
    widget.examine_edit_files(widget.input_files, efd, [0])
    assert widget.input_files[0]['group'] == "group 1"

#test to see if fils get updated correctly
def test_ParametersWidget_update_input_files():
    widget = ParametersWidget()
    widget.input_files = [{'raw_path': 'C:/Users/Downloads/1_3.mzXML', 'reference': False}]
    widget.update_input_files(widget.input_files)
    assert widget.input_files_table.rowCount() == 1

# test to see if files get removed
def test_ParametersWidget_remove_file():
    widget = ParametersWidget()
    widget.input_files = [{'raw_path': 'C:/Users/Downloads/1_3.mzXML', 'reference': False}, {'raw_path': 'C:/Users/Downloads/1_4.mzXML', 'reference': False}, {'raw_path': 'C:/Users/Downloads/1_5.mzXML', 'reference': False}]
    widget.update_input_files(widget.input_files)
    widget.input_files_table.selectRow(0)
    widget.remove_file()
    assert widget.input_files_table.rowCount() == 2

def test_ParametersWidget_parameters_update():
    widget = ParametersWidget()
    widget.res_ms1.setValue(3000)
    widget.inst_type.setCurrentIndex(0)
    widget.update_parameters()
    assert widget.parameters['resolution_ms1'] == 3000
    assert widget.parameters['instrument_type'] == "orbitrap"
    assert widget.get_saved() == False