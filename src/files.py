import os
import subprocess

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


# Window when you edit row(s)
class EditFileDialog(QDialog):
    group = ''
    mzid_paths = []

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('PASTAQ: DDA Pipeline - Add files')

        # Edit parameters.
        form_container = QWidget()
        self.group_box = self.init_group()
        mzid_picker = self.init_mzid_picker()

        drop = ImageLabel()
        self.setAcceptDrops(True)

        form_layout = self.init_layout(mzid_picker, drop)
        form_container.setLayout(form_layout)

        # Dialog buttons (Ok/Cancel).
        buttons = self.init_buttons()

        layout = QVBoxLayout()
        layout.addWidget(form_container)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def init_layout(self, mzid_picker, drop):
        form_layout = QFormLayout()
        form_layout.addRow('Group', self.group_box)
        form_layout.addRow('mgf/mzID', mzid_picker)
        form_layout.addRow(drop)
        return form_layout

    def init_group(self):
        group_box = QLineEdit()
        group_box.textChanged.connect(self.set_group)
        return group_box

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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        drop = []
        for file in files:
            if file.endswith(".mzID'") or file.endswith(".mzIdentML'") or file.endswith(".mgf'"):
                drop.append(file)
        if len(drop) > 0:
            self.mzid_paths = drop

    def set_group(self):
        self.group = self.group_box.text()

    def set_mzid_paths(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            parent=self,
            caption='Select input files',
            directory=os.getcwd(),
            filter='Identification files (*.mzID *.mzIdentML *.mgf)'
        )
        if len(file_paths) > 0:
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

    def setPixmap(self, image):
        super().setPixmap(image)


# class for file processing
class FileProcessor:
    ms_jar = [False, '']
    id_file = [False, '']
    params = [False, '']

    # browse for msfragger .jar file
    def set_jar_path(self, text):
        jar, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption='Select MSFragger .jar file',
            directory=os.getcwd(),
            filter='jar (*.jar)'
        )
        if len(jar) > 0:
            self.ms_jar[1] = jar
            text.setText(self.ms_jar[1])

    # confirm .jar file
    def check_ms(self, text):
        if os.path.exists(text):
            self.ms_jar[1] = text
            is_jar = self.ms_jar[1].endswith('.jar')
            if not is_jar:
                self.ms_jar[0] = False
                self.popup_window('Error', 'Not a .jar file')
            else:
                self.ms_jar = [True, text]
                self.popup_window('Success', '.jar confirmed')
        else:
            self.ms_jar[0] = False
            self.popup_window('Error', 'MSFragger path does not exist')

    # browse for idconvert.exe
    def set_id_path(self, text):
        file, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption='Select idconvert executable',
            directory=os.getcwd(),
            filter='exe (*.exe)'
        )
        if len(file) > 0:
            self.id_file[1] = file
            text.setText(self.id_file[1])

    # confirm idconvert
    def check_id(self, text):
        if os.path.exists(text):
            idconvert = os.access(text, os.X_OK)
            if not text.endswith('.exe') or not idconvert:
                self.id_file[0] = False
                self.popup_window('Error', 'Not an .exe file or not executable')

            else:
                self.id_file = [True, text]
                self.popup_window('Success', '.exe confirmed')
        else:
            self.id_file[0] = False
            self.popup_window('Error', 'idconvert path does not exist')

    # browse for params
    def set_params_path(self, text):
        file, _ = QFileDialog.getOpenFileName(
            parent=None,
            caption='Select .params file',
            directory=os.getcwd(),
            filter='Parameters (*.params)'
        )
        if len(file) > 0:
            self.params[1] = file
            text.setText(self.params[1])

    # confirm params
    def check_params(self, text):
        if os.path.exists(text):
            if not text.endswith('.params'):
                self.params[0] = False
                self.popup_window('Error', 'Not a .params file')
            else:
                self.params = [True, text]
                self.popup_window('Success', '.params confirmed')
        else:
            self.params[0] = False
            self.popup_window('Error', '.params path does not exist')

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
        return mzid.replace(".mgf", ".mzID")

    # creates popup
    @staticmethod
    def popup_window(status, text):
        popup = QMessageBox()
        popup.setText(text)
        popup.setWindowTitle(status)
        popup.exec_()
        return

    # msfragger process
    def execute_msfragger(self, mgf):
        ms, ms_jar = self.get_ms()
        params = self.params[1]

        # try/exception process failure
        try:
            msfragger = subprocess.run(
                ["java", "-Xmx32g", "-jar", ms_jar, params, mgf],
                cwd=ms,
                capture_output=True
            )
        except Exception:
            self.popup_window('Error', "MSFragger failure")
            return False

        # try/exception output failure
        try:
            msfragger.check_returncode()
        except subprocess.CalledProcessError:
            # print(subprocess.CalledProcessError.output) error in terminal
            # popup window if there was an error
            self.popup_window('Error', "MSFragger failure")
            return False
        return True

    # idconvert process
    def execute_idconvert(self, pep, mgf):
        id_file = self.id_file[1]

        try:
            idconvert = subprocess.run([id_file, pep, "-o", os.path.dirname(mgf)], capture_output=True)
        except Exception:
            self.popup_window('Error', "idconvert failure")
            return False

        # check if idconvert was successful
        try:
            idconvert.check_returncode()
        except subprocess.CalledProcessError:
            # print(subprocess.CalledProcessError.output) error in terminal
            self.popup_window('Error', "idconvert failure")
            return False
        return True

    # check all the paths needed for identification
    def check(self):
        if not self.ms_jar[0]:
            self.popup_window('Error', 'MSFragger path has not been confirmed or is not valid')
            return False
        if not self.id_file[0]:
            self.popup_window('Error', 'idconvert path has not been confirmed or is not valid')
            return False
        if not self.params[0]:
            self.popup_window('Error', '.params path has not been confirmed or is not valid')
            return False
        return True

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
            self.popup_window('Error', '.pepXML does not exist')
            return False

        # idconvert
        if not self.execute_idconvert(pep, mgf):
            return False

        # delete intermediary .pepXML
        os.unlink(pep)

        mzid = self.make_mzid_path(mgf)
        # check if the .mzid file exists
        if not os.path.exists(mzid):
            self.popup_window('Error', '.mzid does not exist')
            return False
        return mzid
