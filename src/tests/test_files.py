import os
import sys
import mock
import pytest
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import files
file_processor = files.FileProcessor()


@mock.patch('files.Path.is_file')
class TestCheckPaths:

    # tests for check_path
    # path not None and is path exists
    # 1
    def test_check_path_valid(self, mock_path):
        mock_path.return_value = True
        assert file_processor.check_path('path')

    # path not None, so path should be verified
    # 2
    def test_check_path_call(self, mock_path):
        file_processor.check_path('path')
        mock_path.assert_called()

    # path not None and path does not exist
    # 3
    def test_check_path_invalid(self, mock_path):
        mock_path.return_value = False
        assert not file_processor.check_path('path')

    # path None
    # 4
    def test_check_path_none(self, mock_path):
        assert not file_processor.check_path(None)

    # path None, so should not be verified
    # 5
    def test_check_path_none_call(self, mock_path):
        file_processor.check_path(None)
        mock_path.assert_not_called()


@mock.patch('files.FileProcessor.check_path')
class TestLoadMs:

    # tests for load_ms_path
    # check_path is False
    # 6
    def test_load_ms_path_false(self, mock_check):
        mock_check.return_value = False
        assert not file_processor.load_ms_path('ms_path')

    # check_path is False
    # 7
    def test_load_ms_path_false_value(self, mock_check):
        mock_check.return_value = False
        file_processor.load_ms_path('ms_path')
        assert file_processor.ms_jar == [False, '']

    # check_path is True
    # 8
    def test_load_ms_path_true(self, mock_check):
        mock_check.return_value = True
        assert file_processor.load_ms_path('ms_path')

    # check_path is True
    # 9
    def test_load_ms_path_true_value(self, mock_check):
        mock_check.return_value = True
        file_processor.load_ms_path('ms_path')
        assert file_processor.ms_jar == [True, 'ms_path']

    # tests load_id_path
    # check_path is False
    # 10
    def test_load_id_path_false(self, mock_check):
        mock_check.return_value = False
        assert not file_processor.load_id_path('id_path')

    # check_path is False
    # 11
    def test_load_id_path_false_value(self, mock_check):
        mock_check.return_value = False
        file_processor.load_ms_path('id_path')
        assert file_processor.id_file == [False, '']

    # check_path is True
    # 12
    def test_load_id_path_true(self, mock_check):
        mock_check.return_value = True
        assert file_processor.load_id_path('id_path')

    # check_path is True
    # 13
    def test_load_id_path_true_value(self, mock_check):
        mock_check.return_value = True
        file_processor.load_ms_path('id_path')
        assert file_processor.id_file == [True, 'id_path']

    # tests load_params_path
    # 14
    def test_load_params_path(self, mock_check):
        file_processor.load_params_path('params_path')
        assert file_processor.params == [True, 'params_path']


class TestPathManipulationDeletion:

    # test for make_pep_path
    # 15
    def test_make_pep_path(self):
        assert file_processor.make_pep_path('make_pep_from_mgf.mgf') == 'make_pep_from_mgf.pepxml'

    # test for make_mzid_path
    # 16
    def test_make_mzid_path(self):
        assert file_processor.make_mzid_path('make_mzid_from_mgf.mgf') == 'make_mzid_from_mgf.mzID'

    # test for delete_pep
    # 33
    @mock.patch('files.os.unlink')
    def test_delete_pep(self, mock_unlink):
        file_processor.delete_pep('path_to_delete.pepxml')
        mock_unlink.assert_called()



