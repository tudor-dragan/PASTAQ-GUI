import buttons
import inspect
import os
import subprocess
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QDialogButtonBox
from PyQt5.QtWidgets import QPushButton, QFileDialog, QDialog, QLabel,  QListWidget
from PyQt5.QtWidgets import QWidget, QLineEdit, QFormLayout, QAction
from pathlib import Path


# creates a popup
def popup_window(status, icon, text):
    popup = QMessageBox()
    popup.setText(text)
    popup.setWindowTitle(status)
    if icon:
        popup.setIcon(icon)
    popup.exec_()
    return  # return is necessary regardless of sonarqube


class EditFileDialog(QDialog):
    """
    This is the modal that shows up when editing an already added .mzML file.
    It allows for adding .mzID files as well as setting a group for the measurement.
    Attributes:
    - the sorting function for the files
    - the updating function
    """
    group = ''
    mzid_paths = []

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('PASTAQ: DDA Pipeline - Add files')
        # Edit parameters
        form_container = QWidget()
        self.group_box = self.init_group()
        mzid_picker = self.init_mzid_picker()

        self.drop = ImageLabel()
        self.setAcceptDrops(True)

        form_layout = self.init_layout(mzid_picker)
        form_container.setLayout(form_layout)

        # Dialog buttons (Ok/Cancel).
        buttons = self.init_buttons()

        layout = QVBoxLayout()
        layout.addWidget(form_container)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def event(self, event):
        instruction = inspect.cleandoc(
            '''Select/drop matching identification files to the selected quantification files.
                mgf and mzID file formats can be uploaded.
                mgf files will automatically be processed to mzID files, when the pipeline is started.
                
                WARNING: Automatic file processing not supported on MacOS
            '''
        )
        if event.type() == QEvent.EnterWhatsThisMode:
            popup_window('Edit files', None, instruction)
        return QDialog.event(self, event)

    # Layout of the modal
    def init_layout(self, mzid_picker):
        lay = QVBoxLayout()
        form_layout = QFormLayout()
        tooltip_group = 'Sample group'
        form_layout.addRow(buttons.init_button_params('Group', tooltip_group), self.group_box)
        tooltip_browse = 'Browse for identification files (.mgf needs to be processed to .mzId, see paths tab)'
        form_layout.addRow(buttons.init_button_params('mgf/mzID', tooltip_browse), mzid_picker)
        form_layout.addRow(self.drop)
        lay.addLayout(form_layout)
        self.files_list = QListWidget()
        lay.addWidget(self.files_list)
        return lay

    # Grouping for the measurements
    def init_group(self):
        group_box = QLineEdit()
        group_box.textChanged.connect(self.set_group)
        return group_box

    # File browsing for corresponding .mzIDs
    def init_mzid_picker(self):
        mzid_picker = QPushButton('Browse')
        mzid_picker.clicked.connect(self.set_mzid_paths)
        return mzid_picker

    def init_buttons(self):
        dialog_buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        buttons = QDialogButtonBox(dialog_buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        return buttons

    # Enables drag and drop event
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def feedback_drop(self):
        self.drop.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa;
                border-color: #8cff66;
            }
        ''')

    # Update the list of the files
    def update_files(self, files):
        self.files_list.clear()
        i = 0
        for file in files:
            self.files_list.insertItem(i, file)
            i += 1

    # When a file is dropped on the UI
    def dropEvent(self, event):
        self.feedback_drop()
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        listing = []
        for file in files:
            if file.lower().endswith('.mzid') or file.lower().endswith('.mzidentmL') or file.lower().endswith('.mgf'):
                listing.append(file)
        if len(listing) > 0:
            self.update_files(listing)
            self.mzid_paths = listing

    def set_group(self):
        self.group = self.group_box.text()

    # Set file paths for the identification files for the project
    def set_mzid_paths(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Select identification files',
            directory=os.getcwd(),
            filter='Identification files (*.mzID *.mzIdentML *.mgf)'
        )
        if len(file_paths) > 0:
            self.update_files(file_paths)
            self.mzid_paths = file_paths


# class for drag and drop field (aesthetics)
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

    def set_pixmap(self, image):
        super().set_pixmap(image)


class FileProcessor:
    """
    This class is responsible for the automatic conversion of .mgf files to .mzID files.
    It requires paths to idconvert and MSFragger executable and parameters file to do the conversion.
    """
    ms_jar = [False, '']
    id_file = [False, '']
    params = [False, '']
    saved = True

    def get_saved(self):
        return self.saved

    def set_saved(self, bool):
        self.saved = bool

    # checks path
    def check_path(self, path):
        if not path or not Path(path).is_file():
            return False
        else:
            return True

    # load given jar file
    def load_ms_path(self, path):
        if self.check_path(path):
            self.ms_jar = [True, path]
            return True
        else:
            return False

    # browse for msfragger .jar file
    def set_jar_path(self, text):
        jar, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption='Select MSFragger .jar file',
            directory=os.getcwd(),
            filter='jar (*.jar)'
        )
        if len(jar) > 0:
            self.ms_jar = [True, jar]
            text.setText(self.ms_jar[1])

    # load given id path
    def load_id_path(self, path):
        if self.check_path(path):
            self.id_file = [True, path]
            return True
        else:
            return False

    # browse for idconvert.exe
    def set_id_path(self, text):
        file, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption='Select idconvert executable',
            directory=os.getcwd(),
            filter='exe (*.exe)'
        )
        if len(file) > 0:
            self.id_file = [True, file]
            text.setText(self.id_file[1])
            self.saved = False

    # load given params path
    def load_params_path(self, path):
        self.params = [True, path]

    # browse for params
    def set_params_path(self, text):
        file, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption='Select .params file',
            directory=os.getcwd(),
            filter='Parameters (*.params)'
        )
        if len(file) > 0:
            self.params = [True, file]
            text.setText(self.params[1])
            self.saved = False

    # split path into jar file name and directory path
    def get_ms(self):
        jar = self.ms_jar[1]
        jar_file = os.path.basename(jar)  # jar
        ms_path = os.path.dirname(jar)  # directory
        return ms_path, jar_file

    # string manipulation to get .pepxml path because location and name are guaranteed
    @staticmethod
    def make_pep_path(mgf):
        return mgf.replace('.mgf', '.pepxml')

    # string manipulation to get .mzID path because location and name are guaranteed
    @staticmethod
    def make_mzid_path(mzid):
        return mzid.replace('.mgf', '.mzID')

    # msfragger process
    def execute_msfragger(self, mgf):
        ms, ms_jar = self.get_ms()
        params = self.params[1]

        # try/exception process failure
        try:
            msfragger = subprocess.run(
                ['java', '-Xmx32g', '-jar', ms_jar, params, mgf],
                cwd=ms,
                capture_output=True
            )
        except subprocess.SubprocessError:
            popup_window('Error', QMessageBox.Critical, 'MSFragger failure')
            return False

        # try/exception output failure
        try:
            msfragger.check_returncode()
        except subprocess.CalledProcessError:
            # print(subprocess.CalledProcessError.output) error in terminal
            # popup window if there was an error
            popup_window('Error', QMessageBox.Critical, 'MSFragger failure')
            return False
        return True

    # idconvert process
    def execute_idconvert(self, pep, mgf):
        id_file = self.id_file[1]

        try:
            idconvert = subprocess.run([id_file, pep, '-o', os.path.dirname(mgf)], capture_output=True)
        except subprocess.SubprocessError:
            popup_window('Error', QMessageBox.Critical, 'idconvert failure')
            return False

        # check if idconvert was successful
        try:
            idconvert.check_returncode()
        except subprocess.CalledProcessError:
            # print(subprocess.CalledProcessError.output) error in terminal
            popup_window('Error', QMessageBox.Critical, 'idconvert failure')
            return False
        return True

    # check all the paths needed for identification
    def check(self):
        if not self.ms_jar[0]:
            popup_window('Error', QMessageBox.Warning, 'MSFragger path is not valid')
            return False
        if not self.id_file[0]:
            popup_window('Error', QMessageBox.Warning, 'idconvert path is not valid')
            return False
        if not self.params[0]:
            popup_window('Error', QMessageBox.Warning, '.params path is not valid')
            return False
        return True

    def delete_pep(self, pep):
        os.unlink(pep)

    # automatic identification process
    def process(self, mgf):
        # check if an .mzid is already in same directory with same name as the mgf
        if os.path.exists(self.make_mzid_path(mgf)):
            return self.make_mzid_path(mgf)

        if not self.check():
            return False

        # execute MSFragger
        if not self.execute_msfragger(mgf):
            return False

        # .pepXML should exist at this point
        pep = self.make_pep_path(mgf)

        # check if path exists just to be sure
        if not os.path.exists(pep):
            popup_window('Error', QMessageBox.Critical, '.pepXML does not exist')
            return False

        # idconvert
        if not self.execute_idconvert(pep, mgf):
            return False

        # delete intermediary .pepXML
        self.delete_pep(pep)

        mzid = self.make_mzid_path(mgf)
        # check if the .mzid file exists
        if not os.path.exists(mzid):
            popup_window('Error', QMessageBox.Critical, '.mzid does not exist')
            return False
        return mzid
