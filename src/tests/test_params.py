import os, sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QSpinBox, QAbstractSpinBox
from PyQt5.QtWidgets import QWidget, QLineEdit, QDoubleSpinBox, QCheckBox
from PyQt5.QtWidgets import QPushButton, QFileDialog, QScrollArea, QComboBox, QLabel
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QHBoxLayout, QGroupBox, QGridLayout

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from parameter import init_button_params

import pytest



assert True

def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4

def test_init_button_params():
    button = init_button_params("test_label", "test_tooltip")
    assert button.toolTip == "test_tooltip"
