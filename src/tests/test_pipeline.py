import os,sys

from files import FileProcessor
from pipeline import PipelineLogDialog,PipelineRunner
from app import MainWindow

from PyQt5.QtWidgets import QDialog, QTextEdit, QDialogButtonBox, QVBoxLayout

# This is done for importing from a parent directory
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

#
# FIXTURES (these are functions that are run before tests for setup purposes)
#

#
# UNIT TESTS
#

#R1.10
def test_msfragger_param_execution():
    fileProcessor = FileProcessor()

    input = 'test.mgf'
    params = 'test.params'

    fileProcessor.load_params_path(params)
    fileProcessor.execute_msfragger(input)

#R1.12
def test_execution_identification_processing():
    pipelineRunner = PipelineRunner(FileProcessor())

    input = 'test.mgf'
    expectedOutput = 'test.mzID'
    
    pipelineRunner.input_files=input
    pipelineRunner.start()
    actualOutput = pipelineRunner.input_files
    assert actualOutput == expectedOutput

#R1.11
def test_msfragger_process_mgf():
    fileProcessor = FileProcessor()

    input = 'test.mgf'
    expectedOutput = 'test.pepXML'
    
    fileProcessor.execute_msfragger(input)
    actualOutput = fileProcessor.make_pep_path(input)
    assert actualOutput == expectedOutput

#R1.13
def test_idconvert_convert_mzid():
    fileProcessor = FileProcessor()

    input = 'test.mgf'
    expectedOutput = 'test.mzIDL'
    fileProcessor.execute_msfragger(input)
    pep = fileProcessor.make_pep_path(input)

    fileProcessor.execute_idconvert(pep,input)
    actualOutput = fileProcessor.make_mzid_path(input)
    assert actualOutput == expectedOutput

#R1.14
def test_discarding_pepXML():
    fileProcessor = FileProcessor()
    
    input = 'test.mgf'
    fileProcessor.execute_msfragger(input)
    pep = fileProcessor.make_pep_path(input)
    
    fileProcessor.delete_pep(pep)
    assert (not os.path.exists(pep))


#R1.15
def test_pipeline_output():
    pipelineRunner = PipelineRunner()

    input = 'test.mgf'

    pipelineRunner.input_files=input
    pipelineRunner.start()

#R1.18
def test_display_cancel_button():
    pipelineLogDialog = PipelineLogDialog()
    
    text_box =pipelineLogDialog.init_log()
    button = QDialogButtonBox(QDialogButtonBox.Ok)
    expectedLayout = pipelineLogDialog.init_layout(button, text_box)
    
    pipelineLogDialog.exit_success()
    actualLayout = pipelineLogDialog.layout
    assert actualLayout == expectedLayout

#R2.2
def test_cancelling_pipeline_crash():
    pipelineLogDialog = PipelineLogDialog()

    pipelineLogDialog.exit_failure()
    assert True
