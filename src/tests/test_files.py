import pytest

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from files import FileProcessor
from pathlib import Path

file_processor = FileProcessor()

