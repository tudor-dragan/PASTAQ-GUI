import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import files
from pathlib import Path

file_processor = files.FileProcessor()

def test_check_path():
    filename = 'test.txt'
    open(filename, 'w').close()
    assert file_processor.check_path(filename)
    os.remove(filename)
    assert not file_processor.check_path(filename)

def test_load_ms_path():
    assert not file_processor.ms_jar[0]
    filename = 'test.jar'
    assert not file_processor.load_ms_path(filename)
    assert not file_processor.ms_jar[0]
    open(filename, 'w').close()
    assert file_processor.load_ms_path(filename)
    assert file_processor.ms_jar[0]
    assert file_processor.ms_jar[1] == filename
    os.remove(filename)

def test_load_id_path():
    assert not file_processor.id_file[0]
    filename = 'test.exe'
    assert not file_processor.load_id_path(filename)
    assert not file_processor.id_file[0]
    open(filename, 'w').close()
    assert file_processor.load_id_path(filename)
    assert file_processor.id_file[0]
    assert file_processor.id_file[1] == filename
    os.remove(filename)

def test_load_params_path():
    assert not file_processor.params[0]
    filename = 'test.params'
    open(filename, 'w').close()
    file_processor.load_params_path(filename)
    assert file_processor.params[0]
    assert file_processor.params[1] == filename
    os.remove(filename)

def test_get_ms():
    dir = 'test'
    filename = 'test.jar'
    path = os.path.join(dir, filename)
    file_processor.ms_jar[1] = path
    d, f = file_processor.get_ms()
    assert d == dir
    assert f == filename


def test_make_pep_path():
    input = 'test.mgf'
    expected_output = 'test.pepxml'
    actual_output = FileProcessor.make_pep_path(input)
    assert expected_output == actual_output

def test_make_mzid_path():
    input = 'test.mgf'
    expected_output = 'test.mzID'
    actual_output = FileProcessor.make_mzid_path(input)
    assert expected_output == actual_output

def tests_CI():
    test_check_path()
    test_get_ms()
    test_load_ms_path()
    test_load_id_path()
    test_load_params_path()
    test_make_pep_path()
    test_make_mzid_path()
