import json
import os
import platform
import sys
import time
import resources
import params
import platform


from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QKeySequence, QPalette, QColor
from PyQt5.QtWidgets import *

import pastaq


# TODO: Create custom file picker widget that shows the name of the picked files
# TODO: Switch the cwd to the project directory and/or use it instead of os.getcwd()
# TODO: The RUN button should only be access when there is at least 1 sample active.

# Window when you edit row(s)
class EditFileDialog(QDialog):
    group = ''
    mzid_paths = []

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('PASTAQ: DDA Pipeline - Add files')

        # Edit parameters.
        form_container = QWidget()
        form_layout = QFormLayout()
        self.group_box = QLineEdit()
        self.group_box.textChanged.connect(self.set_group)
        mzid_picker = QPushButton('Browse')
        mzid_picker.clicked.connect(self.set_mzid_paths)
        #start of drag and drop
        drop = ImageLabel()
        self.setAcceptDrops(True)

        form_layout.addRow('Group', self.group_box)
        form_layout.addRow('mgf/mzID', mzid_picker)
        form_layout.addRow(drop)

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    # TODO somehow do the same as edit_file(self) function (preferably no duplicate code so combine if possible)
    # only allow specific file types
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        drop = []
        for file in files:
            if file.endswith(".mzID'") or file.endswith(".mzIdentML'") or file.endswith(".mgf'"):
                drop.append(file)
        if len(drop) > 0:
            self.mzid_paths = drop

        #
        #for f in files:
            #print(f)

    def set_group(self):
        self.group = self.group_box.text()

    def set_mzid_paths(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Select input files',
            directory=os.getcwd(),
            # two extension possibilities
            filter='Identification files (*.mzID *.mzIdentML *.mgf)'
        )
        if len(file_paths) > 0:
            self.mzid_paths = file_paths

# class for drag and drop field
class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Drop File(s) Here \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')

    def setPixmap(self, image):
        super().setPixmap(image)


class ParameterItem(QWidget):
    def __init__(self, label, tooltip, widget, parent=None):
        QWidget.__init__(self, parent=parent)
        layout = QVBoxLayout(self)

        button = ParameterLabel(label)
        button.setToolTip(tooltip)

        icon = QIcon(':/icons/question.png')
        button.setLayoutDirection(Qt.RightToLeft)
        button.setIcon(icon)
        button.setFlat(True)


        layout.addWidget(button)
        layout.addWidget(widget)


class ParameterLabel(QPushButton):
    def mousePressEvent(self, event):
        return


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
        print('Starting DDA Pipeline')
        time.sleep(1)

        try:
            pastaq.dda_pipeline(self.params, self.input_files, self.output_dir)
        except Exception as e:
            print('ERROR:', e)

        self.finished.emit()


class PipelineLogDialog(QDialog):
    group = ''
    mzid_paths = []

    def __init__(self, params, input_files, output_dir, parent=None):
        super().__init__(parent)

        # TODO: Set fixed size for this.
        self.setWindowTitle('PASTAQ: DDA Pipeline (Running)')

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
        self.buttons.clear()
        self.layout.replaceWidget(self.buttons, new_buttons)
        self.buttons = new_buttons

    def exit_failure(self):
        # TODO: Confirm we want to exit, since this could lead to corrupt
        # temporary files.

        # Restore stdout pipe.
        sys.stdout = sys.__stdout__
        # this does not quit the thread it keeps running in the background
        self.pipeline_thread.quit()
        # self.pipeline_thread.terminate() can be used in place of quit and it will end the thread
        # but not free the memory allocated in the C++ part of the code
        self.reject()

