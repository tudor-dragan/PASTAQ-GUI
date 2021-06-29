import sys
import os
import json

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pastaq

class ParametersWidget(QTabWidget):
    input_files = [
            {'reference': True,  'raw_path': '/path/to/mzxml/1_1.mzXML', 'group': 'a', 'ident_path': '/path/to/mzidentml/1_1.mzid'},
            {'reference': True,  'raw_path': '/path/to/mzxml/1_2.mzXML', 'group': 'a', 'ident_path': '/path/to/mzidentml/1_2.mzid'},
            {'reference': False, 'raw_path': '/path/to/mzxml/1_3.mzXML', 'group': 'a', 'ident_path': '/path/to/mzidentml/1_3.mzid'},
    ]

    def __init__(self, parent = None):
        super(ParametersWidget, self).__init__(parent)
        self.input_files_tab = QWidget()
        self.parameters_tab = QWidget()

        self.addTab(self.input_files_tab, "Input files")
        self.addTab(self.parameters_tab, "Parameters")
        self.input_files_tab_ui()
        self.parameters_tab_ui()

    def input_files_tab_ui(self):
        self.input_files_table = QTableWidget()
        self.input_files_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.input_files_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.input_files_table.setRowCount(len(self.input_files))
        self.input_files_table.setColumnCount(4)
        column_names = [
            "Raw File (mzXML/mzML)",
            "Identification file (mzID)",
            "Group",
            "Reference"
        ]
        self.input_files_table.setHorizontalHeaderLabels(column_names)
        self.input_files_table.verticalHeader().hide()
        header = self.input_files_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        for i, input_file in enumerate(self.input_files):
            self.input_files_table.setCellWidget(i, 0, QLabel(input_file['raw_path']))
            if 'ident_path' in input_file:
                self.input_files_table.setCellWidget(i, 1, QLabel(input_file['ident_path']))
            if 'group' in input_file:
                label = QLabel(input_file['group'])
                label.setAlignment(Qt.AlignCenter)
                self.input_files_table.setCellWidget(i, 2, label)
            if 'reference' in input_file:
                cell_widget = QWidget()
                checkbox = QCheckBox()
                if input_file['reference']:
                    checkbox.setCheckState(Qt.Checked)
                lay_out = QHBoxLayout(cell_widget)
                lay_out.addWidget(checkbox)
                lay_out.setAlignment(Qt.AlignCenter)
                lay_out.setContentsMargins(0, 0, 0, 0)
                cell_widget.setLayout(lay_out)
                self.input_files_table.setCellWidget(i, 3, cell_widget)
                # TODO: Toggle the reference when the checkbox is ticked

        layout = QVBoxLayout()
        layout.addWidget(self.input_files_table)
        self.input_files_tab.setLayout(layout)

    def parameters_tab_ui(self):
        layout = QFormLayout()
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
        self.project_name_ui = QLineEdit()
        self.project_name_ui.textChanged.connect(self.set_project_name)
        self.project_description_ui = QLineEdit()
        self.project_description_ui.textChanged.connect(self.set_project_description)
        self.project_directory_ui = QLineEdit()
        project_variables_layout.addRow("Project name", self.project_name_ui)
        project_variables_layout.addRow("Project description", self.project_description_ui)
        project_variables_layout.addRow("Project directory", self.project_directory_ui)
        self.project_directory_ui.setEnabled(False)
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

        self.run_btn.setEnabled(False)
        self.project_variables_container.setEnabled(False)
        self.parameters_container.setEnabled(False)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

    def set_project_name(self):
        self.parameters['project_name'] = self.project_name_ui.text()

    def set_project_description(self):
        self.parameters['project_description'] = self.project_description_ui.text()

    def update_ui(self):
        # TODO: Update the GUI with all parameters
        self.project_directory_ui.setText(os.path.dirname(self.project_path))
        if "project_name" in self.parameters:
            self.project_name_ui.setText(self.parameters['project_name'])
        if "project_description" in self.parameters:
            self.project_description_ui.setText(self.parameters['project_description'])

    def new_project(self):
        print("new project")
        dir_path = QFileDialog.getExistingDirectory(
                parent=self,
                caption="Select project directory",
                directory=os.getcwd(),
        )
        if len(dir_path) > 0:
            # TODO: Check if the project file already exists and show a warning
            # dialog to let the user overwrite it.
            self.project_path = os.path.join(dir_path, "parameters.json")
            self.parameters = pastaq.default_parameters('orbitrap', 10)
            self.save_project_btn.setEnabled(True)
            self.save_project_as_btn.setEnabled(True)
            self.run_btn.setEnabled(True)
            self.project_variables_container.setEnabled(True)
            self.parameters_container.setEnabled(True)
            self.update_ui()
            self.save_project()

    def open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Select project file",
                directory=os.getcwd(),
                filter="Project file (*.json)",
        )
        if len(file_path) > 0:
            tmp = json.loads(open(file_path).read())
            # TODO: Validate parameters
            valid = True
            if valid:
                self.parameters = tmp
                self.project_path = file_path
                self.save_project_btn.setEnabled(True)
                self.save_project_as_btn.setEnabled(True)
                self.run_btn.setEnabled(True)
                self.project_variables_container.setEnabled(True)
                self.parameters_container.setEnabled(True)
                self.update_ui()

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
            self.update_ui()
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
