import pytest
import os
import mock
import sys
from PyQt5.QtWidgets import QDialog, QTextEdit, QDialogButtonBox, QVBoxLayout

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pipeline

ml_path = 'some_ml_path.mzML'
ident_path_mgf = 'identification_file_path.mgf'
ident_path_mzid = 'identification_file_path.mzid'


@mock.patch('pipeline.files')
@mock.patch('pipeline.pastaq.dda_pipeline')
class TestRun:
    input = [{'raw_path': ml_path, 'reference': False, 'group': '', 'ident_path': ident_path_mgf}]
    output = [{'raw_path': ml_path, 'reference': False, 'group': '', 'ident_path': ident_path_mzid}]

    # assuming the file processing works, input files are changed accordingly
    # T5.1
    def test_run_true(self, mock_pipeline, mock_files):
        pipe = pipeline.PipelineRunner(mock_files)
        pipe.input_files = self.input
        mock_files.process.return_value = ident_path_mzid
        pipe.run()
        assert pipe.input_files == self.output

    # assuming the file processing works, the pipeline can be called
    # T5.2
    def test_run_true_call(self, mock_pipeline, mock_files):
        pipe = pipeline.PipelineRunner(mock_files)
        pipe.input_files = self.input
        mock_files.process.return_value = ident_path_mzid
        pipe.run()
        mock_pipeline.dda_pipeline.asser_not_called()

    # assuming the file processing did not work, the pipeline cannot be called
    # T5.3
    def test_run_false_call(self, mock_pipeline, mock_files):
        pipe = pipeline.PipelineRunner(mock_files)
        mock_files.process.return_value = False
        pipe.run()
        mock_pipeline.dda_pipeline.asser_not_called()

    # assuming the file processing did work but pipeline throws exception
    # T5.4
    @mock.patch('builtins.print')
    def test_run_false_message(self, mock_print, mock_pipeline, mock_files):
        mock_pipeline.side_effect = Exception("ERROR")
        pipe = pipeline.PipelineRunner(mock_files)
        mock_files.process.return_value = True
        pipe.run()
        assert mock_print.getvalue().startswith('ERROR:')