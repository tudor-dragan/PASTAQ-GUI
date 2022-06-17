import os
import sys
import pytest

import mock
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import buttons
import parameter
from files import EditFileDialog, FileProcessor


mzXML = 'C:/Users/Downloads/1_3.mzXML'
mzID = 'C:/Users/Downloads/s174pfZefF5L.mzid'


class TestButtons:

    # T2.1
    # test if the tooltip is correctly set
    def test_init_button_params(self):
        button = buttons.init_button_params("test_label", "test_tooltip")
        print(button.toolTip)
        assert button.toolTip() == "test_tooltip"

    # T4.1
    # tests to see if path gets correctly updated for multiple files when there is matching stems between the files
    def test_multiple_id_files_if_match(self):
        file = {'raw_path': mzXML, 'reference': False, 'group': '', 'ident_path': mzID, 'stem': 'D-10'}
        new_file = {'raw_path': mzXML, 'reference': False, 'group': '', 'ident_path': mzID, 'stem': 'D-10'}
        edit_file_dialog = EditFileDialog()
        edit_file_dialog.mzid_paths = ['C:/Users/Downloads/1_3.mzid']
        parameter.multiple_id_files(file, new_file, edit_file_dialog)
        assert new_file["ident_path"] == 'C:/Users/Downloads/1_3.mzid'

    # T4.2
    # tests to see if path does not get changed if paths don't match
    def test_multiple_id_files_if_no_match(self, tmp_path):
        file = {'raw_path': mzXML, 'reference': False, 'group': '', 'ident_path': mzID, 'stem': 'D-10'}
        new_file = {'raw_path': mzXML, 'reference': False, 'group': '', 'ident_path': mzID, 'stem': 'D-10'}
        directory = tmp_path / "mydir"
        directory.mkdir()
        mzid_file = directory / "myfile.mzid"
        edit_file_dialog = EditFileDialog()
        edit_file_dialog.mzid_paths = [mzid_file.as_posix()]
        parameter.multiple_id_files(file, new_file, edit_file_dialog)
        assert new_file["ident_path"] == mzID

    # T4.3
    # test to see if the path of a single file gets changed
    def test_single_id_file(self, tmp_path):
        directory = tmp_path / "mydir"
        directory.mkdir()
        file = directory / "myfile.mzid"
        new_file = {'raw_path': 'C:/Users/Downloads/D-10.mzXML', 'reference': False, 'group': '', 'ident_path': mzID, 'stem': 'D-10'}
        parameter.single_id_file(file.as_posix(), new_file)
        assert new_file['ident_path'] == file.as_posix()
        assert os.getcwd().replace('\\', '/') == os.path.dirname(file.as_posix())

    # T4.4
    # test if the name of the parameter is correctly set
    def test_init_label(self):
        label = parameter.init_label("test_text")
        assert label.text() == "test_text"

    # T4.5
    # test to see if tooltip is the right one
    def test_init_button(self):
        button = parameter.init_button("test_text", lambda a: a + 10, "test_tooltip")
        assert button.toolTip() == "test_tooltip"

    # T4.6
    # test to see if the file processor is available to the parameters tab
    def test_file_processor(self):
        widget = parameter.ParametersWidget()
        assert isinstance(widget.get_file_processor(), FileProcessor)

    # T4.7
    # test to see if a new file gets added correctly
    @mock.patch('parameter.Path.is_file')
    @mock.patch('parameter.ParametersWidget.check_run_btn')
    def test_add_new_file(self, mock_check, mock_is_file, tmp_path):
        widget = parameter.ParametersWidget()
        mock_is_file.return_value = True
        directory = tmp_path / "mydir"
        directory.mkdir()
        f1 = directory / "myfile.mzXML"
        f2 = directory / "myfile2.mzXML"
        file_paths = [f1.as_posix(), f2.as_posix()]
        widget.add_new_file(file_paths)
        assert len(widget.input_files) == 2
        assert widget.input_files[0]['raw_path'] == f1.as_posix()
        assert widget.input_files[1]['raw_path'] == f2.as_posix()

    # T4.8
    # test to see if files get updated correctly
    def test_examine_edit_files(self):
        efd = EditFileDialog()
        widget = parameter.ParametersWidget()
        efd.group = "group 1"
        input_files = [{'raw_path': mzXML, 'reference': False, 'group': '', 'ident_path': mzID, 'stem': 'D-10'}]
        widget.input_files = input_files
        widget.examine_edit_files(widget.input_files, efd, [0])
        assert widget.input_files[0]['group'] == "group 1"

    # T4.9
    # test to see if files get updated correctly
    @mock.patch('parameter.files.popup_window')
    @mock.patch('parameter.Path.is_file')
    @mock.patch('parameter.ParametersWidget.check_run_btn')
    def test_update_input_files(self, mock_check, mock_is_file, mock_popup, tmp_path):
        widget = parameter.ParametersWidget()
        mock_is_file.return_value = True
        directory = tmp_path / "mydir"
        directory.mkdir()
        f1 = directory / mzXML
        widget.input_files = [{'raw_path': str(f1), 'reference': False}]
        widget.update_input_files(widget.input_files)
        assert widget.input_files_table.rowCount() == 1

    # T4.10
    # test to see if files get removed
    @mock.patch('parameter.files.popup_window')
    @mock.patch('parameter.ParametersWidget.check_run_btn')
    def test_remove_file(self, mock_check, mock_popup):
        widget = parameter.ParametersWidget()
        widget.input_files = [{'raw_path': mzXML, 'reference': False}, {'raw_path': 'C:/Users/Downloads/1_4.mzXML', 'reference': False}, {'raw_path': 'C:/Users/Downloads/1_5.mzXML', 'reference': False}]
        widget.update_input_files(widget.input_files)
        widget.input_files_table.selectRow(0)
        widget.remove_file()
        assert widget.input_files_table.rowCount() == 2

    # T4.11
    # test to see if the parameters update accordingly
    @mock.patch('parameter.files.popup_window')
    def test_parameters_update(self, mock_popup):
        widget = parameter.ParametersWidget()
        widget.res_ms1.setValue(3000)
        widget.inst_type.setCurrentIndex(0)
        widget.update_parameters()
        assert widget.parameters['resolution_ms1'] == 3000
        assert widget.parameters['instrument_type'] == "orbitrap"
        assert not parameter.saved
