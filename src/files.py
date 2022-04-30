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

# class for file processing
class FileProcessor:
    ms_jar = ""
    id_file = ""
    fasta = ""
    
    # browse for msfragger .jar file
    def set_jar_path(self, input):
        jar, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select MSFragger .jar file',
            directory=os.getcwd(),
            filter='jar (*.jar)'
        )
        if len(jar) > 0:
            self.ms_jar = jar
            input.setText(self.ms_jar)

    # confirm .jar file
    def check_ms(self, input):
        if os.path.exists(input):
            self.ms_jar = input
            is_jar = self.ms_jar.endswith('.jar')
            if not is_jar:
                self.popup_window('Not a .jar file')
                self.ms_jar = ""
            else:
                return True
        else:
            self.popup_window('MSFragger path does not exist')
            return False

    # browse for idconvert.exe
    def set_id_path(self, input):
        file, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select idconvert executable',
            directory=os.getcwd(),
            filter=('exe (*.exe)')
        )
        if len(file) > 0:
            self.id_file = file
            input.setText(self.id_file)

    # confirm idconvert
    def check_id(self, input):
        if os.path.exists(input):
            self.id_file = input
            idconvert = os.access(self.id_file, os.X_OK)
            if not self.id_file.endswith('.exe') or not idconvert:
                self.popup_window('Not an .exe file or not executable')
                self.id_file = ''
            else:
                return True
        else:
            self.popup_window('idconvert path does not exist')
            return False

    # browse for FASTA database
    def set_fasta_path(self, input):
        file, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption='Select FASTA format protein database',
            directory=os.getcwd(),
            filter='FASTA (*.fasta)'
        )
        if len(file) > 0:
            self.fasta = file
            input.setText(self.fasta)

    # confirm fasta
    def check_fasta(self, input):
        if os.path.exists(input):
            self.fasta = input
            if not self.fasta.endswith('.fasta'):
                self.popup_window('Not a FASTA file')
                self.fasta = ''
            else:
                return True
        else:
            self.popup_window('FASTA path does not exist')
            return True
    
    # split path into jar file and directory
    def get_ms(self):
        jar = self.ms_jar
        jar_file = os.path.basename(jar)  # jar
        ms_path = os.path.dirname(jar)   # directory
        return ms_path, jar_file


    # idconvert
    def get_id(self):
        id = self.id_file
        return id

    # msfragger places pepxml in same directory with same name
    def make_pep_path(self, mgf):
        return mgf.replace('.mgf', '.pepxml')

    # idconvert places mzid in same directory with same name
    def make_mzid_path(self, mzid):
        return mzid.replace(".mgf", ".mzID")

    def popup_window(self, text):
        wrong_path = QMessageBox()
        wrong_path.setText(text)
        wrong_path.setWindowTitle("Error")
        wrong_path.exec_()
        return
    

    def process(self, mgf):
        # check if mzid is already in same directory
        if os.path.exists(self.make_mzid_path(mgf)):
            return self.make_mzid_path(mgf)

        # check .jar and assign if possible
        if self.check_ms(self.ms_jar):
            ms, ms_jar = self.get_ms()
        else:
            return False

        params = "C:/Users/kaitl/Downloads/closed_fragger.params"
        params = "C:/Users/kaitl/Desktop/closed_fragger.params"
        msfragger = subprocess.run(
            ["java", "-Xmx32g", "-jar", ms_jar, params, mgf],
            cwd=ms,
            capture_output=True
        )

        # check if msfragger was successful
        try:
            msfragger.check_returncode()
        except subprocess.CalledProcessError as e:
            print(e.output)
            self.popup_window("MSFragger failure")
            return False

        # .pepXML should exist at this point
        pep = self.make_pep_path(mgf)
        if not os.path.exists(pep):
            self.popup_window(".pepXML does not exist")
            return False

        # idconvert exe
        if (self.check_id(self.id_file)):
            id = self.id_file

        idconvert = subprocess.run([id, pep, "-o", os.path.dirname(mgf)], capture_output=True)

        # check if idconvert was successful
        try:
            idconvert.check_returncode()
        except subprocess.CalledProcessError as e:
            print(e.output)
            self.popup_window("idconvert failure")
            return False

        # delete .pepXML
        os.unlink(pep)

        mzid = self.make_mzid_path(mgf)
        if not os.path.exists(mzid):
            self.popup_window(".mzid does not exist")
            return False

        return mzid
