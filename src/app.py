import sys
import os
import json

# from PyQt5.QtCore import QSize, Qt
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pastaq

class ParametersWidget(QTabWidget):
   def __init__(self, parent = None):
      super(ParametersWidget, self).__init__(parent)
      self.input_files_tab = QWidget()
      self.parameters_tab = QWidget()

      self.addTab(self.input_files_tab, "Input files")
      self.addTab(self.parameters_tab, "Parameters")
      self.input_files_tab_ui()
      self.parameters_tab_ui()

   def input_files_tab_ui(self):
      layout = QFormLayout()
      layout.addRow("files", QLineEdit())
      layout.addRow("go", QLineEdit())
      layout.addRow("here", QLineEdit())
      self.input_files_tab.setLayout(layout)

   def parameters_tab_ui(self):
      layout = QFormLayout()
      sex = QHBoxLayout()
      sex.addWidget(QRadioButton("parameters"))
      sex.addWidget(QRadioButton("go"))
      layout.addRow(QLabel("here"),sex)
      self.parameters_tab.setLayout(layout)

class MainWindow(QMainWindow):
    parameters = {}
    project_path = ''

    def __init__(self):
        super().__init__()

        self.setWindowTitle("PASTAQ: DDA Pipeline")

        # NOTE: Setting up a fixed window size for now.
        self.setFixedSize(QSize(1024, 800))

        # Main layout
        layout = QVBoxLayout()

        #
        # Control panel.
        #
        self.new_project_btn = QPushButton("New project")
        self.new_project_btn.clicked.connect(self.new_project)
        self.open_project_btn = QPushButton("Open project")
        self.open_project_btn.clicked.connect(self.open_project)
        self.save_project_btn = QPushButton("Save")
        self.save_project_btn.clicked.connect(self.save_project)
        self.save_project_btn.setEnabled(False)
        self.save_project_as_btn = QPushButton("Save as")
        self.save_project_as_btn.clicked.connect(self.save_project_as)
        self.save_project_as_btn.setEnabled(False)

        self.controls_container = QWidget()
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.new_project_btn)
        controls_layout.addWidget(self.open_project_btn)
        controls_layout.addWidget(self.save_project_btn)
        controls_layout.addWidget(self.save_project_as_btn)
        self.controls_container.setLayout(controls_layout)
        layout.addWidget(self.controls_container)

        #
        # Project variables.
        #
        self.project_variables_container = QWidget()
        project_variables_layout = QFormLayout()
        project_variables_layout.addRow("Project name", QLineEdit())
        project_variables_layout.addRow("Project description", QLineEdit())
        project_variables_layout.addRow("Project file", QLineEdit())
        self.project_variables_container.setLayout(project_variables_layout)
        layout.addWidget(self.project_variables_container)

        #
        # Tabbed input files/parameters
        #
        self.parameters_container = ParametersWidget()
        layout.addWidget(self.parameters_container)

        #
        # Run button
        #
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_pipeline)
        layout.addWidget(self.run_btn)

        container = QWidget()
        container.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

    def new_project(self):
        print("new project")
        path = QFileDialog.getExistingDirectory(
                parent=self,
                caption="Select project file",
                directory=os.getcwd(),
        )
        if len(path) > 0:
            self.project_path = os.path.join(path, "parameters.json")
            self.parameters = pastaq.default_parameters('orbitrap', 10)
            self.save_project_btn.setEnabled(True)
            self.save_project_as_btn.setEnabled(True)
            self.save_project()

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Select project file",
                directory=os.getcwd(),
                filter="Project file (*.json)",
        )
        if len(path) > 0:
            tmp = json.loads(open(path).read())
            # TODO: Validate parameters
            valid = True
            if valid:
                self.parameters = tmp
                self.save_project_btn.setEnabled(True)
                self.save_project_as_btn.setEnabled(True)
                # TODO: Update the GUI with new parameters
        print("open project:", self.parameters)

    def save_project(self):
        try:
            with open(self.project_path, 'w') as json_file:
                json.dump(self.parameters, json_file)
        except:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText("Error")
            error_dialog.setInformativeText("Can't save project at the given directory")
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()

    def save_project_as(self):
        path = QFileDialog.getExistingDirectory(
                parent=self,
                caption="Select project file",
                directory=os.getcwd(),
        )
        if len(path) > 0:
            self.project_path = os.path.join(path, "parameters.json")
            self.save_project()

    def run_pipeline(self):
        # Disable this window so that buttons can't be clicked.
        self.run_btn.setText("Running...")
        self.run_btn.setEnabled(False)
        self.controls_container.setEnabled(False)
        self.project_variables_container.setEnabled(False)
        self.parameters_container.setEnabled(False)

        # TODO: Open modal with log progress and cancel button.
        # TODO: Run pipeline in a different thread/fork.

        print("Running")

# Initialize main window.
app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Start the event loop.
app.exec()

# DEBUG: This gets executed on exit.
print("DONE: exiting")
