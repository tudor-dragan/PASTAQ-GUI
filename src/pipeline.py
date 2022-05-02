import sys
import time

import pastaq
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

# The log text appearing on the pipeline modal
class TextStream(QObject):
    # A qt signal carrying the text output by the pipeline
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(str(text))

# Thread that runs the pipeline parallel to the GUI
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

# A modal that appears after the running of the pipeline
# It outputs the log of the pipeline and allows for cancellation.
class PipelineLogDialog(QDialog):
    group = ''
    mzid_paths = []

    def __init__(self, params, input_files, output_dir, parent=None):
        super().__init__(parent)

        self.setWindowTitle('PASTAQ: DDA Pipeline (Running)')

        # Add custom output to text stream.
        sys.stdout = TextStream(text_written=self.append_text)

        # Log text box.
        self.text_box = self.init_log()

        # Dialog buttons (Ok/Cancel).
        self.buttons = self.init_buttons()

        # Prepare layout.
        self.setLayout(self.init_layout())

        self.pipeline_thread = self.init_pipeline(params, input_files, output_dir)
        self.pipeline_thread.start()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def init_log(self):
        text_box = QTextEdit()
        text_box.setReadOnly(True)
        return text_box

    # Allows for cancelation of the pipeline or confirmation once it is done
    def init_buttons(self):
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(self.exit_failure)
        return buttons

    def init_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.text_box)
        layout.addWidget(self.buttons)
        return layout

    # Creates the pipeline thread with the input files and parameters
    def init_pipeline(self, params, input_files, output_dir):
        pipeline_thread = PipelineRunner()
        pipeline_thread.params = params
        pipeline_thread.input_files = input_files
        pipeline_thread.output_dir = output_dir
        pipeline_thread.finished.connect(self.exit_success)
        return pipeline_thread

    # Appends text in the log field from the pipeline
    def append_text(self, text):
        cursor = self.text_box.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.text_box.setTextCursor(cursor)
        self.text_box.ensureCursorVisible()

    def exit_success(self):
        # Restore stdout pipe.
        sys.stdout = sys.__stdout__

        # Replace button with OK instead of Cancel.
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
