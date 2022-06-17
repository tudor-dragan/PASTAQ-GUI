from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton


# Each changeable parameter in the parameters tab with its tooltip.
def init_button_params(label, tooltip):
    button = ParameterLabel(label)
    button.setToolTip(tooltip)

    icon = QIcon(':/icons/question.png')
    button.setLayoutDirection(Qt.RightToLeft)
    button.setIcon(icon)
    button.setFlat(True)

    return button


# Do nothing when pressing a label.
class ParameterLabel(QPushButton):

    def mousePressEvent(self, event):
        return
