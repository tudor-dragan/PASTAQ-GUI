#import pytest

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from files import FileProcessor
from pathlib import Path

file_processor = FileProcessor()

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
    test_make_pep_path()
    test_make_mzid_path()