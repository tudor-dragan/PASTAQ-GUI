import sys
import os
import json
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pastaq


# TODO: Create custom file picker widget that shows the name of the picked files
# TODO: Switch the cwd to the project directory and/or use it instead of os.getcwd()

class EditFileDialog(QDialog):
    group = ''
    mzid_paths = []

    def __init__(self, parent=None):
        super().__init__(parent)

        # TODO: Set fixed size for this.
        self.setWindowTitle("PASTAQ: DDA Pipeline - Add files")

        # Edit parameters.
        form_container = QWidget()
        form_layout = QFormLayout()
        self.group_box = QLineEdit()
        self.group_box.textChanged.connect(self.set_group)
        mzid_picker = QPushButton("Find")
        mzid_picker.clicked.connect(self.set_mzid_paths)
        form_layout.addRow("Group", self.group_box)
        form_layout.addRow("mzID", mzid_picker)
        form_container.setLayout(form_layout)

        # Dialog buttons (Ok/Cancel).
        dialog_buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttons = QDialogButtonBox(dialog_buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(form_container)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def set_group(self):
        self.group = self.group_box.text()

    def set_mzid_paths(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
                parent=self,
                caption="Select input files",
                directory=os.getcwd(),
                filter="Identification files (*.mzID *.mzIdentML)",
        )
        if len(file_paths) > 0:
            self.mzid_paths = file_paths

class ParameterItem(QWidget):
    def __init__(self, label, widget, parent=None):
        QWidget.__init__(self, parent=parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(label))
        layout.addWidget(widget)

class TextStream(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))

class PipelineRunner(QThread):
    done = pyqtSignal()
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        # TODO: MOCKUP run pipeline here.
        print("Starting thread")
        time.sleep(2)
        print("Finished thread")
        self.done.emit()

class PipelineLog(QDialog):
    group = ''
    mzid_paths = []

    def __init__(self, parent=None):
        super().__init__(parent)

        # TODO: Set fixed size for this.
        self.setWindowTitle("PASTAQ: DDA Pipeline (Running)")

        # Add custom output to text stream.
        sys.stdout = TextStream(text_written=self.append_text)

        # Log text box.
        self.text_box = QTextEdit()

        # Dialog buttons (Ok/Cancel).
        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.exit_failure)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_box)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

        # Setup pipeline thread.
        self.pipeline_thread = PipelineRunner()
        self.pipeline_thread.done.connect(self.exit_success)
        self.pipeline_thread.start()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def append_text(self, text):
        cursor = self.text_box.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)

    def exit_success(self):
        # Restore stdout pipe.
        sys.stdout = sys.__stdout__

        # Replace button to OK instead of Cancel.
        new_buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        new_buttons.accepted.connect(self.accept)
        self.layout.replaceWidget(self.buttons, new_buttons)
        self.buttons = new_buttons

    def exit_failure(self):
        # Restore stdout pipe.
        sys.stdout = sys.__stdout__
        self.pipeline_thread.terminate()
        self.reject()

