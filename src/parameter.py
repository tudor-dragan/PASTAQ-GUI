import inspect
import os

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QSpinBox, QAbstractSpinBox, QListWidgetItem
from PyQt5.QtWidgets import QWidget, QLineEdit, QDoubleSpinBox, QCheckBox, QStackedWidget, QListWidget
from PyQt5.QtWidgets import QPushButton, QFileDialog, QScrollArea, QComboBox, QLabel
from PyQt5.QtWidgets import QTableWidget, QHeaderView, QHBoxLayout, QGroupBox, QGridLayout


import files
import resources

global saved
saved = True


# Each changeable parameter in the parameters tab with its tooltip.
def init_button_params(label, tooltip):
    button = ParameterLabel(label)
    button.setToolTip(tooltip)

    icon = QIcon(':/icons/question.png')
    button.setLayoutDirection(Qt.RightToLeft)
    button.setIcon(icon)
    button.setFlat(True)

    return button


class ParameterItem(QWidget):
    """
    A container for each parameter for the PASTAQ pipeline.

    Arguments:
    - name of parameter
    - tooltip text
    - type of Qt widget
    """
    def __init__(self, label, tooltip, widget, parent=None):
        QWidget.__init__(self, parent=parent)
        layout = QVBoxLayout(self)

        button = init_button_params(label, tooltip)

        layout.addWidget(button)
        layout.addWidget(widget)


# Do nothing when pressing a label.
class ParameterLabel(QPushButton):
    def mousePressEvent(self, event):
        return


# Function for dealing with adding multiple identification files at once
def multiple_id_files(file, new_file, edit_file_dialog):
    base_name = os.path.basename(file['raw_path'])
    base_name = os.path.splitext(base_name)
    stem = base_name[0]
    for mzid in edit_file_dialog.mzid_paths:
        base_name = os.path.basename(mzid)
        base_name = os.path.splitext(base_name)
        mzid_stem = base_name[0]
        #compares the stem of the ML file to the one of the ID file for matching
        if mzid_stem == stem:
            new_file['ident_path'] = mzid
            break
        os.chdir(os.path.dirname(mzid))  # sets directory to last identification file added


# For when a single .mzID file is added
def single_id_file(path, new_file):
    new_file['ident_path'] = path
    os.chdir(os.path.dirname(path))  # sets directory to last identification file added


def init_check(cell_widget, checkbox):
    lay_out = QHBoxLayout(cell_widget)
    lay_out.addWidget(checkbox)
    lay_out.setAlignment(Qt.AlignCenter)
    lay_out.setContentsMargins(0, 0, 0, 0)
    return lay_out


def init_label(text):
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    return label


def init_button(text, action, tooltip):
    button = QPushButton(text)
    button.clicked.connect(action)
    button.setToolTip(tooltip)
    return button


