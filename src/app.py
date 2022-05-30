import json
import os
import parameter
import pastaq
import pipeline
import platform
import resources
import sys
import time
import webbrowser
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QIcon, QKeySequence, QPalette, QColor, QPixmap
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QVBoxLayout, QLabel, QSplashScreen
from PyQt5.QtWidgets import QPushButton, QFileDialog, QApplication, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QAction, QLineEdit, QFormLayout, QFrame
from configparser import ConfigParser
from pathlib import Path
from time import time, sleep


# Setting the colors to lighter colors
def light_mode():
    app.setStyle("Fusion")
    palette = QPalette()
    app.setPalette(palette)


# Error dialog when unable to save the project.
def init_error_dialog(text):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setText('Error')
    error_dialog.setInformativeText(text)
    error_dialog.setWindowTitle('Error')
    return error_dialog


# Popup that appears if the project is closed without saving.
def close_popup():
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
    return box, button_s, button_d, button_c


class MainWindow(QMainWindow):
    """
    This is the main windows of the GUI, and it contains the project settings
    as well as the input tabs for files parameters and conversion executables.
    """
    project_path = ''
    dark = False

    def __init__(self):
        super().__init__()
        self.setWindowTitle('PASTAQ: DDA Pipeline')
        # Tabbed input files/parameters
        self.parameters_container = parameter.ParametersWidget()
        self.file_processor = self.parameters_container.file_processor
        self.parameters_container.setEnabled(False)  # determines whether parameter tab visible or not
        # Main layout
        layout = QVBoxLayout()

        # Menu Bar
        self.init_menu()

        # New Project
        self.init_new_project()

        # Open Project
        self.init_open_project()

        # Save Project
        self.init_save_project()

        # Save Project As
        self.init_save_as()

        # reset button
        self.init_reset()

        # dark/light mode button
        self.init_dark()

        self.init_guide()

        # Project variables.
        self.project_variables_container = self.init_var()
        self.project_variables_container.setEnabled(False)

        header = QHBoxLayout()
        meta = QVBoxLayout()
        icon = self.init_logo()

        # project meta
        meta.addWidget(self.project_variables_container)
        # add meta and logo
        header.addLayout(meta)
        header.addWidget(icon)
        layout.addLayout(header)
        # Applying layout to tabbed input files/parameters
        layout.addWidget(self.parameters_container)

        # Run button
        self.init_run()
        layout.addWidget(self.run_btn)

        container = QWidget()
        container.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)
        self.default_param = pastaq.default_parameters('orbitrap', 10)

    def init_logo(self):
        label = QLabel()
        pixmap = QPixmap(':/icons/pastaq.png')
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        label.setPixmap(pixmap)
        return label

    # Project menu allowing for creating opening and saving.
    def init_menu(self):
        self.menu = self.menuBar()
        self.fileMenu = self.menu.addMenu('File')
        self.actionMenu = self.menu.addMenu('Action')
        self.helpMenu = self.menu.addMenu('Help')

    def guide_action(self):
        webbrowser.open('https://pastaq.horvatovichlab.com/gui-tutorial/index.html')

    def init_guide(self):
        self.guide = QAction('Guide', self)
        self.guide.triggered.connect(self.guide_action)
        self.helpMenu.addAction(self.guide)

    def add_menu_action(self, action):
        self.fileMenu.addAction(action)

    def init_new_project(self):
        self.newProj = QAction('New Project', self)
        self.newProj.triggered.connect(self.new_project)
        self.newProj.setShortcut(QKeySequence('Ctrl+n'))
        self.add_menu_action(self.newProj)

    def init_open_project(self):
        self.openProj = QAction('Open Project', self)
        self.openProj.triggered.connect(self.open_project)
        self.openProj.setShortcut(QKeySequence('Ctrl+o'))
        self.add_menu_action(self.openProj)

    def init_save_project(self):
        self.save_project_btn = QAction('Save', self)
        self.save_project_btn.triggered.connect(self.save_project)
        self.save_project_btn.setShortcut(QKeySequence('Ctrl+s'))
        self.save_project_btn.setEnabled(False)
        self.add_menu_action(self.save_project_btn)

    def init_save_as(self):
        self.save_project_as_btn = QAction('Save as', self)
        self.save_project_as_btn.triggered.connect(self.save_project_as)
        self.save_project_as_btn.setEnabled(False)
        self.add_menu_action(self.save_project_as_btn)

    def add_action_menu_action(self, action):
        self.actionMenu.addAction(action)

    def init_reset(self):
        self.reset_param_btn = QAction('Reset Parameters', self)
        self.reset_param_btn.triggered.connect(self.reset_param)
        self.reset_param_btn.setEnabled(False)
        self.add_action_menu_action(self.reset_param_btn)

    def init_dark(self):
        self.view_mode_btn = QAction('Dark Mode', self)
        self.view_mode_btn.triggered.connect(self.view_mode)
        self.reset_param_btn.setEnabled(True)
        self.add_action_menu_action(self.view_mode_btn)

    def init_project_name(self):
        self.project_name_ui = QLineEdit()
        self.project_name_ui.textChanged.connect(self.set_project_name)

    def init_project_desc(self):
        self.project_description_ui = QLineEdit()
        self.project_description_ui.textChanged.connect(self.set_project_description)

    def init_project_dir(self):
        self.project_directory_ui = QLineEdit()
        self.project_directory_ui.setReadOnly(True)

    def init_var(self):
        project_variables_container = QWidget()
        project_variables_layout = QFormLayout()
        self.init_project_name()
        self.init_project_desc()
        self.init_project_dir()
        project_variables_layout.addRow('Project name', self.project_name_ui)
        project_variables_layout.addRow('Project description', self.project_description_ui)
        project_variables_layout.addRow('Project directory', self.project_directory_ui)
        project_variables_container.setLayout(project_variables_layout)
        return project_variables_container

    def init_run(self):
        self.run_btn = QPushButton('Run')
        self.run_btn.clicked.connect(self.run_pipeline)
        self.run_btn.setEnabled(False)
        self.parameters_container.set_run_btn(self.run_btn)

    def set_project_name(self):
        self.parameters_container.parameters['project_name'] = self.project_name_ui.text()
        self.parameters_container.set_saved(False)

    def set_project_description(self):
        self.parameters_container.parameters['project_description'] = self.project_description_ui.text()
        self.parameters_container.set_saved(False)

    def set_params_path(self):
        self.parameters_container.parameters['params_path'] = self.parameters_container.get_file_processor.params[1]
        self.parameters_container.set_saved(False)

    # Menu action that resets all parameters to default value.
    def reset_param(self):
        box = QMessageBox()
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle('Reset Parameters')
        box.setText('Are you sure you want to reset parameters?')
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        button_s = box.button(QMessageBox.Yes)
        box.exec_()
        if box.clickedButton() == button_s:
            self.update_ui(True)
        self.parameters_container.set_saved(False)

    # Setting the color palette of the UI to dark colors.
    def dark_mode(self):
        self.setStyle("Fusion")
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

        self.setPalette(palette)

    # changes the colors of the GUI to either dark or light
    def view_mode(self):
        if not self.dark:
            self.dark_mode()
            self.dark = True
            self.view_mode_btn.setText('Light Mode')
        else:
            light_mode()
            self.dark = False
            self.view_mode_btn.setText('Dark Mode')

    # Updating the project settings
    def update_meta_project(self):
        self.project_directory_ui.setText(os.path.dirname(self.project_path))
        if 'project_name' in self.parameters_container.parameters:
            self.project_name_ui.setText(self.parameters_container.parameters['project_name'])
        if 'project_description' in self.parameters_container.parameters:
            self.project_description_ui.setText(self.parameters_container.parameters['project_description'])

    # update params path
    def update_params(self):
        if 'params_path' in self.parameters_container.parameters:
            self.parameters_container.set_params_path(self.parameters_container.parameters['params_path'])

    # Updating the parameters for the instrument section
    def update_inst(self, params):
        self.parameters_container.inst_type.setCurrentText(params['instrument_type'])
        self.parameters_container.res_ms1.setValue(params['resolution_ms1'])
        self.parameters_container.res_ms2.setValue(params['resolution_msn'])
        self.parameters_container.reference_mz.setValue(params['reference_mz'])
        self.parameters_container.avg_fwhm_rt.setValue(params['avg_fwhm_rt'])

    def update_raw(self, params):
        self.parameters_container.min_mz.setValue(params['min_mz'])
        self.parameters_container.max_mz.setValue(params['max_mz'])
        self.parameters_container.min_rt.setValue(params['min_rt'])
        self.parameters_container.max_rt.setValue(params['max_rt'])
        self.parameters_container.polarity.setCurrentText(params['polarity'])

    def update_resamp(self, params):
        self.parameters_container.num_samples_mz.setValue(params['num_samples_mz'])
        self.parameters_container.num_samples_rt.setValue(params['num_samples_rt'])
        self.parameters_container.smoothing_coefficient_mz.setValue(params['smoothing_coefficient_mz'])
        self.parameters_container.smoothing_coefficient_rt.setValue(params['smoothing_coefficient_rt'])
        self.parameters_container.max_peaks.setValue(params['max_peaks'])
        self.parameters_container.feature_detection_charge_state_min.setValue(
            min(params['feature_detection_charge_states']))
        self.parameters_container.feature_detection_charge_state_max.setValue(
            max(params['feature_detection_charge_states']))

    def update_warp(self, params):
        self.parameters_container.warp2d_slack.setValue(params['warp2d_slack'])
        self.parameters_container.warp2d_window_size.setValue(params['warp2d_window_size'])
        self.parameters_container.warp2d_num_points.setValue(params['warp2d_num_points'])
        self.parameters_container.warp2d_rt_expand_factor.setValue(params['warp2d_rt_expand_factor'])
        self.parameters_container.warp2d_peaks_per_window.setValue(params['warp2d_peaks_per_window'])

    def update_meta(self, params):
        self.parameters_container.metamatch_fraction.setValue(params['metamatch_fraction'])
        self.parameters_container.metamatch_n_sig_mz.setValue(params['metamatch_n_sig_mz'])
        self.parameters_container.metamatch_n_sig_rt.setValue(params['metamatch_n_sig_rt'])

    def update_ident(self, params):
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
        self.parameters_container.link_n_sig_mz.setValue(params['link_n_sig_mz'])
        self.parameters_container.link_n_sig_rt.setValue(params['link_n_sig_rt'])
        self.parameters_container.similarity_num_peaks.setValue(params['similarity_num_peaks'])

    def update_qual(self, params):
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

    def update_quantt(self, params):
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

    def update_ui(self, default=False):
        # Project metadata.
        self.update_meta_project()
        if default:
            params = self.default_param
        else:
            params = self.parameters_container.parameters

        self.parameters_container.update_allowed = False
        self.update_inst(params)
        self.update_raw(params)
        self.update_resamp(params)
        self.update_warp(params)
        self.update_meta(params)
        self.update_ident(params)
        self.update_qual(params)
        self.update_quantt(params)
        self.parameters_container.update_allowed = True

    # Creates a new project at the specified folder
    def new_project(self):
        dir_path = QFileDialog.getExistingDirectory(
            parent=self,
            caption='Select project directory',
            directory=os.getcwd(),
        )
        if len(dir_path) > 0:
            self.prepare_new_project(dir_path)
            self.prepare_paths_tab()
            self.update_ui()
            self.save_project()
            self.parameters_container.set_saved(True)

    # Enables the features of the UI once a project is created
    def prepare_new_project(self, dir_path):
        self.project_path = os.path.join(dir_path, 'parameters.json')
        self.parameters_container.parameters = pastaq.default_parameters('orbitrap', 10)
        self.save_project_btn.setEnabled(True)
        self.save_project_as_btn.setEnabled(True)
        self.parameters_container.check_run_btn()
        self.reset_param_btn.setEnabled(True)
        self.project_variables_container.setEnabled(True)
        self.parameters_container.setEnabled(True)

    # Opens an already existing project.
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
            self.prepare_open_project(tmp, file_path)
            self.prepare_paths_tab()
            self.update_ui()
            self.parameters_container.set_saved(True)

    # Enables the features of the UI once a project is opened
    def prepare_open_project(self, tmp, file_path):
        self.parameters_container.parameters = tmp
        self.project_path = file_path
        self.save_project_btn.setEnabled(True)
        self.save_project_as_btn.setEnabled(True)
        self.parameters_container.check_run_btn()
        self.reset_param_btn.setEnabled(True)
        self.project_variables_container.setEnabled(True)
        self.parameters_container.setEnabled(True)
        if 'input_files' in self.parameters_container.parameters:
            self.parameters_container.update_input_files(self.parameters_container.parameters['input_files'])
        if 'params_path' in self.parameters_container.parameters:
            self.parameters_container.load_params(self.parameters_container.parameters['params_path'])

    # creates config path
    def get_config_path(self):
        config_dir_path = os.path.dirname(os.path.dirname(__file__))
        config = os.path.join(config_dir_path, 'config.ini')
        return Path(config)

    # Reads config
    def read_config(self):
        config = self.get_config_path()
        if config.is_file():
            config_object = ConfigParser()
            try:
                config_object.read(config)
                paths = config_object['paths']
                return paths
            except OSError:
                dialog = init_error_dialog('Can\'t read from config file.')
                dialog.exec_()
                return False
        else:
            return False

    # loads config into GUI
    def prepare_paths_tab(self):
        paths = self.read_config()
        if paths:
            self.parameters_container.load_ms_path(paths['ms_jar'])
            self.parameters_container.load_id_path(paths['id_file'])

    # Saves all the parts of a project as a json file.
    # This file can later be used to reopen the project or to start the PASTAQ pipeline.
    def save_project(self):
        try:
            self.save_json()
            self.save_paths()
            self.parameters_container.set_saved(True)
        except IOError:
            dialog = init_error_dialog('Can\'t save project at the given directory')
            dialog.exec_()

    # Stores the project in a json file
    def save_json(self):
        with open(self.project_path, 'w') as json_file:
            params_values = self.parameters_container.parameters
            params_values['input_files'] = self.parameters_container.input_files
            params_values['params_path'] = self.file_processor.params[1]
            json.dump(params_values, json_file)

    # Stores the paths in a config file
    def save_paths(self):
        if not self.check_config():
            config_object = ConfigParser()
            config_object['paths'] = {
                'ms_jar': self.file_processor.ms_jar[1],
                'id_file': self.file_processor.id_file[1]
            }
            with open(self.get_config_path(), 'w+') as conf:
                config_object.write(conf)

    # Check if the config file needs to be changed or not
    def check_config(self):
        # check if paths stayed the same
        paths = self.read_config()
        if paths:
            if paths['ms_jar'] == self.file_processor.ms_jar[1] and paths['id_file'] == self.file_processor.id_file[1]:
                return True
            else:
                return False
        else:
            return False

    # If the project is not saved open a popup otherwise close the UI
    def closeEvent(self, event):
        if not self.parameters_container.get_saved():
            box, button_s, button_d, button_c = close_popup()
            box.exec_()
            if box.clickedButton() == button_s:
                self.save_project()
                event.accept()
            elif box.clickedButton() == button_c:
                event.ignore()
            else:
                event.accept()

    # Saves the project to a new directory
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
            self.parameters_container.set_saved(True)

    def prepare_run(self):
        # Save changes before running.
        self.save_project()

        # Disable this window so that buttons can't be clicked.
        self.run_btn.setText('Running...')
        self.run_btn.setEnabled(False)
        self.project_variables_container.setEnabled(False)
        self.parameters_container.setEnabled(False)

    # Creates the pipeline runner thread and modal
    def init_pipeline(self):
        pipe = pipeline.PipelineLogDialog(
            parent=self,
            params=self.parameters_container.parameters,
            input_files=self.parameters_container.input_files,
            output_dir=os.path.dirname(self.project_path),
            file_processor=self.parameters_container.get_file_processor())
        return pipe

    def restore_run(self):
        # Restore previous button statuses.
        self.run_btn.setText('Run')
        self.parameters_container.check_run_btn()
        self.project_variables_container.setEnabled(True)
        self.parameters_container.setEnabled(True)

    # Runs the PASTAQ pipeline with the input files and parameters.
    # This creates a new thread for the pipeline that runs in parallel to the GUI thread.
    def run_pipeline(self):
        self.prepare_run()

        # Open modal with log progress and cancel button and run pipeline
        # in a different thread/fork.
        pipeline_log_dialog = self.init_pipeline()
        if pipeline_log_dialog.exec():
            print('EXIT SUCCESS')
        else:
            print('EXIT CANCEL')

        self.restore_run()


class SplashScreen(QSplashScreen):
    """
    This is the splash screen of the GUI, and it contains the logo
    and informs that the main frame of the GUI is loading.
    """
    def __init__(self):
        super(QSplashScreen, self).__init__()
        # TODO another pic
        pixmap = QPixmap(':/splash/loading.png')
        self.setPixmap(pixmap)

        self.window = MainWindow()
        self.window.resize(QSize(900, 700))
        QTimer.singleShot(1500, self.done)

    def done(self):
        self.close()
        self.window.show()


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/icons/pastaq.png'))

    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('pastaq-gui')
    app.setStyle("Fusion")

    # show splash screen before opening GUI
    splash = SplashScreen()
    splash.show()

    app.processEvents()

    app.exec_()


if __name__ == "__main__":
    main()
