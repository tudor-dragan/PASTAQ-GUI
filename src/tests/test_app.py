import sys, os
import pytest
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMenuBar, QMenu, QAction, QPushButton, QLineEdit, QWidget
from PyQt5.QtTest import QTest
from pathlib import Path

from PyQt5.QtCore import Qt
import mock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # fixed this for importing app properly
import app


class TestApp:
    application = QApplication(sys.argv)
    mainWindow = app.MainWindow()
    default_param = {'instrument_type': 'orbitrap', 'resolution_ms1': 70000,
                     'resolution_msn': 30000,
                     'reference_mz': 200, 'avg_fwhm_rt': 10, 'num_samples_mz': 5,
                     'num_samples_rt': 5,
                     'smoothing_coefficient_mz': 0.4, 'smoothing_coefficient_rt': 0.4,
                     'warp2d_slack': 30,
                     'warp2d_window_size': 100, 'warp2d_num_points': 2000,
                     'warp2d_rt_expand_factor': 0.2,
                     'warp2d_peaks_per_window': 100, 'metamatch_fraction': 0.7,
                     'metamatch_n_sig_mz': 1.5,
                     'metamatch_n_sig_rt': 1.5,
                     'feature_detection_charge_states': [5, 4, 3, 2, 1],
                     'max_peaks': 1000000, 'polarity': 'both', 'min_mz': 0,
                     'max_mz': 100000,
                     'min_rt': 0,
                     'max_rt': 100000, 'link_n_sig_mz': 3, 'link_n_sig_rt': 3,
                     'ident_max_rank_only': True,
                     'ident_require_threshold': True, 'ident_ignore_decoy': True,
                     'similarity_num_peaks': 2000,
                     'qc_plot_palette': 'husl', 'qc_plot_extension': 'png',
                     'qc_plot_fill_alpha': 'dynamic',
                     'qc_plot_line_alpha': 0.5, 'qc_plot_scatter_alpha': 0.3,
                     'qc_plot_scatter_size': 2,
                     'qc_plot_min_dynamic_alpha': 0.1, 'qc_plot_per_file': False,
                     'qc_plot_line_style': 'fill',
                     'qc_plot_dpi': 300, 'qc_plot_font_family': 'sans-serif',
                     'qc_plot_font_size': 7,
                     'qc_plot_fig_size_x': 7.08661, 'qc_plot_fig_size_y': 4.379765814562611,
                     'qc_plot_fig_legend': False,
                     'qc_plot_mz_vs_sigma_mz_max_peaks': 200000,
                     'quant_isotopes': 'height', 'quant_features': 'max_height',
                     'quant_features_charge_state_filter': True,
                     'quant_ident_linkage': 'msms_event',
                     'quant_consensus': True, 'quant_consensus_min_ident': 2,
                     'quant_save_all_annotations': True,
                     'quant_proteins_min_peptides': 1,
                     'quant_proteins_remove_subset_proteins': True,
                     'quant_proteins_ignore_ambiguous_peptides': True,
                     'quant_proteins_quant_type': 'razor'}

    test_param = {'instrument_type': 'or', 'resolution_ms1': 500,
                  'resolution_msn': 4,
                  'reference_mz': 200, 'avg_fwhm_rt': 10, 'num_samples_mz': 5,
                  'num_samples_rt': 5}

    # test if the dark mode is of at initialisation
    # T1.1
    def test_init_light_mode(self):
        assert not self.mainWindow.dark

    # check if the icon is right
    # T1.2
    def test_icon(self):
        testIcon = self.mainWindow.init_logo()
        pixmap = QPixmap(':/icons/pastaq.png')
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
        icon = QLabel()
        icon.setPixmap(pixmap)
        assert icon.layout() == testIcon.layout()
        assert icon.font() == testIcon.font()
        assert icon.height() == testIcon.height()
        assert icon.picture() == testIcon.picture()

    # check if the menu bar is present and that there is only one
    # T1.3
    def test_menu_bar(self):
        menu_bar = self.mainWindow.findChildren(QMenuBar)
        assert len(menu_bar) == 1

    # test if there is a file menu
    # T1.4
    def test_file_menu(self):
        menu = self.mainWindow.findChildren(QMenu)
        assert self.mainWindow.fileMenu in menu

    # test if there is a action menu
    # T1.5
    def test_action_menu(self):
        menu = self.mainWindow.findChildren(QMenu)
        assert self.mainWindow.actionMenu in menu

    # test if there is a help menu
    # T1.6
    def test_help_menu(self):
        menu = self.mainWindow.findChildren(QMenu)
        assert self.mainWindow.fileMenu in menu

    # test the number of menus
    # T1.7
    def test_number_menu(self):
        menus = self.mainWindow.findChildren(QMenu)
        assert len(menus) == 3

    # test the number of actions
    # T1.8
    def test_number_actions(self):
        actions = self.mainWindow.findChildren(QAction)
        assert len(actions) == 10

    # test the number of buttons
    # T1.9
    def test_number_btn(self):
        buttons = self.mainWindow.findChildren(QPushButton)
        assert len(buttons) == 66

    # test is the save project btn is the main window
    # T1.10
    def test_save_proj_btn(self):
        buttons = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.save_project_btn in buttons

    # test is the save project as btn is the main window
    # T1.11
    def test_save_proj_as_btn(self):
        buttons = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.save_project_as_btn in buttons

    # test if the run btn is the main window
    # T1.12
    def test_run_btn(self):
        buttons = self.mainWindow.findChildren(QPushButton)
        assert self.mainWindow.run_btn in buttons

    # test if the reset btn is the main window
    # T1.13
    def test_reset_btn(self):
        buttons = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.reset_param_btn in buttons

    # test is the view mode btn is the main window
    # T1.14
    def test_view_mode_btn(self):
        buttons = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.view_mode_btn in buttons

    # test if the guide is the main window
    # T1.15
    def test_guide(self):
        actions = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.guide in actions

    # test if the default parameters are the right ones
    # T1.16
    def test_default_param(self):
        assert self.mainWindow.default_param == self.default_param

    # check if the default parameter have the right length
    # T1.17
    def test_len_default_param(self):
        assert len(self.mainWindow.default_param) == 57

    # check if the project desc is in the main window
    # T1.18
    def test_project_desc(self):
        lineEdits = self.mainWindow.findChildren(QLineEdit)
        assert self.mainWindow.project_description_ui in lineEdits

    # check if the project dir is in the main window
    # T1.19
    def test_project_dir(self):
        lineEdits = self.mainWindow.findChildren(QLineEdit)
        assert self.mainWindow.project_directory_ui in lineEdits

    # check if the project name ui is in the main window
    # T1.20
    def test_project_name_ui(self):
        lineEdits = self.mainWindow.findChildren(QLineEdit)
        assert self.mainWindow.project_name_ui in lineEdits

    # check if the project variable container is in the main window
    # T1.21
    def test_project_variables_container(self):
        lineEdits = self.mainWindow.findChildren(QWidget)
        assert self.mainWindow.project_variables_container in lineEdits

    # check if preparing a new project sets the right parameters and enables the right buttons
    # T1.22
    def test_prepare_new_project(self):
        self.mainWindow.prepare_new_project('')
        assert self.mainWindow.parameters_container.parameters == self.default_param
        assert self.mainWindow.save_project_btn.isEnabled()
        assert self.mainWindow.save_project_as_btn.isEnabled()
        assert self.mainWindow.reset_param_btn.isEnabled()
        assert self.mainWindow.project_variables_container.isEnabled()
        assert self.mainWindow.parameters_container.isEnabled()

    # check if preparing to open a project sets the right parameters and enables the right buttons
    # T1.23
    def test_prepare_open_project(self):
        self.mainWindow.parameters_container.parameters = self.default_param
        self.mainWindow.prepare_open_project(self.test_param, '')
        assert self.mainWindow.parameters_container.parameters == self.test_param
        assert self.mainWindow.project_path == ''
        assert self.mainWindow.save_project_btn.isEnabled()
        assert self.mainWindow.save_project_as_btn.isEnabled()
        assert self.mainWindow.reset_param_btn.isEnabled()
        assert self.mainWindow.project_variables_container.isEnabled()
        assert self.mainWindow.parameters_container.isEnabled()

    # check if reading the config without config file behaves correctly
    # T1.24
    @mock.patch('app.MainWindow')
    def test_read_config_without_file(self, mock_window):
        mock_window.get_config_path.return_value = ''
        assert mock_window.read_config()

    # TODO: test config with config file (I don't have any - nacer)

    # check if the paths are being loaded when there is no config
    # T1.25
    @mock.patch('app.MainWindow')
    def test_prepare_paths_tab_without_config(self, mock_window):
        mock_window.read_config.return_value = False
        mock_window.prepare_paths_tab()
        assert not mock_window.parameters_container.load_ms_path.called
        assert not mock_window.parameters_container.load_id_path.called

    # check if the paths are being loaded when there is a config
    # T1.26
    @mock.patch('app.MainWindow')
    def test_prepare_paths_tab_with_config(self, mock_window):
        mock_window.read_config.return_value = './test/'
        mock_window.prepare_paths_tab()
        assert mock_window.parameters_container.input_ms.text()
        assert mock_window.parameters_container.input_id.text()

    # tests if a project saves properly
    # T1.27
    @mock.patch('app.MainWindow')
    def test_save_project(self, mock_window):
        mock_window.save_json = True
        mock_window.save_paths = True
        self.mainWindow.parameters_container.set_saved(False)
        mock_window.save_project()
        assert self.mainWindow.parameters_container.get_saved()

    # test if the run restoration functions properly
    # T1.28
    def test_restore_run(self):
        self.mainWindow.run_btn.setText('')
        self.mainWindow.project_variables_container.setEnabled(False)
        self.mainWindow.parameters_container.setEnabled(False)
        self.mainWindow.restore_run()
        assert self.mainWindow.run_btn.text() == 'Run'
        assert self.mainWindow.project_variables_container.isEnabled()
        assert self.mainWindow.parameters_container.isEnabled()
