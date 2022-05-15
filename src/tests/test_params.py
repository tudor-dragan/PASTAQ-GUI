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
from app import MainWindow

import pytest


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4

# test if the tooltip is correctly set
def test_init_button_params():
    button = init_button_params("test_label", "test_tooltip")
    print(button.toolTip)
    assert button.toolTip() == "test_tooltip"

def test_PrameterItem():
    # a test here
    assert True

def test_multiple_id_files():
    # a test here
    assert True

# test if the name of the parameter is correctly set
def test_init_label():
    label = init_label("test_text")
    assert label.text() == "test_text"


def test_input_files_tab(qtbot):
    window = MainWindow()
    #window.show()
    qtbot.addWidget(window)
    window.open_project()

    #this will click the add file button in the gui but unfortunately i cant figure out how to select a file
    qtbot.mouseClick(window.parameters_container.input_files_tab.findChildren(QPushButton)[0], Qt.LeftButton)
    #qtbot.mouseClick(window.findChildren(QFileDialog)[0].browseButton, Qt.LeftButton)
    qtbot.keyClicks(window.findChildren(QFileDialog)[0], 'proj')
    return