pop = False
class MainWindow(QMainWindow):
    project_path = ''
    dark = False
   
    def __init__(self):
        super().__init__()

        self.setWindowTitle('PASTAQ: DDA Pipeline')

        # Tabbed input files/parameters
        self.parameters_container = params.ParametersWidget()
        
        # Main layout
        layout = QVBoxLayout()

        #Menu Bar
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('File')
        self.actionMenu = self.menubar.addMenu('Action')
                
        #New Project 
        self.newProj = QAction('New Project', self)
        self.newProj.triggered.connect(self.new_project)
        self.fileMenu.addAction(self.newProj)

        #Open Project 
        self.openProj = QAction('Open Project', self)
        self.openProj.triggered.connect(self.open_project)
        self.openProj.setShortcut(QKeySequence('Ctrl+o'))
        self.fileMenu.addAction(self.openProj)

        #Save Project
        self.save_project_btn = QAction('Save', self)
        self.save_project_btn.triggered.connect(self.save_project)
        self.save_project_btn.setShortcut(QKeySequence('Ctrl+s'))
        self.save_project_btn.setEnabled(False)
        self.fileMenu.addAction(self.save_project_btn)

        #Save Project As
        self.save_project_as_btn = QAction('Save as', self)
        self.save_project_as_btn.triggered.connect(self.save_project_as)
        self.save_project_as_btn.setEnabled(False)
        self.fileMenu.addAction(self.save_project_as_btn)

        #remove file menu button
        self.remove_file_btn = QAction('Remove Selected Files', self)
        self.remove_file_btn.triggered.connect(self.parameters_container.remove_file)
        self.remove_file_btn.setShortcut(QKeySequence('Ctrl+d'))
        self.remove_file_btn.setEnabled(False)
        self.actionMenu.addAction(self.remove_file_btn)

        #reset button
        self.reset_param_btn = QAction('Reset Parameters', self)
        self.reset_param_btn.triggered.connect(self.reset_param)
        self.reset_param_btn.setEnabled(False)
        self.actionMenu.addAction(self.reset_param_btn)
        
        #dark/light mode button
        self.view_mode_btn = QAction('Dark Mode', self)
        self.view_mode_btn.triggered.connect(self.view_mode)
        self.reset_param_btn.setEnabled(True)
        self.actionMenu.addAction(self.view_mode_btn)

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
        project_variables_layout.addRow('Project name', self.project_name_ui)
        project_variables_layout.addRow('Project description', self.project_description_ui)
        project_variables_layout.addRow('Project directory', self.project_directory_ui)
        self.project_directory_ui.setReadOnly(True)
        self.project_variables_container.setLayout(project_variables_layout)
        layout.addWidget(self.project_variables_container)

        # Applying layout to Tabbed input files/parameters
        layout.addWidget(self.parameters_container)

        #
        # Run button
        #
        self.run_btn = QPushButton('Run')
        self.run_btn.clicked.connect(self.run_pipeline)
        layout.addWidget(self.run_btn)

        container = QWidget()
        container.setLayout(layout)

        self.run_btn.setEnabled(False)
        self.project_variables_container.setEnabled(False)
        self.parameters_container.setEnabled(False)  # determines whether parameter tab visible or not

        # Set the central widget of the Window.
        self.setCentralWidget(container)
        self.default_param = pastaq.default_parameters('orbitrap', 10)

    def set_project_name(self):
        self.parameters_container.parameters['project_name'] = self.project_name_ui.text()

    def set_project_description(self):
        self.parameters_container.parameters['project_description'] = self.project_description_ui.text()

    def reset_param(self):
        self.update_ui(True)
    
    def view_mode(self):
        if (self.dark == False):
            self.dark_mode()
            self.dark = True
            self.view_mode_btn.setText('Light Mode')
        else:
            self.light_mode()
            self.dark = False
            self.view_mode_btn.setText('Dark Mode')
               
    def dark_mode(self):
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))

        app.setPalette(palette)
        
    def light_mode(self):
        app.setStyle("Fusion")
        palette = QPalette()
        app.setPalette(palette)
                
    def update_ui(self, default=False):
        # Project metadata.
        self.project_directory_ui.setText(os.path.dirname(self.project_path))
        if 'project_name' in self.parameters_container.parameters:
            self.project_name_ui.setText(self.parameters_container.parameters['project_name'])
        if 'project_description' in self.parameters_container.parameters:
            self.project_description_ui.setText(self.parameters_container.parameters['project_description'])
        if default:
            params = self.default_param
        else:
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
        self.parameters_container.min_mz.setValue(params['min_mz'])
        self.parameters_container.max_mz.setValue(params['max_mz'])
        self.parameters_container.min_rt.setValue(params['min_rt'])
        self.parameters_container.max_rt.setValue(params['max_rt'])
        self.parameters_container.polarity.setCurrentText(params['polarity'])
        self.parameters_container.max_peaks.setValue(params['max_peaks'])
        self.parameters_container.link_n_sig_mz.setValue(params['link_n_sig_mz'])
        self.parameters_container.link_n_sig_rt.setValue(params['link_n_sig_rt'])
        self.parameters_container.feature_detection_charge_state_min.setValue(
            min(params['feature_detection_charge_states']))
        self.parameters_container.feature_detection_charge_state_max.setValue(
            max(params['feature_detection_charge_states']))
        self.parameters_container.similarity_num_peaks.setValue(params['similarity_num_peaks'])
        self.parameters_container.qc_plot_palette.setCurrentText(params['qc_plot_palette'])
        self.parameters_container.qc_plot_extension.setCurrentText(params['qc_plot_extension'])
        if params['qc_plot_fill_alpha'] == 'dynamic':
            self.parameters_container.qc_plot_fill_alpha.setValue(0.0)
        else:
            self.parameters_container.qc_plot_fill_alpha.setValue(params['qc_plot_fill_alpha'])
        self.parameters_container.qc_plot_line_alpha.setValue(params['qc_plot_line_alpha'])
        self.parameters_container.qc_plot_scatter_alpha.setValue(params['qc_plot_scatter_alpha'])
        self.parameters_container.qc_plot_scatter_size.setValue(params['qc_plot_scatter_size'])
        self.parameters_container.qc_plot_min_dynamic_alpha.setValue(params['qc_plot_min_dynamic_alpha'])
        if params['qc_plot_per_file']:
            self.parameters_container.qc_plot_per_file.setCheckState(Qt.Checked)
        else:
            self.parameters_container.qc_plot_per_file.setCheckState(Qt.Unchecked)
        self.parameters_container.qc_plot_line_style.setCurrentText(params['qc_plot_line_style'])
        self.parameters_container.qc_plot_dpi.setValue(params['qc_plot_dpi'])
        self.parameters_container.qc_plot_font_family.setCurrentText(params['qc_plot_font_family'])
        self.parameters_container.qc_plot_font_size.setValue(params['qc_plot_font_size'])
        self.parameters_container.qc_plot_fig_size_x.setValue(params['qc_plot_fig_size_x'])
        self.parameters_container.qc_plot_fig_size_y.setValue(params['qc_plot_fig_size_y'])
        if params['qc_plot_fig_legend']:
            self.parameters_container.qc_plot_fig_legend.setCheckState(Qt.Checked)
        else:
            self.parameters_container.qc_plot_fig_legend.setCheckState(Qt.Unchecked)
        self.parameters_container.qc_plot_mz_vs_sigma_mz_max_peaks.setValue(params['qc_plot_mz_vs_sigma_mz_max_peaks'])
        self.parameters_container.quant_isotopes.setCurrentText(params['quant_isotopes'])
        self.parameters_container.quant_features.setCurrentText(params['quant_features'])
        if params['quant_features_charge_state_filter']:
            self.parameters_container.quant_features_charge_state_filter.setCheckState(Qt.Checked)
        else:
            self.parameters_container.quant_features_charge_state_filter.setCheckState(Qt.Unchecked)
        self.parameters_container.quant_ident_linkage.setCurrentText(params['quant_ident_linkage'])
        if params['quant_consensus']:
            self.parameters_container.quant_consensus.setCheckState(Qt.Checked)
        else:
            self.parameters_container.quant_consensus.setCheckState(Qt.Unchecked)
        self.parameters_container.quant_consensus_min_ident.setValue(params['quant_consensus_min_ident'])
        if params['quant_save_all_annotations']:
            self.parameters_container.quant_save_all_annotations.setCheckState(Qt.Checked)
        else:
            self.parameters_container.quant_save_all_annotations.setCheckState(Qt.Unchecked)
        self.parameters_container.quant_proteins_min_peptides.setValue(params['quant_proteins_min_peptides'])
        if params['quant_proteins_remove_subset_proteins']:
            self.parameters_container.quant_proteins_remove_subset_proteins.setCheckState(Qt.Checked)
        else:
            self.parameters_container.quant_proteins_remove_subset_proteins.setCheckState(Qt.Unchecked)
        if params['quant_proteins_ignore_ambiguous_peptides']:
            self.parameters_container.quant_proteins_ignore_ambiguous_peptides.setCheckState(Qt.Checked)
        else:
            self.parameters_container.quant_proteins_ignore_ambiguous_peptides.setCheckState(Qt.Unchecked)
        self.parameters_container.quant_proteins_quant_type.setCurrentText(params['quant_proteins_quant_type'])
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
            caption='Select project directory',
            directory=os.getcwd(),
        )
        if len(dir_path) > 0:
            # TODO: Check if the project file already exists and show a warning
            # dialog to let the user overwrite it.
            self.project_path = os.path.join(dir_path, 'parameters.json')
            self.parameters_container.parameters = pastaq.default_parameters('orbitrap', 10)
            self.save_project_btn.setEnabled(True)
            self.save_project_as_btn.setEnabled(True)
            self.remove_file_btn.setEnabled(True)
            self.run_btn.setEnabled(True)
            self.reset_param_btn.setEnabled(True)
            self.project_variables_container.setEnabled(True)
            self.parameters_container.setEnabled(True)
            self.update_ui()
            self.save_project()
            global pop
            pop = True

    def open_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select project file',
            directory=os.getcwd(),
            filter='Project file (*.json)',
        )
        if len(file_path) > 0:
            os.chdir(os.path.dirname(file_path))
            tmp = json.loads(open(file_path).read())
            # TODO: Validate parameters
            valid = True
            if valid:
                self.parameters_container.parameters = tmp
                self.project_path = file_path
                self.save_project_btn.setEnabled(True)
                self.save_project_as_btn.setEnabled(True)
                self.remove_file_btn.setEnabled(True)
                self.run_btn.setEnabled(True)
                self.reset_param_btn.setEnabled(True)
                self.project_variables_container.setEnabled(True)
                self.parameters_container.setEnabled(True)
                if 'input_files' in self.parameters_container.parameters:
                    self.parameters_container.update_input_files(self.parameters_container.parameters['input_files'])
                self.update_ui()
                global pop
                pop = True

    def save_project(self):
        try:
            with open(self.project_path, 'w') as json_file:
                params = self.parameters_container.parameters
                params['input_files'] = self.parameters_container.input_files
                json.dump(params, json_file)
        except:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText('Error')
            error_dialog.setInformativeText('Can\'t save project at the given directory')
            error_dialog.setWindowTitle('Error')
            error_dialog.exec_()

    def closeEvent(self, event):
        if pop == True:
            box = QMessageBox()
            box.setWindowTitle('Window Close')
            box.setText('Do you want to save your work?')
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            button_s = box.button(QMessageBox.Yes)
            button_s.setText('Save and Exit')
            button_d = box.button(QMessageBox.No)
            button_d.setText('Discard and Exit')
            button_c = box.button(QMessageBox.Cancel)
            button_c.setText('Cancel')
            box.exec_()
            if box.clickedButton() == button_s:
                self.save_project()
                event.accept()
            elif box.clickedButton() == button_c:
                event.ignore()
            else:
                event.accept()

    def save_project_as(self):
        path = QFileDialog.getExistingDirectory(
            parent=self,
            caption='Select project file',
            directory=os.getcwd(),
        )
        if len(path) > 0:
            self.project_path = os.path.join(path, 'parameters.json')
            self.update_ui()
            self.save_project()
            global pop
            pop = True

    def run_pipeline(self):
        # Save changes before running.
        self.save_project()

        # Disable this window so that buttons can't be clicked.
        self.run_btn.setText('Running...')
        self.run_btn.setEnabled(False)
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
            print('EXIT SUCCESS')
        else:
            print('EXIT CANCEL')

        # Restore previous button statuses.
        self.run_btn.setText('Run')
        self.run_btn.setEnabled(True)
        self.project_variables_container.setEnabled(True)
        self.parameters_container.setEnabled(True)


# Initialize main window.
app = QApplication(sys.argv)
app.setWindowIcon(QIcon(':/icons/pastaq.png'))
if platform.system() == 'Windows':
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('pastaq-gui')
app.setStyle("Fusion")

window = MainWindow()
window.resize(QSize(600, 600))
window.show()

# Start the event loop.
app.exec()
