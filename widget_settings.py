import re
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QGroupBox, QComboBox, QRadioButton, QCheckBox
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt


class Label(QLabel):
    def __init__(self, text: str, fixed_width=0, fixed_height=50):
        super().__init__()
        self.setText(text)
        self.setStyleSheet('color: #203764; font-size: 16px; font-weight: bold')
        if fixed_width:
            self.setFixedWidth(fixed_width)
        if fixed_height:
            self.setFixedHeight(fixed_height)


class LabelCode(QLabel):
    def __init__(self, text: str, fixed_width=0, fixed_height=50):
        super().__init__()
        self.setText(text)
        self.setStyleSheet('color: #4D7731; font-size: 16px; font-weight: bold; font-family: Courier New')
        if fixed_width:
            self.setFixedWidth(fixed_width)
        if fixed_height:
            self.setFixedHeight(fixed_height)


class SmallLabel(QLabel):
    def __init__(self, text: str, fixed_width=0, fixed_height=0, color='green'):
        super().__init__()
        self.setText(text)
        self.setStyleSheet(f'color: {color}; font-size: 12px')
        if fixed_width:
            self.setFixedWidth(fixed_width)
        if fixed_height:
            self.setFixedHeight(fixed_height)


class EditBox(QLineEdit):
    def __init__(self, text='', fixed_width=0, fixed_height=30, max_length=50):
        super().__init__(text)
        self.setStyleSheet('color: #203764; font-size: 16px; font-weight: bold')
        if fixed_width:
            self.setFixedWidth(fixed_width)
        if fixed_height:
            self.setFixedHeight(fixed_height)
        if max_length:
            self.setMaxLength(max_length)


class Button(QPushButton):
    def __init__(self, text: str, fixed_width=0, fixed_height=50):
        super().__init__()
        self.setText(text)
        self.setStyleSheet("""
            QPushButton {font-size: 16px; font-weight: bold; color: #203764; border: 2px groove #c0c0c0; border-radius: 6px;
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
            stop: 0 #f0f0f0, stop: 1 #d0d0d0)}
            QPushButton::disabled {background-color: #D9D9D9; color: gray; font-weight: bold}
            QPushButton::hover {background-color: #203764; color: white; font-weight: bold}
            """)
        if fixed_width:
            self.setFixedWidth(fixed_width)
        if fixed_height:
            self.setFixedHeight(fixed_height)


class Group(QGroupBox):
    def __init__(self, text: str):
        super().__init__()
        self.setStyleSheet("""
            QGroupBox {
                font-size: 16px; 
                font-weight: bold; 
                margin-top: 15px; 
                border: 2px solid black;
                border-radius: 6px;
                padding: 5px
                }
            QGroupBox::title {
                color: #203764;
                subcontrol-origin: margin;
                left: 10px;
                padding: 5px 5px 5px 5px;
                }""")
        self.setTitle(text)


class ComboList(QComboBox):
    def __init__(self, fixed_width=0, fixed_height=30):
        super().__init__()
        self.setStyleSheet('color: #203764; font-size: 16px')
        self.setMaxVisibleItems(10)
        if fixed_width:
            self.setFixedWidth(fixed_width)
        if fixed_height:
            self.setFixedHeight(fixed_height)


class RadioButton(QRadioButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setStyleSheet('''
        color: #203764; 
        border: 1px groove #c0c0c0;
        padding-left: 10px;
        padding-top: 3px;
        padding-bottom: 3px;
        font-size: 16px; 
        font-weight: bold; 
        font-family: Courier New''')


class CheckBox(QCheckBox):
    def __init__(self, text: str):
        super().__init__(text)
        self.setStyleSheet('''
        color: #203764; 
        border: 1px groove #c0c0c0;
        padding-left: 10px;
        padding-top: 3px;
        padding-bottom: 3px;
        font-size: 16px; 
        font-weight: bold; 
        font-family: Courier New''')


class ProgressBar(QWidget):
    def __init__(self, parent=None, fixed_height=30):
        super().__init__(parent)
        self.match_percent = 0
        self.miss_percent = 0
        self.remain_percent = 100
        self.text = ''
        self.setFixedHeight(fixed_height)

    def set_values(self, match: int, miss: int, total: int, text: str):
        """Set values in percent"""
        self.match_percent = (match / total) * 100 if total > 0 else 0
        self.miss_percent = (miss / total) * 100 if total > 0 else 0
        self.remain_percent = 100 - self.match_percent - self.miss_percent
        self.text = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        match_width = int(width * self.match_percent / 100)
        miss_width = int(width * self.miss_percent / 100)
        remain_width = width - match_width - miss_width

        painter.fillRect(0, 0, match_width, height, QColor('green'))
        painter.fillRect(match_width, 0, miss_width, height, QColor('red'))
        painter.fillRect(match_width + miss_width, 0, remain_width, height, QColor('gray'))

        border_width = 2
        painter.setPen(QPen(QColor("black"), border_width))
        painter.drawRect(
            border_width // 2,
            border_width // 2,
            width - border_width,
            height - border_width
        )

        # borders between segments
        if self.match_percent > 0 or self.miss_percent > 0:
            painter.setPen(QColor('black'))
            painter.drawLine(match_width, 0, match_width, height)
            painter.drawLine(match_width + miss_width, 0, match_width + miss_width, height)

        # Adjust text to center
        painter.setPen(QColor('white'))
        painter.setFont(self.font())
        text_rect = self.rect().adjusted(5, 0, -5, 0)  # paddings
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text)


class Window(QWidget):
    def __init__(self, text: str, width=300, height=300):
        super().__init__()
        self.setMinimumSize(width, height)
        self.setWindowTitle(text)
        # screen = QApplication.primaryScreen().size()
        # self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)
        self.setWindowIcon(QIcon('images/chilli.ico'))


def change_style(widget, parameter: str, value: str):
    style = widget.styleSheet()
    pattern = rf'([^-]?\b{parameter}:[ ]?)([#]?\b\w+\b)'
    if re.search(pattern, style):
        widget.setStyleSheet(re.sub(pattern, rf'\1{value}', style))
