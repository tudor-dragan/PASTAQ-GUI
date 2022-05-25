import sys, os
import pytest
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMenuBar, QMenu, QAction, QPushButton, QLineEdit, QWidget
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # fixed this for importing app properly
import app


class TestApp:
    application = QApplication(sys.argv)
    mainWindow = app.MainWindow()
    param = {'instrument_type': 'orbitrap', 'resolution_ms1': 70000,
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

    # test if the dark mode is of at initialisation
    def test_init_light_mode(self):
        assert not self.mainWindow.dark

    # check if the icon is right
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
    def test_menu_bar(self):
        menu_bar = self.mainWindow.findChildren(QMenuBar)
        assert len(menu_bar) == 1

    # test if there is a file menu
    def test_file_menu(self):
        menu = self.mainWindow.findChildren(QMenu)
        assert self.mainWindow.fileMenu in menu

    # test if there is a action menu
    def test_action_menu(self):
        menu = self.mainWindow.findChildren(QMenu)
        assert self.mainWindow.actionMenu in menu

    # test if there is a help menu
    def test_help_menu(self):
        menu = self.mainWindow.findChildren(QMenu)
        assert self.mainWindow.fileMenu in menu

    # test the number of menus
    def test_number_menu(self):
        menus = self.mainWindow.findChildren(QMenu)
        assert len(menus) == 3

    # test the number of actions
    def test_number_actions(self):
        actions = self.mainWindow.findChildren(QAction)
        assert len(actions) == 11

    # test the number of buttons
    def test_number_btn(self):
        buttons = self.mainWindow.findChildren(QPushButton)
        assert len(buttons) == 66

    # test is the save project btn is the main window
    def test_save_proj_btn(self):
        buttons = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.save_project_btn in buttons

    # test is the save project as btn is the main window
    def test_save_proj_as_btn(self):
        buttons = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.save_project_as_btn in buttons

    # test if the run btn is the main window
    def test_run_btn(self):
        buttons = self.mainWindow.findChildren(QPushButton)
        assert self.mainWindow.run_btn in buttons

    # test if the reset btn is the main window
    def test_reset_btn(self):
        buttons = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.reset_param_btn in buttons

    # test is the remove btn is the main window
    def test_remove_file_btn(self):
        buttons = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.remove_file_btn in buttons

    # test is the view mode btn is the main window
    def test_view_mode_btn(self):
        buttons = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.view_mode_btn in buttons

    # test if the guide is the main window
    def test_guide(self):
        actions = self.mainWindow.findChildren(QAction)
        assert self.mainWindow.guide in actions

    # test if the default parameters are the right ones
    def test_default_param(self):
        assert self.mainWindow.default_param == self.param

    # check if the default parameter have the right length
    def test_len_default_param(self):
        assert len(self.mainWindow.default_param) == 57

    # check if the project desc is in the main window
    def test_project_desc(self):
        lineEdits = self.mainWindow.findChildren(QLineEdit)
        assert self.mainWindow.project_description_ui in lineEdits

    # check if the project dir is in the main window
    def test_project_dir(self):
        lineEdits = self.mainWindow.findChildren(QLineEdit)
        assert self.mainWindow.project_directory_ui in lineEdits

    # check if the project name ui is in the main window
    def test_project_name_ui(self):
        lineEdits = self.mainWindow.findChildren(QLineEdit)
        assert self.mainWindow.project_name_ui in lineEdits

    # check if the project variable container is in the main window
    def test_project_variables_container(self):
        lineEdits = self.mainWindow.findChildren(QWidget)
        assert self.mainWindow.project_variables_container in lineEdits

    # check if the update_inst function works
    def test_update_inst(self): # (not sure if this is relevant)
        self.param['instrument_type'] = "or"
        self.param['resolution_ms1'] = 70001
        self.param['resolution_ms1'] = 30001
        self.param['reference_mz'] = 201
        self.param['avg_fwhm_rt'] = 11
        self.mainWindow.update_inst(params=self.param)
        assert self.mainWindow.parameters_container.inst_type == self.param['instrument_type']
        assert self.mainWindow.parameters_container.res_ms1 == self.param['resolution_ms1']
        assert self.mainWindow.parameters_container.res_ms2 == self.param["resolution_ms1"]
        assert self.mainWindow.parameters_container.reference_mz == self.param['reference_mz']
        assert self.mainWindow.parameters_container.avg_fwhm_rt == self.param['avg_fwhm_rt']

    # # check if the update_inst function works
    # def test_update_raw(self):
    #     self.param['instrument_type'] = "or"
    #     self.param['resolution_ms1'] = 70001
    #     self.param['resolution_ms1'] = 30001
    #     self.param['reference_mz'] = 201
    #     self.param['avg_fwhm_rt'] = 11
    #     self.mainWindow.update_raw(params=self.param)
    #     assert self.mainWindow.parameters_container.inst_type == self.param['instrument_type']
    #     assert self.mainWindow.parameters_container.res_ms1 == self.param['resolution_ms1']
    #     assert self.mainWindow.parameters_container.res_ms2 == self.param["resolution_ms1"]
    #     assert self.mainWindow.parameters_container.reference_mz == self.param['reference_mz']
    #     assert self.mainWindow.parameters_container.avg_fwhm_rt == self.param['avg_fwhm_rt']