@mock.patch('files.popup_window')
class TestMS:

    # tests for execute_msfragger
    # tests if subprocess is called
    # 17
    @mock.patch('files.subprocess.run')
    def test_execute_msfragger_call(self, mock_run, mock_popup):
            file_processor.execute_msfragger('mgf_path.mgf')
            mock_run.assert_called()

    # tests when subprocess throws exception, should trigger popup window
    # 18
    def test_execute_msfragger_popup(self, mock_popup):
        with mock.patch('files.subprocess.run', side_effect=Exception("ERROR")):
            file_processor.execute_msfragger('mgf_path.mgf')
            mock_popup.assert_called()

    # tests when subprocess throws exception, should return False
    # 19
    def test_execute_msfragger_return(self, mock_popup):
        with mock.patch('files.subprocess.run', side_effect=Exception("ERROR")):
            assert not file_processor.execute_msfragger('mgf_path.mgf')

    # test return code checking
    # test return code called
    # 20
    @mock.patch('files.subprocess.run')
    @mock.patch('files.subprocess.CompletedProcess.check_returncode')
    def test_execute_msfragger_return_code_call(self, mock_run, mock_returncode, mock_popup):
        file_processor.execute_msfragger('mgf_path.mgf')
        mock_returncode.assert_called()

    # test returncode throws error, should trigger popup window
    # 21
    @mock.patch('files.subprocess.run')
    @mock.patch('files.subprocess.CompletedProcess.check_returncode')
    def test_execute_msfragger_return_code_popup(self, mock_run, mock_return, mock_popup):
        mock_return.side_effect = subprocess.CalledProcessError(1, 'java')
        file_processor.execute_msfragger('mgf_path.mgf')
        mock_popup.assert_called()

    # test returncode throws error, should return False
    # 22
    @mock.patch('files.subprocess.run')
    @mock.patch('files.subprocess.CompletedProcess.check_returncode')
    def test_execute_msfragger_return_code_return(self, mock_run, mock_return, mock_popup):
        mock_return.side_effect = subprocess.CalledProcessError(1, 'java')
        assert not file_processor.execute_msfragger('mgf_path.mgf')


@mock.patch('files.popup_window')
class TestID:

    # tests for execute_idconvert
    # tests if subprocess is called
    # 23
    @mock.patch('files.subprocess.run')
    def test_execute_idconvert_call(self, mock_run, mock_popup):
        file_processor.execute_idconvert('pep_path.pepxml', 'mgf_path.mgf')
        mock_run.assert_called()

    # tests when subprocess throws exception, should trigger popup window
    # 24
    def test_execute_idconvert_popup(self, mock_popup):
        with mock.patch('files.subprocess.run', side_effect=Exception("ERROR")):
            file_processor.execute_idconvert('pep_path.pepxml', 'mgf_path.mgf')
            mock_popup.assert_called()

    # tests when subprocess throws exception, should return False
    # 25
    def test_execute_idconvert_return(self, mock_popup):
        with mock.patch('files.subprocess.run', side_effect=Exception("ERROR")):
            assert not file_processor.execute_idconvert('pep_path.pepxml', 'mgf_path.mgf')

    # test return code checking
    # test return code called
    # 26
    @mock.patch('files.subprocess.run')
    @mock.patch('files.subprocess.CompletedProcess.check_returncode')
    def test_execute_idconvert_return_code_call(self, mock_run, mock_returncode, mock_popup):
        file_processor.execute_idconvert('pep_path.pepxml', 'mgf_path.mgf')
        mock_returncode.assert_called()

    # test returncode throws error, should trigger popup window
    # 27
    @mock.patch('files.subprocess.run')
    @mock.patch('files.subprocess.CompletedProcess.check_returncode')
    def test_execute_idconvert_return_code_popup(self, mock_run, mock_return, mock_popup):
        mock_return.side_effect = subprocess.CalledProcessError(1, 'java')
        file_processor.execute_idconvert('pep_path.pepxml', 'mgf_path.mgf')
        mock_popup.assert_called()

    # test returncode throws error, should return False
    # 28
    @mock.patch('files.subprocess.run')
    @mock.patch('files.subprocess.CompletedProcess.check_returncode')
    def test_execute_idconvert_return_code_return(self, mock_run, mock_return, mock_popup):
        mock_return.side_effect = subprocess.CalledProcessError(1, 'java')
        assert not file_processor.execute_idconvert('pep_path.pepxml', 'mgf_path.mgf')


