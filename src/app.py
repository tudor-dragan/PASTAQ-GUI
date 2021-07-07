import sys
import os
import json
import time

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import pastaq


# TODO: Create custom file picker widget that shows the name of the picked files
# TODO: Switch the cwd to the project directory and/or use it instead of os.getcwd()
# TODO: The RUN button should only be access when there is at least 1 sample active.

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
    finished = pyqtSignal()

    params = {}
    input_files = []
    output_dir = ''

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        print("Starting DDA Pipeline")
        time.sleep(1)

        try:
            pastaq.dda_pipeline(self.params, self.input_files, self.output_dir)
        except Exception as e:
            print("ERROR:", e)

        self.finished.emit()

class PipelineLogDialog(QDialog):
    group = ''
    mzid_paths = []

    def __init__(self, params, input_files, output_dir, parent=None):
        super().__init__(parent)

        # TODO: Set fixed size for this.
        self.setWindowTitle("PASTAQ: DDA Pipeline (Running)")

        # Add custom output to text stream.
        sys.stdout = TextStream(text_written=self.append_text)

        # Log text box.
        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)

        # Dialog buttons (Ok/Cancel).
        self.buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.buttons.rejected.connect(self.exit_failure)

        # Prepare layout.
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text_box)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

        self.pipeline_thread = PipelineRunner()
        self.pipeline_thread.params = params
        self.pipeline_thread.input_files = input_files
        self.pipeline_thread.output_dir = output_dir
        self.pipeline_thread.finished.connect(self.exit_success)
        self.pipeline_thread.start()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def append_text(self, text):
        cursor = self.text_box.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.text_box.setTextCursor(cursor)
        self.text_box.ensureCursorVisible()

    def exit_success(self):
        # Restore stdout pipe.
        sys.stdout = sys.__stdout__

        # Replace button to OK instead of Cancel.
        new_buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        new_buttons.accepted.connect(self.accept)
        self.layout.replaceWidget(self.buttons, new_buttons)
        self.buttons = new_buttons

    def exit_failure(self):
        # TODO: Confirm we want to exit, since this could lead to corrupt
        # temporary files.

        # Restore stdout pipe.
        sys.stdout = sys.__stdout__
        self.pipeline_thread.quit()
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

        # TODO: Add tooltips.
        # TODO: Make sure constrains are set properly.

        self.update_allowed = False

        # Instruments
        self.inst_settings_box = QGroupBox("Instrument Settings")
        grid_layout_inst = QGridLayout()

        self.inst_type = QComboBox()
        self.inst_type.addItems(["orbitrap", "tof", "ft-icr", "quadrupole"])
        self.inst_type.currentIndexChanged.connect(self.update_parameters)
        grid_layout_inst.addWidget(ParameterItem("Instrument Type", self.inst_type), 0, 0)

        self.res_ms1 = QSpinBox()
        self.res_ms1.setRange(-LARGE, LARGE)
        self.res_ms1.valueChanged.connect(self.update_parameters)
        grid_layout_inst.addWidget(ParameterItem("Resolution MS1", self.res_ms1), 0, 1)

        self.res_ms2 = QSpinBox()
        self.res_ms2.setRange(-LARGE, LARGE)
        self.res_ms2.valueChanged.connect(self.update_parameters)
        grid_layout_inst.addWidget(ParameterItem("Resolution MS2", self.res_ms2), 0, 2)

        self.reference_mz = QSpinBox()
        self.reference_mz.setRange(-LARGE, LARGE)
        self.reference_mz.valueChanged.connect(self.update_parameters)
        grid_layout_inst.addWidget(ParameterItem("Reference m/z", self.reference_mz), 1, 0)

        self.avg_fwhm_rt = QSpinBox()
        self.avg_fwhm_rt.setRange(-LARGE, LARGE)
        self.avg_fwhm_rt.valueChanged.connect(self.update_parameters)
        grid_layout_inst.addWidget(ParameterItem("Avg FWHM RT", self.avg_fwhm_rt), 1, 1)

        self.inst_settings_box.setLayout(grid_layout_inst)

        # Resampling
        self.resampling_box = QGroupBox("Resampling")
        grid_layout_resamp = QGridLayout()

        self.num_samples_mz = QSpinBox()
        self.num_samples_mz.setRange(-LARGE, LARGE)
        self.num_samples_mz.valueChanged.connect(self.update_parameters)
        grid_layout_resamp.addWidget(ParameterItem("Number of samples m/z", self.num_samples_mz), 0, 0)

        self.num_samples_rt = QSpinBox()
        self.num_samples_rt.setRange(-LARGE, LARGE)
        self.num_samples_rt.valueChanged.connect(self.update_parameters)
        grid_layout_resamp.addWidget(ParameterItem("Number of samples rt", self.num_samples_rt), 0, 1)

        self.smoothing_coefficient_mz = QDoubleSpinBox()
        self.smoothing_coefficient_mz.setRange(-LARGE, LARGE)
        self.smoothing_coefficient_mz.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.smoothing_coefficient_mz.valueChanged.connect(self.update_parameters)
        grid_layout_resamp.addWidget(ParameterItem("Smoothing coefficient (m/z)", self.smoothing_coefficient_mz), 0, 2)

        self.smoothing_coefficient_rt = QDoubleSpinBox()
        self.smoothing_coefficient_rt.setRange(-LARGE, LARGE)
        self.smoothing_coefficient_mz.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.smoothing_coefficient_rt.valueChanged.connect(self.update_parameters)
        grid_layout_resamp.addWidget(ParameterItem("Smoothing coefficient (rt)", self.smoothing_coefficient_rt), 1, 0)
        self.resampling_box.setLayout(grid_layout_resamp)

        # Warp2D
        self.warp_box = QGroupBox("Warp2D")
        grid_layout_warp = QGridLayout()

        self.warp2d_slack = QSpinBox()
        self.warp2d_slack.setRange(-LARGE, LARGE)
        self.warp2d_slack.valueChanged.connect(self.update_parameters)
        grid_layout_warp.addWidget(ParameterItem("Slack", self.warp2d_slack), 0, 0)

        self.warp2d_window_size = QSpinBox()
        self.warp2d_window_size.setRange(-LARGE, LARGE)
        self.warp2d_window_size.valueChanged.connect(self.update_parameters)
        grid_layout_warp.addWidget(ParameterItem("Window Size", self.warp2d_window_size), 0, 1)

        self.warp2d_num_points = QSpinBox()
        self.warp2d_num_points.setRange(-LARGE, LARGE)
        self.warp2d_num_points.valueChanged.connect(self.update_parameters)
        grid_layout_warp.addWidget(ParameterItem("Number of points", self.warp2d_num_points), 0, 2)

        self.warp2d_rt_expand_factor = QDoubleSpinBox()
        self.warp2d_rt_expand_factor.setRange(-LARGE, LARGE)
        self.warp2d_rt_expand_factor.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.warp2d_rt_expand_factor.valueChanged.connect(self.update_parameters)
        grid_layout_warp.addWidget(ParameterItem("Expand factor rt", self.warp2d_rt_expand_factor), 1, 0)
        self.warp_box.setLayout(grid_layout_warp)

        self.warp2d_peaks_per_window = QSpinBox()
        self.warp2d_peaks_per_window.setRange(-LARGE, LARGE)
        # self.warp2d_peaks_per_window.setValue(70000)
        self.warp2d_peaks_per_window.valueChanged.connect(self.update_parameters)
        grid_layout_warp.addWidget(ParameterItem("Peaks per window", self.warp2d_peaks_per_window), 1, 1)
        self.warp_box.setLayout(grid_layout_warp)

        # MetaMatch
        self.meta_box = QGroupBox("MetaMatch")
        grid_layout_meta = QGridLayout()

        self.metamatch_fraction = QDoubleSpinBox()
        self.metamatch_fraction.setRange(-LARGE, LARGE)
        self.metamatch_fraction.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.metamatch_fraction.valueChanged.connect(self.update_parameters)
        grid_layout_meta.addWidget(ParameterItem("Fraction of samples", self.metamatch_fraction), 0, 0)

        self.metamatch_n_sig_mz = QDoubleSpinBox()
        self.metamatch_n_sig_mz.setRange(-LARGE, LARGE)
        self.metamatch_n_sig_mz.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.metamatch_n_sig_mz.valueChanged.connect(self.update_parameters)
        grid_layout_meta.addWidget(ParameterItem("Number of sigma (m/z)", self.metamatch_n_sig_mz), 0, 1)

        self.metamatch_n_sig_rt = QDoubleSpinBox()
        self.metamatch_n_sig_rt.setRange(-LARGE, LARGE)
        self.metamatch_n_sig_rt.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.metamatch_n_sig_rt.valueChanged.connect(self.update_parameters)
        grid_layout_meta.addWidget(ParameterItem("Number of sigma (rt)", self.metamatch_n_sig_rt), 0, 2)
        self.meta_box.setLayout(grid_layout_meta)

        # Identification
        self.ident_box = QGroupBox("Identification")
        grid_layout_ident = QGridLayout()

        self.ident_max_rank_only = QCheckBox()
        self.ident_max_rank_only.stateChanged.connect(self.update_parameters)
        grid_layout_ident.addWidget(ParameterItem("Max Rank Only", self.ident_max_rank_only), 0, 0)

        self.ident_require_threshold = QCheckBox()
        self.ident_require_threshold.stateChanged.connect(self.update_parameters)
        grid_layout_ident.addWidget(ParameterItem("Require Threshold", self.ident_require_threshold), 0, 1)

        self.ident_ignore_decoy = QCheckBox()
        self.ident_ignore_decoy.stateChanged.connect(self.update_parameters)
        grid_layout_ident.addWidget(ParameterItem("Ignore Decoy", self.ident_ignore_decoy), 0, 2)
        self.ident_box.setLayout(grid_layout_ident)

        # TODO: Add the rest of parameters.

        # Enable scrolling
        content_widget = QWidget()
        self.parameters_tab.setWidget(content_widget)
        self.parameters_tab.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(self.inst_settings_box)
        layout.addWidget(self.resampling_box)
        layout.addWidget(self.warp_box)
        layout.addWidget(self.meta_box)
        layout.addWidget(self.ident_box)

        content_widget.setLayout(layout)
        self.update_allowed = True

    def update_parameters(self):
        if not self.update_allowed:
            return

        # TODO: Add remaining parameters
        print("updating params:") # DEBUG: ...
        self.parameters['instrument_type'] = self.inst_type.currentText().lower()
        self.parameters['resolution_ms1'] = self.res_ms1.value()
        self.parameters['resolution_msn'] = self.res_ms2.value()
        self.parameters['reference_mz'] = self.reference_mz.value()
        self.parameters['avg_fwhm_rt'] = self.avg_fwhm_rt.value()
        self.parameters['num_samples_mz'] = self.num_samples_mz.value()
        self.parameters['num_samples_rt'] = self.num_samples_rt.value()
        self.parameters['smoothing_coefficient_mz'] = self.smoothing_coefficient_mz.value()
        self.parameters['smoothing_coefficient_rt'] = self.smoothing_coefficient_rt.value()
        self.parameters['warp2d_slack'] = self.warp2d_slack.value()
        self.parameters['warp2d_window_size'] = self.warp2d_window_size.value()
        self.parameters['warp2d_num_points'] = self.warp2d_num_points.value()
        self.parameters['warp2d_rt_expand_factor'] = self.warp2d_rt_expand_factor.value()
        self.parameters['warp2d_peaks_per_window'] = self.warp2d_peaks_per_window.value()
        self.parameters['metamatch_fraction'] = self.metamatch_fraction.value()
        self.parameters['metamatch_n_sig_mz'] = self.metamatch_n_sig_mz.value()
        self.parameters['metamatch_n_sig_rt'] = self.metamatch_n_sig_rt.value()
        # self.parameters['feature_detection_charge_states'] = [5, 4, 3, 2, 1]
        # self.parameters['max_peaks'] = 1000000
        # self.parameters['polarity'] = 'both'
        # self.parameters['min_mz'] = 0
        # self.parameters['max_mz'] = 100000
        # self.parameters['min_rt'] = 0
        # self.parameters['max_rt'] = 100000
        # self.parameters['link_n_sig_mz'] = 3
        # self.parameters['link_n_sig_rt'] = 3
        self.parameters['ident_max_rank_only'] = self.ident_max_rank_only.isChecked()
        self.parameters['ident_require_threshold'] = self.ident_require_threshold.isChecked()
        self.parameters['ident_ignore_decoy'] = self.ident_ignore_decoy.isChecked()
        # self.parameters['similarity_num_peaks'] = 2000
        # self.parameters['qc_plot_palette'] = 'husl'
        # self.parameters['qc_plot_extension'] = 'png'
        # self.parameters['qc_plot_fill_alpha'] = 'dynamic'
        # self.parameters['qc_plot_line_alpha'] = 0.5
        # self.parameters['qc_plot_scatter_alpha'] = 0.3
        # self.parameters['qc_plot_scatter_size'] = 2
        # self.parameters['qc_plot_min_dynamic_alpha'] = 0.1
        # self.parameters['qc_plot_per_file'] = False
        # self.parameters['qc_plot_line_style'] = 'fill'
        # self.parameters['qc_plot_dpi'] = 300
        # self.parameters['qc_plot_font_family'] = 'sans-serif'
        # self.parameters['qc_plot_font_size'] = 7
        # self.parameters['qc_plot_fig_size_x'] = 7.08661
        # self.parameters['qc_plot_fig_size_y'] = 7.08661/1.618034
        # self.parameters['qc_plot_fig_legend'] = False
        # self.parameters['qc_plot_mz_vs_sigma_mz_max_peaks'] = 200000
        # self.parameters['quant_isotopes'] = 'height'
        # self.parameters['quant_features'] = 'max_height'
        # self.parameters['quant_features_charge_state_filter'] = True
        # self.parameters['quant_ident_linkage'] = 'msms_event'
        # self.parameters['quant_consensus'] = True
        # self.parameters['quant_consensus_min_ident'] = 2
        # self.parameters['quant_save_all_annotations'] = True
        # self.parameters['quant_proteins_min_peptides'] = 1
        # self.parameters['quant_proteins_remove_subset_proteins'] = True
        # self.parameters['quant_proteins_ignore_ambiguous_peptides'] = True
        # self.parameters['quant_proteins_quant_type'] = 'razor'
        print(self.parameters)

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
        self.project_directory_ui.setReadOnly(True)
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
        # Project metadata.
        self.project_directory_ui.setText(os.path.dirname(self.project_path))
        if "project_name" in self.parameters_container.parameters:
            self.project_name_ui.setText(self.parameters_container.parameters['project_name'])
        if "project_description" in self.parameters_container.parameters:
            self.project_description_ui.setText(self.parameters_container.parameters['project_description'])
        params = self.parameters_container.parameters

        # Parameters.
        self.parameters_container.update_allowed = False
        self.parameters_container.inst_type.setCurrentText(params['instrument_type'])
        self.parameters_container.res_ms1.setValue(params['resolution_ms1'])
        self.parameters_container.res_ms2.setValue(params['resolution_msn'])
        self.parameters_container.reference_mz.setValue(params['reference_mz'])
        self.parameters_container.avg_fwhm_rt.setValue(params['avg_fwhm_rt'])
        self.parameters_container.num_samples_mz.setValue(params['num_samples_mz'])
        self.parameters_container.num_samples_rt.setValue(params['num_samples_rt'])
        self.parameters_container.smoothing_coefficient_mz.setValue(params['smoothing_coefficient_mz'])
        self.parameters_container.smoothing_coefficient_rt.setValue(params['smoothing_coefficient_rt'])
        self.parameters_container.warp2d_slack.setValue(params['warp2d_slack'])
        self.parameters_container.warp2d_window_size.setValue(params['warp2d_window_size'])
        self.parameters_container.warp2d_num_points.setValue(params['warp2d_num_points'])
        self.parameters_container.warp2d_rt_expand_factor.setValue(params['warp2d_rt_expand_factor'])
        self.parameters_container.warp2d_peaks_per_window.setValue(params['warp2d_peaks_per_window'])
        self.parameters_container.metamatch_fraction.setValue(params['metamatch_fraction'])
        self.parameters_container.metamatch_n_sig_mz.setValue(params['metamatch_n_sig_mz'])
        self.parameters_container.metamatch_n_sig_rt.setValue(params['metamatch_n_sig_rt'])
        # TODO: Rest of parameters
        if params['ident_max_rank_only']:
            self.parameters_container.ident_max_rank_only.setCheckState(Qt.Checked)
        else:
            self.parameters_container.ident_max_rank_only.setCheckState(Qt.Unchecked)
        if params['ident_require_threshold']:
            self.parameters_container.ident_require_threshold.setCheckState(Qt.Checked)
        else:
            self.parameters_container.ident_require_threshold.setCheckState(Qt.Unchecked)
        if params['ident_ignore_decoy']:
            self.parameters_container.ident_ignore_decoy.setCheckState(Qt.Checked)
        else:
            self.parameters_container.ident_ignore_decoy.setCheckState(Qt.Unchecked)

        self.parameters_container.update_allowed = True

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
        # Save changes before running.
        self.save_project()

        # Disable this window so that buttons can't be clicked.
        self.run_btn.setText("Running...")
        self.run_btn.setEnabled(False)
        self.controls_container.setEnabled(False)
        self.project_variables_container.setEnabled(False)
        self.parameters_container.setEnabled(False)

        # Open modal with log progress and cancel button and run pipeline
        # in a different thread/fork.
        pipeline_log_dialog = PipelineLogDialog(
                parent=self,
                params=self.parameters_container.parameters,
                input_files=self.parameters_container.input_files,
                output_dir=os.path.dirname(self.project_path))
        if pipeline_log_dialog.exec():
            print("EXIT SUCCESS")
        else:
            print("EXIT CANCEL")

        # Restore previous button statuses.
        self.run_btn.setText("Run")
        self.run_btn.setEnabled(True)
        self.controls_container.setEnabled(True)
        self.project_variables_container.setEnabled(True)
        self.parameters_container.setEnabled(True)

# Initialize main window.
app = QApplication(sys.argv)
window = MainWindow()
window.show()

# Start the event loop.
app.exec()