class ParametersWidget(QTabWidget):
    input_files = []
    parameters = {}

    def __init__(self, parent = None):
        super(ParametersWidget, self).__init__(parent)
        self.input_files_tab = QWidget()
        self.parameters_tab = QScrollArea()

        self.addTab(self.input_files_tab, "Input files")
        self.addTab(self.parameters_tab, "Parameters")
        self.input_files_tab_ui()
        self.parameters_tab_ui()

    def input_files_tab_ui(self):
        self.input_files_table = QTableWidget()
        self.input_files_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.input_files_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.input_files_table.setRowCount(0)
        self.input_files_table.setColumnCount(4)
        self.input_files_table.setFocusPolicy(False)
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

        # Buttons.
        self.add_file_btn = QPushButton("Add")
        self.add_file_btn.clicked.connect(self.add_file)
        self.edit_file_btn = QPushButton("Edit")
        self.edit_file_btn.clicked.connect(self.edit_file)
        self.remove_file_btn = QPushButton("Remove")
        self.remove_file_btn.clicked.connect(self.remove_file)

        self.input_file_buttons = QWidget()
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.add_file_btn)
        controls_layout.addWidget(self.edit_file_btn)
        controls_layout.addWidget(self.remove_file_btn)
        self.input_file_buttons.setLayout(controls_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.input_file_buttons)
        layout.addWidget(self.input_files_table)
        self.input_files_tab.setLayout(layout)

    def add_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
                parent=self,
                caption="Select input files",
                directory=os.getcwd(),
                filter="MS files (*.mzXML *.mzML)",
        )
        if len(file_paths) > 0:
            input_files = self.input_files
            current_files = [file['raw_path'] for file in self.input_files]
            for file_path in file_paths:
                if file_path not in current_files:
                    input_files.append({'raw_path': file_path, 'reference': False})
            self.update_input_files(input_files)

    def edit_file(self):
        indexes = self.find_selected_files()
        if len(indexes) == 0:
            return

        edit_file_dialog = EditFileDialog(self)
        if edit_file_dialog.exec():
            old_list = self.input_files
            new_list = []
            for i, file in enumerate(old_list):
                if i in indexes:
                    new_file = file
                    new_file['group'] = edit_file_dialog.group

                    # When only 1 file is selected mzID can have any name, if
                    # multiple files are selected, the stem of raw_path and
                    # ident_path will be matched.
                    if len(indexes) == 1 and len(edit_file_dialog.mzid_paths) == 1:
                        new_file['ident_path'] = edit_file_dialog.mzid_paths[0]
                    else:
                        base_name = os.path.basename(file['raw_path'])
                        base_name = os.path.splitext(base_name)
                        stem = base_name[0]
                        for mzid in edit_file_dialog.mzid_paths:
                            base_name = os.path.basename(mzid)
                            base_name = os.path.splitext(base_name)
                            mzid_stem = base_name[0]
                            if mzid_stem == stem:
                                new_file['ident_path'] = mzid
                                break

                    new_list += [new_file]
                else:
                    new_list += [file]
            self.update_input_files(new_list)

    def remove_file(self):
        indexes = self.find_selected_files()
        if len(indexes) > 0:
            old_list = self.input_files
            new_list = []
            for i, file in enumerate(old_list):
                if i not in indexes:
                    new_list += [file]
            self.update_input_files(new_list)

    def find_selected_files(self):
        selected_ranges = self.input_files_table.selectedRanges()
        indexes = []
        for sel in selected_ranges:
            for i in range(sel.topRow(), sel.bottomRow() + 1):
                indexes += [i]
        return indexes

    def update_input_files(self, input_files):
        self.input_files = input_files
        self.input_files_table.setRowCount(len(self.input_files))
        for i, input_file in enumerate(self.input_files):
            label = QLabel(input_file['raw_path'])
            self.input_files_table.setCellWidget(i, 0, label)
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
                checkbox.stateChanged.connect(self.toggle_reference)
                self.input_files_table.setCellWidget(i, 3, cell_widget)

    def toggle_reference(self):
        for row in range(self.input_files_table.rowCount()):
            checkbox = self.input_files_table.cellWidget(row, 3).children()[1]
            self.input_files[row]['reference'] = checkbox.isChecked()

    def parameters_tab_ui(self):
        # TODO: Maybe we should add the constrains and default values in
        # a dictionary format. Parameters are not going to change often, so
        # probably is fine with hardcoding the ranges here.
        LARGE = 1000000000

        # Instruments
        self.inst_settings_box = QGroupBox("Instrument Settings")
        grid_layout_inst = QGridLayout()

        self.inst_type = QComboBox()
        self.inst_type.addItems(["Orbitrap", "TOF", "FT-ICR", "Quadrupole"])
        grid_layout_inst.addWidget(ParameterItem("Instrument Type", self.inst_type), 0, 0)

        self.res_ms1 = QSpinBox()
        self.res_ms1.setRange(-LARGE, LARGE)
        self.res_ms1.setValue(70000)
        grid_layout_inst.addWidget(ParameterItem("Resolution MS1", self.res_ms1), 0, 1)

        self.res_ms2 = QSpinBox()
        self.res_ms2.setRange(-LARGE, LARGE)
        self.res_ms2.setValue(30000)
        grid_layout_inst.addWidget(ParameterItem("Resolution MS2", self.res_ms2), 0, 2)

        self.reference_mz = QSpinBox()
        self.reference_mz.setRange(-LARGE, LARGE)
        self.reference_mz.setValue(70000)
        grid_layout_inst.addWidget(ParameterItem("Reference m/z", self.reference_mz), 1, 0)

        self.avg_fwhm_rt = QSpinBox()
        self.avg_fwhm_rt.setRange(-LARGE, LARGE)
        self.avg_fwhm_rt.setValue(30000)
        grid_layout_inst.addWidget(ParameterItem("Avg FWHM RT", self.avg_fwhm_rt), 1, 1)

        self.inst_settings_box.setLayout(grid_layout_inst)

        # Resampling
        self.resampling_box = QGroupBox("Resampling")
        grid_layout_resamp = QGridLayout()

        self.num_samples_mz = QSpinBox()
        self.num_samples_mz.setRange(-LARGE, LARGE)
        self.num_samples_mz.setValue(5)
        grid_layout_resamp.addWidget(ParameterItem("Num Samples MZ", self.num_samples_mz), 0, 0)

        self.num_samples_rt = QSpinBox()
        self.num_samples_rt.setRange(-LARGE, LARGE)
        self.num_samples_rt.setValue(5)
        grid_layout_resamp.addWidget(ParameterItem("Num Samples RT", self.num_samples_rt), 0, 1)

        self.smoothing_coefficient_mz = QSpinBox()
        self.smoothing_coefficient_mz.setRange(-LARGE, LARGE)
        self.smoothing_coefficient_mz.setValue(70000)
        grid_layout_resamp.addWidget(ParameterItem("Smoothing Coefficient MZ", self.smoothing_coefficient_mz), 0, 2)

        self.smoothing_coefficient_rt = QSpinBox()
        self.smoothing_coefficient_rt.setRange(-LARGE, LARGE)
        self.smoothing_coefficient_rt.setValue(70000)
        grid_layout_resamp.addWidget(ParameterItem("Smoothing Coefficient RT", self.smoothing_coefficient_rt), 1, 0)
        self.resampling_box.setLayout(grid_layout_resamp)

        # Warp2D
        self.warp_box = QGroupBox("Warp2D")
        grid_layout_warp = QGridLayout()

        self.warp2d_slack = QSpinBox()
        self.warp2d_slack.setRange(-LARGE, LARGE)
        self.warp2d_slack.setValue(5)
        grid_layout_warp.addWidget(ParameterItem("Slack", self.warp2d_slack), 0, 0)

        self.warp2d_window_size = QSpinBox()
        self.warp2d_window_size.setRange(-LARGE, LARGE)
        self.warp2d_window_size.setValue(5)
        grid_layout_warp.addWidget(ParameterItem("Window Size", self.warp2d_window_size), 0, 1)

        self.warp2d_num_points = QSpinBox()
        self.warp2d_num_points.setRange(-LARGE, LARGE)
        self.warp2d_num_points.setValue(70000)
        grid_layout_warp.addWidget(ParameterItem("Number of Points", self.warp2d_num_points), 0, 2)

        self.warp2d_rt_expand_factor = QSpinBox()
        self.warp2d_rt_expand_factor.setRange(-LARGE, LARGE)
        self.warp2d_rt_expand_factor.setValue(70000)
        grid_layout_warp.addWidget(ParameterItem("RT Expand Factor", self.warp2d_rt_expand_factor), 1, 0)
        self.warp_box.setLayout(grid_layout_warp)

        self.warp2d_peaks_per_window = QSpinBox()
        self.warp2d_peaks_per_window.setRange(-LARGE, LARGE)
        self.warp2d_peaks_per_window.setValue(70000)
        grid_layout_warp.addWidget(ParameterItem("Peaks Per Window", self.warp2d_peaks_per_window), 1, 1)
        self.warp_box.setLayout(grid_layout_warp)

        # MetaMatch
        self.meta_box = QGroupBox("MetaMatch")
        grid_layout_meta = QGridLayout()

        self.metamatch_fraction = QSpinBox()
        self.metamatch_fraction.setRange(-LARGE, LARGE)
        self.metamatch_fraction.setValue(5)
        grid_layout_meta.addWidget(ParameterItem("Slack", self.metamatch_fraction), 0, 0)

        self.metamatch_n_sig_mz = QSpinBox()
        self.metamatch_n_sig_mz.setRange(-LARGE, LARGE)
        self.metamatch_n_sig_mz.setValue(5)
        grid_layout_meta.addWidget(ParameterItem("Window Size", self.metamatch_n_sig_mz), 0, 1)

        self.metamatch_n_sig_rt = QSpinBox()
        self.metamatch_n_sig_rt.setRange(-LARGE, LARGE)
        self.metamatch_n_sig_rt.setValue(70000)
        grid_layout_meta.addWidget(ParameterItem("Number of Points", self.metamatch_n_sig_rt), 0, 2)
        self.meta_box.setLayout(grid_layout_meta)

        # Identification
        self.ident_box = QGroupBox("Identification")
        grid_layout_ident = QGridLayout()

        self.ident_max_rank_only = QCheckBox()
        grid_layout_ident.addWidget(ParameterItem("Max Rank Only", self.ident_max_rank_only), 0, 0)

        self.metamatch_n_sig_mz = QCheckBox()
        grid_layout_ident.addWidget(ParameterItem("Require Threshold", self.metamatch_n_sig_mz), 0, 1)

        self.metamatch_n_sig_rt = QCheckBox()
        grid_layout_ident.addWidget(ParameterItem("Ignore Decoy", self.metamatch_n_sig_rt), 0, 2)
        self.ident_box.setLayout(grid_layout_ident)

        # TODO: Add all parameters.

        # Enable scrolling
        content_widget = QWidget()
        self.parameters_tab.setWidget(content_widget)
        self.parameters_tab.setWidgetResizable(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.inst_settings_box)
        vbox.addWidget(self.resampling_box)
        vbox.addWidget(self.warp_box)
        vbox.addWidget(self.meta_box)
        vbox.addWidget(self.ident_box)

        content_widget.setLayout(vbox)