@mock.patch('files.popup_window')
class TestCheck:

    # all paths are valid
    def set_to_true(self):
        file_processor.ms_jar = [True, '']
        file_processor.id_file = [True, '']
        file_processor.params = [True, '']

    # tests for check
    # all True
    # 29
    def test_check_true(self, mock_popup):
        self.set_to_true()
        assert file_processor.check()

    # all True, so no popup window
    # 30
    def test_check_call(self, mock_popup):
        self.set_to_true()
        file_processor.check()
        mock_popup.assert_not_called()

    # one of the paths is not valid
    def set_to_false(self):
        file_processor.ms_jar = [True, '']
        file_processor.id_file = [False, '']
        file_processor.params = [True, '']

    # one not True, should return False
    # 31
    def test_check_false(self, mock_popup):
        self.set_to_false()
        assert not file_processor.check()

    # one not True, should trigger popup window
    # 32
    def test_check_false_call(self, mock_popup):
        self.set_to_false()
        file_processor.check()
        mock_popup.assert_called()


@mock.patch('files.os.path.exists')
@mock.patch('files.FileProcessor.check')
@mock.patch('files.FileProcessor.execute_msfragger')
@mock.patch('files.FileProcessor.execute_idconvert')
@mock.patch('files.FileProcessor.make_pep_path')
@mock.patch('files.FileProcessor.delete_pep')
@mock.patch('files.FileProcessor.make_mzid_path')
@mock.patch('files.popup_window')
class TestProcess:

    # tests for process
    # mzid already exists
    # 34
    def test_process(self, mock_os_path, mock_make_mzid, mock_delete_pep, mock_make_pep,
                     mock_idconvert, mock_msfragger, mock_check, mock_popup):
        mock_os_path.return_value = True
        assert file_processor.process('mgf_path.mgf') == file_processor.make_mzid_path('mgf_path.mgf')

    # mzid already exists so no need to continue
    # 35
    def test_process_discontinue_call(self, mock_os_path, mock_make_mzid, mock_delete_pep, mock_make_pep,
                     mock_idconvert, mock_msfragger, mock_check, mock_popup):
        mock_os_path.return_value = True
        file_processor.process('mgf_path.mgf')
        mock_check.assert_not_called()

    # 36
    def test_process_fail_check(self, mock_popup, mock_make_mzid, mock_delete_pep, mock_make_pep,
                     mock_idconvert, mock_msfragger, mock_check, mock_os_path):
        mock_os_path.return_value = False
        mock_check.return_value = False
        assert not file_processor.process('mgf_path.mgf')

    # 37
    def test_process_fail_check_call(self, mock_os_path, mock_make_mzid, mock_delete_pep, mock_make_pep,
                     mock_idconvert, mock_msfragger, mock_check, mock_popup):
        mock_os_path.return_value = False
        mock_check.return_value = False
        file_processor.process('mgf_path.mgf')
        mock_msfragger.assert_not_called()

    # 38
    def test_process_fail_msfragger(self, mock_popup, mock_make_mzid, mock_delete_pep, mock_make_pep,
                     mock_idconvert, mock_msfragger, mock_check, mock_os_path):
        mock_os_path.return_value = False
        mock_check.return_value = True
        mock_msfragger.return_value = False
        assert not file_processor.process('mgf_path.mgf')

    # 39
    def test_process_fail_msfragger_call(self, mock_os_path, mock_make_mzid, mock_delete_pep, mock_make_pep,
                     mock_idconvert, mock_msfragger, mock_check, mock_popup):
        mock_os_path.return_value = False
        mock_check.return_value = True
        mock_msfragger.return_value = False
        file_processor.process('mgf_path.mgf')
        mock_make_pep.assert_not_called()

    # 40
    def test_process_fail_pep(self, mock_popup, mock_make_mzid, mock_delete_pep, mock_make_pep,
                                    mock_idconvert, mock_msfragger, mock_check, mock_os_path):
        mock_os_path.side_effect = lambda x: {1: False, 2: False}[x]
        mock_make_mzid.return_value = 1
        mock_check.return_value = True
        mock_msfragger.return_value = True
        mock_make_pep.return_value = 2
        assert not file_processor.process('mgf_path.mgf')

    # 41
    def test_process_fail_pep_popup(self, mock_popup, mock_make_mzid, mock_delete_pep, mock_make_pep,
                                    mock_idconvert, mock_msfragger, mock_check, mock_os_path):
        mock_os_path.side_effect = lambda x: {1: False, 2: False}[x]
        mock_make_mzid.return_value = 1
        mock_check.return_value = True
        mock_msfragger.return_value = True
        mock_make_pep.return_value = 2
        file_processor.process('mgf_path.mgf')
        mock_popup.assert_called()

    # 42
    def test_process_fail_pep_call(self, mock_popup, mock_make_mzid, mock_delete_pep, mock_make_pep,
                                    mock_idconvert, mock_msfragger, mock_check, mock_os_path):
        mock_os_path.side_effect = lambda x: {1: False, 2: False}[x]
        mock_make_mzid.return_value = 1
        mock_check.return_value = True
        mock_msfragger.return_value = True
        mock_make_pep.return_value = 2
        file_processor.process('mgf_path.mgf')
        mock_idconvert.assert_not_called()

    # 43
    def test_process_fail_idconvert(self, mock_popup, mock_make_mzid, mock_delete_pep, mock_make_pep,
                                    mock_idconvert, mock_msfragger, mock_check, mock_os_path):
        mock_os_path.side_effect = lambda x: {1: False, 2: True}[x]
        mock_make_mzid.return_value = 1
        mock_check.return_value = True
        mock_msfragger.return_value = True
        mock_make_pep.return_value = 2
        mock_idconvert.return_value = False
        assert not file_processor.process('mgf_path.mgf')

    # 44
    def test_process_fail_idconvert_call(self, mock_popup, mock_make_mzid, mock_delete_pep, mock_make_pep,
                                    mock_idconvert, mock_msfragger, mock_check, mock_os_path):
        mock_os_path.side_effect = lambda x: {1: False, 2: True}[x]
        mock_make_mzid.return_value = 1
        mock_check.return_value = True
        mock_msfragger.return_value = True
        mock_make_pep.return_value = 2
        mock_idconvert.return_value = False
        file_processor.process('mgf_path.mgf')
        mock_delete_pep.assert_not_called()

    # 45
    def test_process_fail_mzid(self, mock_popup, mock_make_mzid, mock_delete_pep, mock_make_pep,
                                    mock_idconvert, mock_msfragger, mock_check, mock_os_path):
        mock_os_path.side_effect = lambda x: {1: False, 2: True}[x]
        mock_make_mzid.return_value = 1
        mock_check.return_value = True
        mock_msfragger.return_value = True
        mock_make_pep.return_value = 2
        mock_idconvert.return_value = True
        assert not file_processor.process('mgf_path.mgf')

    # 46
    def test_process_fail_mzid_popup(self, mock_popup, mock_make_mzid, mock_delete_pep, mock_make_pep,
                                    mock_idconvert, mock_msfragger, mock_check, mock_os_path):
        mock_os_path.side_effect = lambda x: {1: False, 2: True}[x]
        mock_make_mzid.return_value = 1
        mock_check.return_value = True
        mock_msfragger.return_value = True
        mock_make_pep.return_value = 2
        mock_idconvert.return_value = True
        file_processor.process('mgf_path.mgf')
        mock_popup.assert_called()