class ParametersWidget(QTabWidget):
    """
    The main component of the GUI it contains the three tabs corresponding to input files,
    input parameters and paths for the conversion executables
    """
    input_files = []
    parameters = {}
    # creates a file processor for processing .mgf files
    file_processor = files.FileProcessor()

    def __init__(self, parent=None):
        super(ParametersWidget, self).__init__(parent)

        # The tabs that make up the widget
        self.input_files_tab = QWidget()
        self.parameters_tab = QScrollArea()
        self.input_paths_tab = QScrollArea()

        self.addTab(self.input_files_tab, 'Input files')
        self.addTab(self.parameters_tab, 'Parameters')
        self.addTab(self.input_paths_tab, 'Paths')
        self.input_files_tab_ui()
        self.parameters_tab_ui()
        self.input_paths_tab_ui()

    def set_saved(self, bool):
        global saved
        saved = bool
        self.file_processor.set_saved(bool)

    def get_file_processor(self):
        return self.file_processor

    # Table for file input
    def init_files_table(self):
        input_files_table = QTableWidget()
        input_files_table.setEditTriggers(QTableWidget.NoEditTriggers)
        input_files_table.setSelectionBehavior(QTableWidget.SelectRows)
        input_files_table.setRowCount(0)
        input_files_table.setColumnCount(4)
        input_files_table.setFocusPolicy(False)
        column_names = [
            'Raw File (mzXML/mzML)',
            'Identification file (mgf/mzID)',
            'Group',
            'Reference'
        ]
        input_files_table.setHorizontalHeaderLabels(column_names)
        input_files_table.verticalHeader().hide()
        return input_files_table

    def init_header(self):
        header = self.input_files_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

    # Buttons to control the files table
    def init_control(self, add_button, edit_button, remove_button, remove_all_button):
        buttons = QWidget()
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(add_button)
        controls_layout.addWidget(edit_button)
        controls_layout.addWidget(remove_button)
        controls_layout.addWidget(remove_all_button)
        buttons.setLayout(controls_layout)
        return buttons

    def input_files_tab_ui(self):
        self.input_files_table = self.init_files_table()
        self.init_header()

        # buttons
        add_button = init_button('Add', self.add_file, 'Add quantification files (.mzXML or .mzML)')
        edit_button = init_button('Edit', self.edit_file,
                                  'Add identification files to the selected quantification files (.mgf or .mzID)')
        remove_button = init_button('Remove', self.remove_file, 'Remove entire row')
        select_all_button = init_button('Select All', self.select_all_files, 'Select all rows')
        select_all_button.setShortcut('Ctrl+a')

        # control panel
        input_file_buttons = self.init_control(add_button, edit_button, remove_button, select_all_button)

        layout = QVBoxLayout()
        layout.addWidget(input_file_buttons)
        layout.addWidget(self.input_files_table)
        self.input_files_tab.setLayout(layout)

    # Creates the container for the path to MSFragger
    def msfragger_container(self):
        box = QGroupBox('MSFragger .jar file')
        lay_ms = QVBoxLayout()

        description = 'For the automatic file processing, MSFragger needs to be installed.'
        lay_ms.addWidget(QLabel(description))
        url = "<a href=\"https://msfragger.nesvilab.org/\">" \
              "<font color='Tomato'>'More info and docs: MSFragger'</font></a>"
        label = QLabel(url)
        label.setOpenExternalLinks(True)
        lay_ms.addWidget(label)

        hlay = QHBoxLayout()
        self.input_ms = QLineEdit()
        self.input_ms.setText(self.file_processor.ms_jar[1])
        self.input_ms.isReadOnly()
        browse_button_ms = \
            init_button('Browse', lambda: self.file_processor.set_jar_path(self.input_ms), 'Browse for .jar file')
        hlay.addWidget(self.input_ms)
        hlay.addWidget(browse_button_ms)
        lay_ms.addLayout(hlay)
        box.setLayout(lay_ms)
        return box

    # Creates the container for the path to idconvert
    def idconvert_container(self):
        box = QGroupBox('idconvert.exe')
        lay_id = QVBoxLayout()

        description = inspect.cleandoc('''For the automatic file processing,
        ProteoWizard (which containes idconvert) needs to be installed.''')
        lay_id.addWidget(QLabel(description))
        url = "<a href=\"https://proteowizard.sourceforge.io//\">" \
              "<font color='Tomato'>'More info and docs: ProteoWizard'</font></a>"
        label = QLabel(url)
        label.setOpenExternalLinks(True)
        lay_id.addWidget(label)

        hlay = QHBoxLayout()
        self.input_id = QLineEdit()
        self.input_id.setText(self.file_processor.id_file[1])
        self.input_id.isReadOnly()
        browse_button_id = \
            init_button('Browse', lambda: self.file_processor.set_id_path(self.input_id), 'Browse for idconvert.exe')
        hlay.addWidget(self.input_id)
        hlay.addWidget(browse_button_id)
        lay_id.addLayout(hlay)
        box.setLayout(lay_id)
        return box

    # Path to a parameters file for MSFragger
    def params_container(self):
        box = QGroupBox('.params file for MSFragger')
        lay_params = QVBoxLayout()

        description = 'For the automatic file processing, MSFragger requires a .params file to run.'
        lay_params.addWidget(QLabel(description))
        url = "<a href=\"https://msfragger.nesvilab.org/\">" \
              "<font color='Tomato'>'More info and docs: MSFragger parameters'</font></a>"
        label = QLabel(url)
        label.setOpenExternalLinks(True)
        lay_params.addWidget(label)

        hlay = QHBoxLayout()
        self.input_params = QLineEdit()
        self.input_params.setText(self.file_processor.params[1])
        self.input_params.isReadOnly()
        browse_button_params = \
            init_button('Browse', lambda: self.file_processor.set_params_path(self.input_params),
                        'Browse for .params file for MSFragger')
        hlay.addWidget(self.input_params)
        hlay.addWidget(browse_button_params)
        lay_params.addLayout(hlay)
        box.setLayout(lay_params)
        return box

    # Adding the paths input to the UI
    def input_paths_tab_ui(self):
        msfragger_box = self.msfragger_container()
        id_box = self.idconvert_container()
        params_box = self.params_container()

        widget = QWidget()
        self.input_paths_tab.setWidget(widget)
        self.input_paths_tab.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(msfragger_box)
        layout.addWidget(id_box)
        layout.addWidget(params_box)

        widget.setLayout(layout)

    # Adds a file to the GUI
    def add_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Select input files',
            directory=os.getcwd(),
            filter='MS files (*.mzXML *.mzML)',
        )
        self.add_new_file(file_paths)

    def add_new_file(self, file_paths):
        if len(file_paths) > 0:
            os.chdir(os.path.dirname(file_paths[0]))
            input_files = self.input_files
            current_files = [file['raw_path'] for file in self.input_files]
            for file_path in file_paths:
                if file_path not in current_files:
                    input_files.append({'raw_path': file_path, 'reference': False})
            self.update_input_files(input_files)

    # handle the files added to the edit dialog
    def examine_edit_files(self, old_list, edit_file_dialog, indexes):
        new_list = []
        for i, file in enumerate(old_list):
            if i in indexes:
                new_file = file
                new_file['group'] = edit_file_dialog.group
                if len(indexes) == 1 and len(edit_file_dialog.mzid_paths) == 1:
                    single_id_file(edit_file_dialog.mzid_paths[0], new_file)
                else:
                    multiple_id_files(file, new_file, edit_file_dialog)
                new_list += [new_file]
            else:
                new_list += [file]
        return new_list

    # When selecting .mzML files these can be edited to add a .mzID file to them
    # This spawns the edit dialog and adds the files to the GUI
    def edit_file(self):
        indexes = self.find_selected_files()
        if len(indexes) == 0:
            return
        edit_file_dialog = files.EditFileDialog()
        if edit_file_dialog.exec():
            old_list = self.input_files
            new_list = self.examine_edit_files(old_list, edit_file_dialog, indexes)
            self.update_input_files(new_list)

    def get_saved(self):
        return saved == self.file_processor.get_saved()
    def select_all_files(self):
        self.input_files_table.selectAll()

    def remove_file(self):
        indexes = self.find_selected_files()
        if len(indexes) > 0:
            old_list = self.input_files
            new_list = []
            for i, file in enumerate(old_list):
                if i not in indexes:
                    new_list += [file]
            self.update_input_files(new_list)

    # Finds the index of the selected files in the UI
    def find_selected_files(self):
        selected_ranges = self.input_files_table.selectedRanges()
        indexes = []
        for sel in selected_ranges:
            for i in range(sel.topRow(), sel.bottomRow() + 1):
                indexes += [i]
        return indexes

    # Updates the UI in case of a change in the input files
    def update_input_files(self, input_files):
        global saved
        saved = False
        self.input_files = input_files
        self.input_files_table.setRowCount(len(self.input_files))
        for i, input_file in enumerate(self.input_files):
            label = QLabel(input_file['raw_path'])
            self.input_files_table.setCellWidget(i, 0, label)
            if 'ident_path' in input_file:
                self.input_files_table.setCellWidget(i, 1, QLabel(input_file['ident_path']))
            if 'group' in input_file:
                label = init_label(input_file['group'])
                self.input_files_table.setCellWidget(i, 2, label)
            if 'reference' in input_file:
                cell_widget = self.make_reference(input_file['reference'])
                self.input_files_table.setCellWidget(i, 3, cell_widget)

    def load_params(self, path):
        self.file_processor.load_params_path(path)
        self.input_params.setText(path)

    def load_ms_path(self, path):
        if self.file_processor.load_ms_path(path):
            self.input_ms.setText(path)
        else:
            files.popup_window('Error', 'Invalid MSFragger path')


    def load_id_path(self, path):
        if self.file_processor.load_id_path(path):
            self.input_id.setText(path)
        else:
            files.popup_window('Error', 'Invalid idconvert path')

    # Enables the reference checkmark box next to each file pair
    def make_reference(self, reference):
        cell_widget = QWidget()
        checkbox = QCheckBox()
        if reference:
            checkbox.setCheckState(Qt.Checked)
        lay_out = init_check(cell_widget, checkbox)
        cell_widget.setLayout(lay_out)
        checkbox.stateChanged.connect(self.toggle_reference)
        return cell_widget

    def toggle_reference(self):
        for row in range(self.input_files_table.rowCount()):
            checkbox = self.input_files_table.cellWidget(row, 3).children()[1]
            self.input_files[row]['reference'] = checkbox.isChecked()

    # Section of parameters
    # This initialises the UI for each parameter, as well as the values it can take
    def init_inst(self):
        grid_layout_inst = QGridLayout()
        # TODO
        description = 'Description of container'
        grid_layout_inst.addWidget(QLabel(description), 0, 0)

        self.inst_type = QComboBox()
        self.inst_type.addItems(['orbitrap', 'tof', 'ft-icr', 'quadrupole'])
        self.inst_type.currentIndexChanged.connect(self.update_parameters)
        tooltip = 'The type of mass analyser used to acquire the data.'
        grid_layout_inst.addWidget(ParameterItem('Instrument type', tooltip, self.inst_type), 1, 0)

        self.res_ms1 = QSpinBox()
        self.res_ms1.setRange(-LARGE, LARGE)
        self.res_ms1.valueChanged.connect(self.update_parameters)
        tooltip = 'MS1 resolution set on the mass spectrometer at the time of data acquisition.'
        grid_layout_inst.addWidget(ParameterItem('Resolution MS1', tooltip, self.res_ms1), 1, 1)

        self.res_ms2 = QSpinBox()
        self.res_ms2.setRange(-LARGE, LARGE)
        self.res_ms2.valueChanged.connect(self.update_parameters)
        tooltip = 'MS/MS resolution set on the mass spectrometer at the time of data acquisition.'
        grid_layout_inst.addWidget(ParameterItem('Resolution MS2', tooltip, self.res_ms2), 1, 2)

        self.reference_mz = QSpinBox()
        self.reference_mz.setRange(-LARGE, LARGE)
        self.reference_mz.valueChanged.connect(self.update_parameters)
        tooltip = 'Reference m/z at which the resolution is calculated.'
        grid_layout_inst.addWidget(ParameterItem('Reference m/z', tooltip, self.reference_mz), 2, 0)

        self.avg_fwhm_rt = QSpinBox()
        self.avg_fwhm_rt.setRange(-LARGE, LARGE)
        self.avg_fwhm_rt.valueChanged.connect(self.update_parameters)
        tooltip = 'Expected full-width half-maximum width of chromatographic peaks.'
        grid_layout_inst.addWidget(ParameterItem('Avg FWHM RT', tooltip, self.avg_fwhm_rt), 2, 1)

        return grid_layout_inst

    # Section of parameters
    def init_raw_data(self):
        grid_layout_raw_data = QGridLayout()
        # TODO
        description = 'Description of container'
        grid_layout_raw_data.addWidget(QLabel(description), 0, 0)

        self.min_mz = QDoubleSpinBox()
        self.min_mz.setRange(0, LARGE)
        self.min_mz.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.min_mz.valueChanged.connect(self.update_parameters)
        tooltip = 'Filter minimum m/z value for spectra during raw data reading.'
        grid_layout_raw_data.addWidget(ParameterItem('Min m/z', tooltip, self.min_mz), 1, 0)

        self.max_mz = QDoubleSpinBox()
        self.max_mz.setRange(0, LARGE)
        self.max_mz.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.max_mz.valueChanged.connect(self.update_parameters)
        tooltip = 'Filter maximum m/z value for spectra during raw data reading.'
        grid_layout_raw_data.addWidget(ParameterItem('Max m/z', tooltip, self.max_mz), 1, 1)

        self.polarity = QComboBox()
        self.polarity.addItems(['positive', 'negative', 'both'])
        self.polarity.currentIndexChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc('''Filter polarity (Positive '+', negative '-', or any) for spectra during raw data reading.
                          This should only be modified if the raw data file contains both positive and negative polarity spectra.''')
        grid_layout_raw_data.addWidget(ParameterItem('Polarity', tooltip, self.polarity), 1, 2)

        self.min_rt = QDoubleSpinBox()
        self.min_rt.setRange(0, LARGE)
        self.min_rt.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.min_rt.valueChanged.connect(self.update_parameters)
        tooltip = 'Filter minimum retention time value for spectra during raw data reading.'
        grid_layout_raw_data.addWidget(ParameterItem('Min retention time', tooltip, self.min_rt), 2, 0)

        self.max_rt = QDoubleSpinBox()
        self.max_rt.setRange(0, LARGE)
        self.max_rt.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.max_rt.valueChanged.connect(self.update_parameters)
        tooltip = 'Filter maximum retention time value for spectra during raw data reading.'
        grid_layout_raw_data.addWidget(ParameterItem('Max retention time', tooltip, self.max_rt), 2, 1)

        return grid_layout_raw_data

    # Section of parameters
    def init_resamp(self):
        grid_layout_resamp = QGridLayout()
        # TODO
        description = 'Description of container'
        grid_layout_resamp.addWidget(QLabel(description), 0, 0)

        self.num_samples_mz = QSpinBox()
        self.num_samples_mz.setRange(-LARGE, LARGE)
        self.num_samples_mz.valueChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc('''Number of sampling points per full-width half-maximum in m/z.
                          If the memory consumption is too high it can be reduced at
                          the cost of potentially missing peaks or obtaining less accurate fitting.''')
        grid_layout_resamp.addWidget(ParameterItem('Number of samples m/z', tooltip, self.num_samples_mz), 1, 0)

        self.num_samples_rt = QSpinBox()
        self.num_samples_rt.setRange(-LARGE, LARGE)
        self.num_samples_rt.valueChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc('''Number of sampling points per full-width half-maximum in retention time.
                          If the memory consumption is too high it can be reduced at the
                          cost of potentially missing peaks or obtaining less accurate fitting.''')
        grid_layout_resamp.addWidget(ParameterItem('Number of samples rt', tooltip, self.num_samples_rt), 1, 1)

        self.smoothing_coefficient_mz = QDoubleSpinBox()
        self.smoothing_coefficient_mz.setRange(-LARGE, LARGE)
        self.smoothing_coefficient_mz.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.smoothing_coefficient_mz.valueChanged.connect(self.update_parameters)
        tooltip = 'Amount of smoothing applied for resampling in the m/z dimension.'
        grid_layout_resamp.addWidget(
            ParameterItem('Smoothing coefficient (m/z)', tooltip, self.smoothing_coefficient_mz), 1, 2)

        self.smoothing_coefficient_rt = QDoubleSpinBox()
        self.smoothing_coefficient_rt.setRange(-LARGE, LARGE)
        self.smoothing_coefficient_mz.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.smoothing_coefficient_rt.valueChanged.connect(self.update_parameters)
        tooltip = 'Amount of smoothing applied for resampling in the retention time dimension.'
        grid_layout_resamp.addWidget(
            ParameterItem('Smoothing coefficient (rt)', tooltip, self.smoothing_coefficient_rt), 2, 0)

        self.max_peaks = QSpinBox()
        self.max_peaks.setRange(-LARGE, LARGE)
        self.max_peaks.valueChanged.connect(self.update_parameters)
        tooltip = 'Maximum number of peaks per file being detected at isotope level in decreasing intensity order.'
        grid_layout_resamp.addWidget(ParameterItem('Max number of peaks', tooltip, self.max_peaks), 3, 0)

        self.feature_detection_charge_state_min = QSpinBox()
        self.feature_detection_charge_state_min.setRange(1, LARGE)
        self.feature_detection_charge_state_min.valueChanged.connect(self.update_parameters)
        tooltip = 'Feature detection charge state min.'
        grid_layout_resamp.addWidget(
            ParameterItem('Feature detection min charge', tooltip, self.feature_detection_charge_state_min), 2, 1)

        self.feature_detection_charge_state_max = QSpinBox()
        self.feature_detection_charge_state_max.setRange(1, LARGE)
        self.feature_detection_charge_state_max.valueChanged.connect(self.update_parameters)
        tooltip = 'Feature detection charge state max.'
        grid_layout_resamp.addWidget(
            ParameterItem('Feature detection max charge', tooltip, self.feature_detection_charge_state_max), 2, 2)

        return grid_layout_resamp

    # Section of parameters
    def init_warp(self):
        grid_layout_warp = QGridLayout()
        # TODO
        description = 'Description of container'
        grid_layout_warp.addWidget(QLabel(description), 0, 0)

        self.warp2d_slack = QSpinBox()
        self.warp2d_slack.setRange(-LARGE, LARGE)
        self.warp2d_slack.valueChanged.connect(self.update_parameters)
        tooltip = 'Number of points allowed to move for each anchor node during retention time alignment.'
        grid_layout_warp.addWidget(ParameterItem('Slack', tooltip, self.warp2d_slack), 1, 0)

        self.warp2d_window_size = QSpinBox()
        self.warp2d_window_size.setRange(-LARGE, LARGE)
        self.warp2d_window_size.valueChanged.connect(self.update_parameters)
        tooltip = 'Number of points between anchor points.'
        grid_layout_warp.addWidget(ParameterItem('Window Size', tooltip, self.warp2d_window_size), 1, 1)

        self.warp2d_num_points = QSpinBox()
        self.warp2d_num_points.setRange(-LARGE, LARGE)
        self.warp2d_num_points.valueChanged.connect(self.update_parameters)
        tooltip = 'Number of points in which the minimum and maximum retention time range will be discretized.'
        grid_layout_warp.addWidget(ParameterItem('Number of points', tooltip, self.warp2d_num_points), 1, 2)

        self.warp2d_rt_expand_factor = QDoubleSpinBox()
        self.warp2d_rt_expand_factor.setRange(-LARGE, LARGE)
        self.warp2d_rt_expand_factor.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.warp2d_rt_expand_factor.valueChanged.connect(self.update_parameters)
        tooltip = 'Expansion of the retention time range to avoid edge effects at the min/max nodes.'
        grid_layout_warp.addWidget(ParameterItem('Expand factor rt', tooltip, self.warp2d_rt_expand_factor), 2, 0)
        self.warp_box.setLayout(grid_layout_warp)

        self.warp2d_peaks_per_window = QSpinBox()
        self.warp2d_peaks_per_window.setRange(-LARGE, LARGE)
        self.warp2d_peaks_per_window.valueChanged.connect(self.update_parameters)
        tooltip = 'Number of peaks used for similarity calculation in each alignment window.'
        grid_layout_warp.addWidget(ParameterItem('Peaks per window', tooltip, self.warp2d_peaks_per_window), 2, 1)

        return grid_layout_warp

    # Section of parameters
    def init_meta(self):
        grid_layout_meta = QGridLayout()
        # TODO
        description = 'Description of container'
        grid_layout_meta.addWidget(QLabel(description), 0, 0)

        self.metamatch_fraction = QDoubleSpinBox()
        self.metamatch_fraction.setRange(-LARGE, LARGE)
        self.metamatch_fraction.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.metamatch_fraction.valueChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc('''Minimum percentage of peak presence (value between 0 and 1) in at least
                one sample group to be included in Metamatch result.
                For example, if there are 10 samples in group A and 10 in group B,
                for a fraction value of 0.7, we consider a valid cluster if there are 
                matched peaks present in at least 7 samples in at least one of the sample group.''')
        grid_layout_meta.addWidget(ParameterItem('Fraction of samples', tooltip, self.metamatch_fraction), 1, 0)

        self.metamatch_n_sig_mz = QDoubleSpinBox()
        self.metamatch_n_sig_mz.setRange(-LARGE, LARGE)
        self.metamatch_n_sig_mz.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.metamatch_n_sig_mz.valueChanged.connect(self.update_parameters)
        tooltip = 'Number of standard deviations to use as tolerance for m/z radius.'
        grid_layout_meta.addWidget(ParameterItem('Number of sigma (m/z)', tooltip, self.metamatch_n_sig_mz), 1, 1)

        self.metamatch_n_sig_rt = QDoubleSpinBox()
        self.metamatch_n_sig_rt.setRange(-LARGE, LARGE)
        self.metamatch_n_sig_rt.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.metamatch_n_sig_rt.valueChanged.connect(self.update_parameters)
        tooltip = 'Number of standard deviations to use as tolerance for retention time radius.'
        grid_layout_meta.addWidget(ParameterItem('Number of sigma (rt)', tooltip, self.metamatch_n_sig_rt), 1, 2)

        return grid_layout_meta

    # Section of parameters
    def init_ident(self):
        grid_layout_ident = QGridLayout()
        # TODO
        description = 'Description of container'
        grid_layout_ident.addWidget(QLabel(description), 0, 0)
        self.ident_max_rank_only = QCheckBox()
        self.ident_max_rank_only.stateChanged.connect(self.update_parameters)
        tooltip = 'Only select the most confident PSM from each MS/MS spectra.'
        grid_layout_ident.addWidget(ParameterItem('Max rank only', tooltip, self.ident_max_rank_only), 1, 0)

        self.ident_require_threshold = QCheckBox()
        self.ident_require_threshold.stateChanged.connect(self.update_parameters)
        tooltip = 'Read only identifications that meet the target-decoy false discovery rate threshold.'
        grid_layout_ident.addWidget(ParameterItem('Require threshold', tooltip, self.ident_require_threshold), 1, 1)

        self.ident_ignore_decoy = QCheckBox()
        self.ident_ignore_decoy.stateChanged.connect(self.update_parameters)
        tooltip = 'Ignore PSM that have been detected as decoys by the identification engine.'
        grid_layout_ident.addWidget(ParameterItem('Ignore decoy', tooltip, self.ident_ignore_decoy), 1, 2)

        self.link_n_sig_mz = QDoubleSpinBox()
        self.link_n_sig_mz.setRange(-LARGE, LARGE)
        self.link_n_sig_mz.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.link_n_sig_mz.valueChanged.connect(self.update_parameters)
        tooltip = 'Tolerance for ms2 events and identification linking measured in number of standard deviations for (m/z)'
        grid_layout_ident.addWidget(ParameterItem('Max number of sigma for linking (m/z)', tooltip, self.link_n_sig_mz),
                                    2, 0)
        self.link_n_sig_rt = QDoubleSpinBox()
        self.link_n_sig_rt.setRange(-LARGE, LARGE)
        self.link_n_sig_rt.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.link_n_sig_rt.valueChanged.connect(self.update_parameters)
        tooltip = 'Tolerance for ms2 events and identification linking measured in number of standard deviations for (rt)'
        grid_layout_ident.addWidget(ParameterItem('Max number of sigma for linking (rt)', tooltip, self.link_n_sig_rt),
                                    2, 1)
        return grid_layout_ident

    # Section of parameters
    def init_qual(self):
        grid_layout_qual = QGridLayout()
        # TODO
        description = 'Description of container'
        grid_layout_qual.addWidget(QLabel(description), 0, 0)

        self.similarity_num_peaks = QSpinBox()
        self.similarity_num_peaks.setRange(-LARGE, LARGE)
        self.similarity_num_peaks.valueChanged.connect(self.update_parameters)
        tooltip = 'Number of peaks used for the similarity matrix calculation.'
        grid_layout_qual.addWidget(ParameterItem('Similarity number of peaks', tooltip, self.similarity_num_peaks), 1,
                                   0)

        self.qc_plot_palette = QComboBox()
        self.qc_plot_palette.addItems(['husl', 'crest', 'Spectral', 'flare', 'mako'])
        self.qc_plot_palette.currentIndexChanged.connect(self.update_parameters)
        tooltip = 'Plot color palette.'
        grid_layout_qual.addWidget(ParameterItem('Plot color palette', tooltip, self.qc_plot_palette), 1, 1)

        self.qc_plot_extension = QComboBox()
        self.qc_plot_extension.addItems(['png', 'pdf', 'eps'])
        self.qc_plot_extension.currentIndexChanged.connect(self.update_parameters)
        tooltip = 'Plot image format'
        grid_layout_qual.addWidget(ParameterItem('Plot image format', tooltip, self.qc_plot_extension), 1, 2)

        # This could be either text 'dynamic' or a double between 0.0-1.0. If
        # set to 0.0 it will be considered dynamic.
        self.qc_plot_fill_alpha = QDoubleSpinBox()
        self.qc_plot_fill_alpha.setRange(0.0, 1.0)
        self.qc_plot_fill_alpha.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.qc_plot_fill_alpha.valueChanged.connect(self.update_parameters)
        tooltip = 'Transparency amount for fill plots.'
        grid_layout_qual.addWidget(ParameterItem('Fill alpha', tooltip, self.qc_plot_fill_alpha), 2, 0)

        self.qc_plot_line_style = QComboBox()
        self.qc_plot_line_style.addItems(['fill', 'line'])
        self.qc_plot_line_style.currentIndexChanged.connect(self.update_parameters)
        tooltip = 'For line plots select if pure lines or fill plots should be used.'
        grid_layout_qual.addWidget(ParameterItem('Line style', tooltip, self.qc_plot_line_style), 2, 1)

        self.qc_plot_font_family = QComboBox()
        self.qc_plot_font_family.addItems(['sans-serif', 'serif'])
        self.qc_plot_font_family.currentIndexChanged.connect(self.update_parameters)
        tooltip = 'Font family.'
        grid_layout_qual.addWidget(ParameterItem('Font family', tooltip, self.qc_plot_font_family), 2, 2)

        self.qc_plot_dpi = QSpinBox()
        self.qc_plot_dpi.setRange(1, 1000)
        self.qc_plot_dpi.valueChanged.connect(self.update_parameters)
        tooltip = 'Plot dpi.'
        grid_layout_qual.addWidget(ParameterItem('Plot dpi', tooltip, self.qc_plot_dpi), 3, 0)

        self.qc_plot_mz_vs_sigma_mz_max_peaks = QSpinBox()
        self.qc_plot_mz_vs_sigma_mz_max_peaks.setRange(10, LARGE)
        self.qc_plot_mz_vs_sigma_mz_max_peaks.valueChanged.connect(self.update_parameters)
        tooltip = 'How many peaks should be plotted for the m/z vs m/z width QC plot.'
        grid_layout_qual.addWidget(
            ParameterItem('Max peaks for m/z vs peak width m/z', tooltip, self.qc_plot_mz_vs_sigma_mz_max_peaks), 3, 1)

        self.qc_plot_line_alpha = QDoubleSpinBox()
        self.qc_plot_line_alpha.setRange(0.0, 1.0)
        self.qc_plot_line_alpha.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.qc_plot_line_alpha.valueChanged.connect(self.update_parameters)
        tooltip = 'Transparency amount for line plots.'
        grid_layout_qual.addWidget(ParameterItem('Line alpha', tooltip, self.qc_plot_line_alpha), 3, 2)

        self.qc_plot_scatter_alpha = QDoubleSpinBox()
        self.qc_plot_scatter_alpha.setRange(0.0, 1.0)
        self.qc_plot_scatter_alpha.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.qc_plot_scatter_alpha.valueChanged.connect(self.update_parameters)
        tooltip = 'Transparency amount for scatter plots.'
        grid_layout_qual.addWidget(ParameterItem('Scatter alpha', tooltip, self.qc_plot_scatter_alpha), 4, 0)

        self.qc_plot_scatter_size = QDoubleSpinBox()
        self.qc_plot_scatter_size.setRange(0.1, 10.0)
        self.qc_plot_scatter_size.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.qc_plot_scatter_size.valueChanged.connect(self.update_parameters)
        tooltip = 'Size of scatter points in QC plots.'
        grid_layout_qual.addWidget(ParameterItem('Scatter size', tooltip, self.qc_plot_scatter_size), 4, 1)

        self.qc_plot_min_dynamic_alpha = QDoubleSpinBox()
        self.qc_plot_min_dynamic_alpha.setRange(0.1, 10.0)
        self.qc_plot_min_dynamic_alpha.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.qc_plot_min_dynamic_alpha.valueChanged.connect(self.update_parameters)
        tooltip = 'When using dynamic transparency, select a minimum alpha level to avoid too faint plots when many samples are present.'
        grid_layout_qual.addWidget(ParameterItem('Min dynamic alpha', tooltip, self.qc_plot_min_dynamic_alpha), 4, 2)

        self.qc_plot_font_size = QDoubleSpinBox()
        self.qc_plot_font_size.setRange(1.0, 15.0)
        self.qc_plot_font_size.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.qc_plot_font_size.valueChanged.connect(self.update_parameters)
        tooltip = 'Font size.'
        grid_layout_qual.addWidget(ParameterItem('Font size', tooltip, self.qc_plot_font_size), 5, 0)

        self.qc_plot_fig_size_x = QDoubleSpinBox()
        self.qc_plot_fig_size_x.setRange(1.0, 15.0)
        self.qc_plot_fig_size_x.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.qc_plot_fig_size_x.valueChanged.connect(self.update_parameters)
        tooltip = 'Figure size X.'
        grid_layout_qual.addWidget(ParameterItem('Figure size X', tooltip, self.qc_plot_fig_size_x), 5, 1)

        self.qc_plot_fig_size_y = QDoubleSpinBox()
        self.qc_plot_fig_size_y.setRange(1.0, 15.0)
        self.qc_plot_fig_size_y.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        self.qc_plot_fig_size_y.valueChanged.connect(self.update_parameters)
        tooltip = 'Figure size Y.'
        grid_layout_qual.addWidget(ParameterItem('Figure size Y', tooltip, self.qc_plot_fig_size_y), 5, 2)

        self.qc_plot_per_file = QCheckBox()
        self.qc_plot_per_file.stateChanged.connect(self.update_parameters)
        tooltip = 'Whether to plot QC plots for individual files or combine them into a common figure.'
        grid_layout_qual.addWidget(ParameterItem('Plot per file', tooltip, self.qc_plot_per_file), 6, 0)

        self.qc_plot_fig_legend = QCheckBox()
        self.qc_plot_fig_legend.stateChanged.connect(self.update_parameters)
        tooltip = 'Whether to show the legend in QC plots.'
        grid_layout_qual.addWidget(ParameterItem('Figure legend', tooltip, self.qc_plot_fig_legend), 6, 1)

        return grid_layout_qual

    # Section of parameters
    def init_quantt(self):
        grid_layout_quantt = QGridLayout()
        # TODO
        description = 'Description of container'
        grid_layout_quantt.addWidget(QLabel(description), 0, 0)

        self.quant_isotopes = QComboBox()
        self.quant_isotopes.addItems(['height', 'volume'])
        self.quant_isotopes.currentIndexChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc(''' Isotope quantification method for the quantitative table generation.
                          \'Height\': Fitted isotope peak height,
                          \'Volume\': Volume of the 3D isotope peak.''')
        grid_layout_quantt.addWidget(ParameterItem('Isotopes', tooltip, self.quant_isotopes), 1, 0)

        self.quant_features = QComboBox()
        self.quant_features.addItems(
            ['monoisotopic_height', 'monoisotopic_volume', 'total_height', 'total_volume', 'max_height', 'max_volume'])
        self.quant_features.currentIndexChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc('''Feature quantification method for the quantitative table generation.
                          \'Max Height/Volume\': Height or volume of the highest intensity isotope,
                          \'Monoisotopic Height/Volume\': Height or volume of the monoisotopic peak,
                          \'Total Height/Volume\': Sum of heights or volumes of all isotopic peaks in the feature.''')
        grid_layout_quantt.addWidget(ParameterItem('Features', tooltip, self.quant_features), 1, 1)

        self.quant_features_charge_state_filter = QCheckBox()
        self.quant_features_charge_state_filter.stateChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc(''''Whether to remove feature annotations from quantitative tables 
                where charge state of the detected features don't mach the one given by the identification engine.''')
        grid_layout_quantt.addWidget(
            ParameterItem('Features charge state filter', tooltip, self.quant_features_charge_state_filter), 1, 2)

        self.quant_ident_linkage = QComboBox()
        self.quant_ident_linkage.addItems(['theoretical_mz', 'msms_event'])
        self.quant_ident_linkage.currentIndexChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc('''Method linking PSM with quantified isotopes.
                          \'Theoretical m/z\': Link identifiations based on the theoretical monoisotopic m/z calculated by the identification engine,
                          \'MS/MS event\': Link identifications to the closest isotope in m/z and retention time from the occurance of the MS/MS event.''')
        grid_layout_quantt.addWidget(ParameterItem('Ident linkage', tooltip, self.quant_ident_linkage), 2, 0)

        self.quant_consensus = QCheckBox()
        self.quant_consensus.stateChanged.connect(self.update_parameters)
        tooltip = 'When selected, a sequence consensus is generated for the quantitative table.'
        grid_layout_quantt.addWidget(ParameterItem('Consensus', tooltip, self.quant_consensus), 2, 1)

        self.quant_consensus_min_ident = QSpinBox()
        self.quant_consensus_min_ident.setRange(-LARGE, LARGE)
        self.quant_consensus_min_ident.valueChanged.connect(self.update_parameters)
        tooltip = 'Minimum number of samples with the same identification required for consensus sequence generation.'
        grid_layout_quantt.addWidget(ParameterItem('Consensus min ident', tooltip, self.quant_consensus_min_ident), 2,
                                     2)

        self.quant_save_all_annotations = QCheckBox()
        self.quant_save_all_annotations.stateChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc('''Whether all annotations should be saved in addition with the aggregated tables.
                          Depending on the number of annotations, this might dramatically increase the disk space required.''')
        grid_layout_quantt.addWidget(ParameterItem('Save all annotations', tooltip, self.quant_save_all_annotations), 3,
                                     0)

        self.quant_proteins_min_peptides = QSpinBox()
        self.quant_proteins_min_peptides.setRange(1, 50)
        self.quant_proteins_min_peptides.valueChanged.connect(self.update_parameters)
        tooltip = 'Minimum number of peptides needed for considering a protein for quantification.'
        grid_layout_quantt.addWidget(ParameterItem('Consensus min peptide', tooltip, self.quant_proteins_min_peptides),
                                     3, 1)

        self.quant_proteins_remove_subset_proteins = QCheckBox()
        self.quant_proteins_remove_subset_proteins.stateChanged.connect(self.update_parameters)
        tooltip = 'Whether to remove proteins whose peptides are entirely contained within another group with longer number of evidence peptides when performing protein inference.'
        grid_layout_quantt.addWidget(
            ParameterItem('Remove subset proteins', tooltip, self.quant_proteins_remove_subset_proteins), 3, 2)

        self.quant_proteins_ignore_ambiguous_peptides = QCheckBox()
        self.quant_proteins_ignore_ambiguous_peptides.stateChanged.connect(self.update_parameters)
        tooltip = 'When performing protein inference, select if peptides with ambiguous protein identifications should be ignored.'
        grid_layout_quantt.addWidget(
            ParameterItem('Ignore ambiguous peptides', tooltip, self.quant_proteins_ignore_ambiguous_peptides), 4, 0)

        self.quant_proteins_quant_type = QComboBox()
        self.quant_proteins_quant_type.addItems(['razor', 'unique', 'all'])
        self.quant_proteins_quant_type.currentIndexChanged.connect(self.update_parameters)
        tooltip = inspect.cleandoc(''' Type of quantification used for protein inference:
                    - unique: only unique peptides will be used for quantification.
                    - razor: same as unique plus peptides assigned as most likely due to Occam's razor constrain.
                    - all: All peptides will be used for quantification. Shared peptides can be used more than once.''')
        grid_layout_quantt.addWidget(
            ParameterItem('Protein quantification type', tooltip, self.quant_proteins_quant_type), 4, 1)

        return grid_layout_quantt

    # navigation to switch between parameter categories
    def init_nav(self):
        self.nav = QListWidget()
        self.nav.insertItem(0, 'Instrument Settings')
        self.nav.insertItem(1, 'Raw Data')
        self.nav.insertItem(2, 'Quantification')
        self.nav.insertItem(3, 'Warp2D')
        self.nav.insertItem(4, 'MetaMatch')
        self.nav.insertItem(5, 'Identification')
        self.nav.insertItem(6, 'Quantitive Table Generation')
        self.nav.insertItem(7, 'Quality Control')
        for i in range(8):
            item = self.nav.item(i)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)

        self.nav.currentRowChanged.connect(self.display)
        self.nav.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav.setAlternatingRowColors(True)
        self.nav.setMinimumWidth(175)
        self.nav.setMaximumWidth(300)

    # determines what parameter category is shown
    def display(self, i):
        self.stack.setCurrentIndex(i)

    # Creates stack of parameter categories
    def init_stack(self):
        self.stack = QStackedWidget()
        self.stack.addWidget(self.inst_settings_box)
        self.stack.addWidget(self.raw_data_box)
        self.stack.addWidget(self.quantification_box)
        self.stack.addWidget(self.warp_box)
        self.stack.addWidget(self.meta_box)
        self.stack.addWidget(self.ident_box)
        self.stack.addWidget(self.quantt_box)
        self.stack.addWidget(self.qual_box)

    # Puts navigation and stack together
    def init_layout(self):
        layout = QGridLayout()
        self.init_nav()
        layout.addWidget(self.nav, 0, 0)
        self.init_stack()
        layout.addWidget(self.stack, 0, 1)
        return layout

    # Creates the UI for the parameters tab
    def parameters_tab_ui(self):
        global LARGE
        LARGE = 1000000000

        self.update_allowed = False

        # Instruments
        self.inst_settings_box = QGroupBox('Instrument Settings')
        grid_layout_inst = self.init_inst()
        self.inst_settings_box.setLayout(grid_layout_inst)

        # Raw data
        self.raw_data_box = QGroupBox('Raw Data')
        grid_layout_raw_data = self.init_raw_data()
        self.raw_data_box.setLayout(grid_layout_raw_data)

        # Quantification
        self.quantification_box = QGroupBox('Quantification')
        grid_layout_resamp = self.init_resamp()
        self.quantification_box.setLayout(grid_layout_resamp)

        # Warp2D
        self.warp_box = QGroupBox('Warp2D')
        grid_layout_warp = self.init_warp()
        self.warp_box.setLayout(grid_layout_warp)

        # MetaMatch
        self.meta_box = QGroupBox('MetaMatch')
        grid_layout_meta = self.init_meta()
        self.meta_box.setLayout(grid_layout_meta)

        # Identification
        self.ident_box = QGroupBox('Identification')
        grid_layout_ident = self.init_ident()
        self.ident_box.setLayout(grid_layout_ident)

        # Quality Control
        self.qual_box = QGroupBox('Quality Control')
        grid_layout_qual = self.init_qual()

        self.qual_box.setLayout(grid_layout_qual)

        # Quantitive Table Generation
        self.quantt_box = QGroupBox('Quantitive Table Generation')
        grid_layout_quantt = self.init_quantt()
        self.quantt_box.setLayout(grid_layout_quantt)

        # Enable scrolling
        content_widget = QWidget()
        self.parameters_tab.setWidget(content_widget)
        self.parameters_tab.setWidgetResizable(True)

        content_widget.setLayout(self.init_layout())
        self.update_allowed = True

    # Updates parameters to values set in the UI by the user for the instrument section
    def update_inst(self):
        self.parameters['instrument_type'] = self.inst_type.currentText().lower()
        self.parameters['resolution_ms1'] = self.res_ms1.value()
        self.parameters['resolution_msn'] = self.res_ms2.value()
        self.parameters['reference_mz'] = self.reference_mz.value()
        self.parameters['avg_fwhm_rt'] = self.avg_fwhm_rt.value()

    def update_raw_data(self):
        self.parameters['min_mz'] = self.min_mz.value()
        self.parameters['max_mz'] = self.max_mz.value()
        self.parameters['min_rt'] = self.min_rt.value()
        self.parameters['max_rt'] = self.max_rt.value()
        self.parameters['polarity'] = self.polarity.currentText()

    def update_resamp(self):
        self.parameters['num_samples_mz'] = self.num_samples_mz.value()
        self.parameters['num_samples_rt'] = self.num_samples_rt.value()
        self.parameters['smoothing_coefficient_mz'] = self.smoothing_coefficient_mz.value()
        self.parameters['smoothing_coefficient_rt'] = self.smoothing_coefficient_rt.value()
        self.parameters['max_peaks'] = self.max_peaks.value()
        charge_state_list = list(
            range(self.feature_detection_charge_state_min.value(), self.feature_detection_charge_state_max.value() + 1))
        charge_state_list.reverse()
        self.parameters['feature_detection_charge_states'] = charge_state_list

    def update_warp(self):
        self.parameters['warp2d_slack'] = self.warp2d_slack.value()
        self.parameters['warp2d_window_size'] = self.warp2d_window_size.value()
        self.parameters['warp2d_num_points'] = self.warp2d_num_points.value()
        self.parameters['warp2d_rt_expand_factor'] = self.warp2d_rt_expand_factor.value()
        self.parameters['warp2d_peaks_per_window'] = self.warp2d_peaks_per_window.value()

    def update_meta(self):
        self.parameters['metamatch_fraction'] = self.metamatch_fraction.value()
        self.parameters['metamatch_n_sig_mz'] = self.metamatch_n_sig_mz.value()
        self.parameters['metamatch_n_sig_rt'] = self.metamatch_n_sig_rt.value()

    def update_ident(self):
        self.parameters['ident_max_rank_only'] = self.ident_max_rank_only.isChecked()
        self.parameters['ident_require_threshold'] = self.ident_require_threshold.isChecked()
        self.parameters['ident_ignore_decoy'] = self.ident_ignore_decoy.isChecked()
        self.parameters['link_n_sig_mz'] = self.link_n_sig_mz.value()
        self.parameters['link_n_sig_rt'] = self.link_n_sig_rt.value()
        self.parameters['similarity_num_peaks'] = self.similarity_num_peaks.value()

    def update_qual(self):
        self.parameters['qc_plot_palette'] = self.qc_plot_palette.currentText()
        self.parameters['qc_plot_extension'] = self.qc_plot_extension.currentText()
        if self.qc_plot_fill_alpha.value() == 0.0:
            self.parameters['qc_plot_fill_alpha'] = 'dynamic'
        else:
            self.parameters['qc_plot_fill_alpha'] = self.qc_plot_fill_alpha.value()
        self.parameters['qc_plot_line_alpha'] = self.qc_plot_line_alpha.value()
        self.parameters['qc_plot_scatter_alpha'] = self.qc_plot_scatter_alpha.value()
        self.parameters['qc_plot_scatter_size'] = self.qc_plot_scatter_size.value()
        self.parameters['qc_plot_min_dynamic_alpha'] = self.qc_plot_min_dynamic_alpha.value()
        self.parameters['qc_plot_per_file'] = self.qc_plot_per_file.isChecked()
        self.parameters['qc_plot_line_style'] = self.qc_plot_line_style.currentText()
        self.parameters['qc_plot_dpi'] = self.qc_plot_dpi.value()
        self.parameters['qc_plot_font_family'] = self.qc_plot_font_family.currentText()
        self.parameters['qc_plot_font_size'] = self.qc_plot_font_size.value()
        self.parameters['qc_plot_fig_size_x'] = self.qc_plot_fig_size_x.value()
        self.parameters['qc_plot_fig_size_y'] = self.qc_plot_fig_size_y.value()
        self.parameters['qc_plot_fig_legend'] = self.qc_plot_fig_legend.isChecked()
        self.parameters['qc_plot_mz_vs_sigma_mz_max_peaks'] = self.qc_plot_mz_vs_sigma_mz_max_peaks.value()

    def update_quantt(self):
        self.parameters['quant_isotopes'] = self.quant_isotopes.currentText()
        self.parameters['quant_features'] = self.quant_features.currentText()
        self.parameters['quant_features_charge_state_filter'] = self.quant_features_charge_state_filter.isChecked()
        self.parameters['quant_ident_linkage'] = self.quant_ident_linkage.currentText()
        self.parameters['quant_consensus'] = self.quant_consensus.isChecked()
        self.parameters['quant_consensus_min_ident'] = self.quant_consensus_min_ident.value()
        self.parameters['quant_save_all_annotations'] = self.quant_save_all_annotations.isChecked()
        self.parameters['quant_proteins_min_peptides'] = self.quant_proteins_min_peptides.value()
        self.parameters[
            'quant_proteins_remove_subset_proteins'] = self.quant_proteins_remove_subset_proteins.isChecked()
        self.parameters[
            'quant_proteins_ignore_ambiguous_peptides'] = self.quant_proteins_ignore_ambiguous_peptides.isChecked()
        self.parameters['quant_proteins_quant_type'] = self.quant_proteins_quant_type.currentText()

    # Updates all the parameters
    def update_parameters(self):
        if not self.update_allowed:
            return

        global saved
        saved = False

        self.update_inst()
        self.update_raw_data()
        self.update_resamp()
        self.update_warp()
        self.update_meta()
        self.update_ident()
        self.update_qual()
        self.update_quantt()