class MainWindow(QMainWindow):
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
        self.parameters_container.parameters['project_name'] = self.project_name_ui.text()

    def set_project_description(self):
        self.parameters_container.parameters['project_description'] = self.project_description_ui.text()

    def update_ui(self):
        # TODO: Update the GUI with all parameters
        self.project_directory_ui.setText(os.path.dirname(self.project_path))
        if "project_name" in self.parameters_container.parameters:
            self.project_name_ui.setText(self.parameters_container.parameters['project_name'])
        if "project_description" in self.parameters_container.parameters:
            self.project_description_ui.setText(self.parameters_container.parameters['project_description'])

    def new_project(self):
        dir_path = QFileDialog.getExistingDirectory(
                parent=self,
                caption="Select project directory",
                directory=os.getcwd(),
        )
        if len(dir_path) > 0:
            # TODO: Check if the project file already exists and show a warning
            # dialog to let the user overwrite it.
            self.project_path = os.path.join(dir_path, "parameters.json")
            self.parameters_container.parameters = pastaq.default_parameters('orbitrap', 10)
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
                self.parameters_container.parameters = tmp
                self.project_path = file_path
                self.save_project_btn.setEnabled(True)
                self.save_project_as_btn.setEnabled(True)
                self.run_btn.setEnabled(True)
                self.project_variables_container.setEnabled(True)
                self.parameters_container.setEnabled(True)
                if "input_files" in self.parameters_container.parameters:
                    self.parameters_container.update_input_files(self.parameters_container.parameters['input_files'])
                self.update_ui()

    def save_project(self):
        try:
            with open(self.project_path, 'w') as json_file:
                params = self.parameters_container.parameters
                params['input_files'] = self.parameters_container.input_files
                json.dump(params, json_file)
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
        pipeline_log_dialog = PipelineLog(self)
        print("Running pipeline")
        if pipeline_log_dialog.exec():
            print("DONE")
        # TODO: Run pipeline in a different thread/fork.

# Initialize main window.
app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Start the event loop.
app.exec()
