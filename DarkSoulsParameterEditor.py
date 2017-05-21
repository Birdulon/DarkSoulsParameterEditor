'''
Documentation, License etc.

@package DarkSoulsParameterEditor
'''

import sys
import os
import ctypes
import struct

import structs


pyqt_version = 0
skip_pyqt5 = "PYQT4" in os.environ
filename = "DaS memory.m0000"

if not skip_pyqt5:
    try:
        from PyQt5 import QtGui, QtCore
        from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QFontInfo, QImage, QPixmap
        from PyQt5.QtWidgets import (
            QApplication, QMainWindow, QFormLayout,
            QGridLayout, QHBoxLayout, QVBoxLayout,
            QAbstractItemView, QHeaderView, QListWidget,
            QListWidgetItem, QTabWidget, QTableWidget,
            QTableWidgetItem, QFrame, QScrollArea,
            QStackedWidget, QWidget, QCheckBox, QComboBox,
            QDoubleSpinBox, QGroupBox, QLineEdit,
            QPushButton, QRadioButton, QSpinBox,
            QStyleOptionButton, QToolButton, QProgressBar,
            QDialog, QColorDialog, QDialogButtonBox,
            QFileDialog, QInputDialog, QMessageBox,
            QAction, QActionGroup, QLabel, QMenu, QStyle,
            QSystemTrayIcon, QStyleOptionProgressBar
        )
        pyqt_version = 5
    except ImportError:
        print("Couldn't import Qt5 dependencies. "
              "Make sure you installed the PyQt5 package.")
if pyqt_version == 0:
    try:
        import sip
        sip.setapi('QVariant', 2)
        from PyQt4 import QtGui, QtCore
        from PyQt4.QtGui import (
            QApplication, QMainWindow, QFormLayout,
            QGridLayout, QHBoxLayout, QVBoxLayout,
            QAbstractItemView, QHeaderView, QListWidget,
            QListWidgetItem, QTabWidget, QTableWidget,
            QTableWidgetItem, QFrame, QScrollArea,
            QStackedWidget, QWidget, QCheckBox,
            QComboBox, QDoubleSpinBox, QGroupBox,
            QLineEdit, QPushButton, QRadioButton,
            QSpinBox, QStyleOptionButton, QToolButton,
            QProgressBar, QDialog, QColorDialog,
            QDialogButtonBox, QFileDialog, QInputDialog,
            QMessageBox, QAction, QActionGroup,
            QLabel, QMenu, QStyle,
            QSystemTrayIcon, QIcon, QPalette, QColor,
            QValidator, QFont, QFontInfo, QImage, QPixmap
        )
        from PyQt4.QtGui import QStyleOptionProgressBarV2 as QStyleOptionProgressBar
        pyqt_version = 4
    except ImportError:
        print("Couldn't import Qt dependencies. "
              "Make sure you installed the PyQt4 package.")
        sys.exit(-1)

monofont = QFont()
monofont.setStyleHint(QFont.Monospace)
if not monofont.fixedPitch():
    monofont.setStyleHint(QFont.TypeWriter)
if not monofont.fixedPitch():
    monofont.setFamily("Monospace")


class DarkSoulsParameterEditor(QMainWindow):
    """
    Main GUI class
    """
    def __init__(self):
        QMainWindow.__init__(self, None)

        with open(filename, 'rb') as file1:
            MEM = file1.read()

        #items = make_string_img_list(0x111380, 9, 256)
        #magics = make_string_img_list(0x111C80, 6, 87)
        weapons = make_weapons(MEM)
        wepnames = make_strings(MEM, b'\x00\x00\x01\x00\xF0\xD7\x06\x00\x01\x00\x00\x00')

        str_headers = ['ID', 'Offset', 'String']

        self.tabwidget = QTabWidget()
        structs_tab = QTabWidget()
        strings_tab = QTabWidget()
        editor_tab = QTabWidget()
        self.tabwidget.addTab(structs_tab, "Structs")
        self.tabwidget.addTab(strings_tab, "Strings")
        #self.tabwidget.addTab(editor_tab, "Images")

        #editor_tab.addTab(make_pixmap_table(glyph_sprites_en_small, scale=4), "Glyphs (EN)")
        #editor_tab.addTab(make_pixmap_table(glyph_sprites_en_large, scale=2), "Glyphs (Dialogue EN)")
        #editor_tab.addTab(make_pixmap_table(glyph_sprites_jp_small, scale=4), "Glyphs (JP)")
        #editor_tab.addTab(make_pixmap_table(glyph_sprites_jp_large, scale=2), "Glyphs (Large JP)")
        #editor_tab.addTab(make_pixmap_table(glyph_sprites_kanji, scale=2), "Glyphs (Kanji)")
        #editor_tab.addTab(make_pixmap_table(self.battle_strips, cols=22, scale=2), "Character Battle Sprites")
        #editor_tab.addTab(make_pixmap_table(status_strips, cols=22, scale=2), "Status Sprites")
        #editor_tab.addTab(make_pixmap_table(enemy_sprites, scale=1), "Enemy Sprites")

        structs_tab.addTab(make_param_table(weapons), "Weapons")
        strings_tab.addTab(make_table(str_headers, wepnames), "Weapon Names")

        layout = QHBoxLayout()
        layout.addWidget(self.tabwidget)
        self.main_widget = QWidget(self)
        self.main_widget.setLayout(layout)
        self.main_widget.setMinimumSize(800, 600)
        self.setCentralWidget(self.main_widget)
        self.show()


def make_weapons(memory):
    """
    Weapon param structs
    "EquipParamWeapon" in UTF-16
    42 bytes after that, (u?)int16 holds number of entries
    After that, "EQUIP_PARAM_WEAPON_ST" in UTF-8
    14 bytes after null terminator, ID of first entry (uint32) followed by offset to struct (uint32) and 4 unk bytes (name id?)
    repeat 12 byte struct for all entries
    """
    idx = memory.find("EquipParamWeapon".encode('utf_16_le'))
    if idx < 0:
        raise ValueError('Weapon params not found.')
    num_structs = int.from_bytes(memory[idx+74:idx+76], 'little')
    start = idx + 112
    size = ctypes.sizeof(structs.EQUIP_PARAM_WEAPON_ST)
    ids = []
    for i in range(start, start+(12*num_structs), 12):
        ids.append(struct.unpack('III', memory[i:i+12]))
    start = i + 12
    params = []
    for i in range(start, start+(size*num_structs), size):
        params.append(structs.EQUIP_PARAM_WEAPON_ST.from_buffer_copy(memory[i:i+size]))

    weapons = [(ids[i], params[i]) for i in range(num_structs)]
    return weapons


def make_strings(memory, header):
    MAX_LEN = 64
    idx = memory.find(header)
    if idx < 0:
        raise ValueError('Header not found.')
    num_blocks = int.from_bytes(memory[idx+12:idx+16], 'little')
    IDs = []
    start = idx + 28
    off_start = start + 12 * num_blocks
    for i in range(start, off_start, 12):
        st_offset, st_ID, end_ID = struct.unpack('III', memory[i:i+12])
        IDs += range(st_ID, end_ID+1)
    str_offsets = []
    for i in range(off_start, off_start+(len(IDs)*4), 4):
        str_offsets.append(int.from_bytes(memory[i:i+4], 'little'))
    strings = []
    for off in str_offsets:
        s = idx + off
        end = s+2
        for i in range(s, s+MAX_LEN*2, 2):
            if int.from_bytes(memory[i:i+2], 'little') == 0:
                end = i
                break
        strings.append(memory[s:end].decode('utf_16_le'))
    return list(zip(IDs, str_offsets, strings))


def divceil(numerator, denominator):
    # Reverse floor division for ceil
    return -(-numerator // denominator)


def hex_length(i):
    return divceil(i.bit_length(), 4)


def table_size_to_contents(table):
    # Stupid hack to get table to size correctly
    table.hide()
    geometry = table.viewport().geometry()
    table.viewport().setGeometry(QtCore.QRect(0, 0, 0x7FFFFFFF, 0x7FFFFFFF))
    table.resizeColumnsToContents()
    table.resizeRowsToContents()
    table.viewport().setGeometry(geometry)
    table.show()


def make_table(headers, items, sortable=False, row_labels=True, scale=2):
    """
    Helper function to tabulate 2d lists
    """
    cols = len(headers)
    rows = len(items)
    rd = hex_length(rows-1)
    table = QTableWidget(rows, cols)
    if row_labels:
        table.setVerticalHeaderLabels(['0x{:0{}X}'.format(v, rd) for v in range(rows)])
    else:
        table.verticalHeader().setVisible(False)
    table.setHorizontalHeaderLabels(headers)
    for row, col, item in [(x, y, items[x][y]) for x in range(rows) for y in range(cols)]:
        if isinstance(item, QPixmap):
            lab = QLabel()
            lab.setPixmap(item.scaled(item.size() * scale))
            table.setCellWidget(row, col, lab)
        elif item is not None:
            if not isinstance(item, str):
                item = str(item)
            q_item = QTableWidgetItem(item)
            if item[:2] == "0x":
                q_item.setFont(monofont)
            table.setItem(row, col, q_item)
    table_size_to_contents(table)
    if sortable:
        table.setSortingEnabled(True)
        table.sortItems(0)
    return table


def make_param_table(items, sortable=False, row_labels=True, scale=2):
    """
    Helper function to tabulate 2d lists
    """
    fields = [f[0] for f in items[0][1]._fields_]
    headers = ['ID'] + fields
    cols = len(headers)
    rows = len(items)
    rd = hex_length(rows-1)
    table = QTableWidget(rows, cols)
    if row_labels:
        table.setVerticalHeaderLabels(['0x{:0{}X}'.format(v, rd) for v in range(rows)])
    else:
        table.verticalHeader().setVisible(False)
    table.setHorizontalHeaderLabels(headers)
    for row, item in enumerate(items):
        table.setItem(row, 0, QTableWidgetItem(str(item[0])))
        for col, value in [(i+1, getattr(item[1], fields[i])) for i in range(len(fields))]:
            if isinstance(value, QPixmap):
                lab = QLabel()
                lab.setPixmap(value.scaled(value.size() * scale))
                table.setCellWidget(row, col, lab)
            elif value is not None:
                q_item = QTableWidgetItem(str(value))
                #if item[:2] == "0x":
                    #q_item.setFont(monofont)
                table.setItem(row, col, q_item)
    table_size_to_contents(table)
    if sortable:
        table.setSortingEnabled(True)
        table.sortItems(0)
    return table

def main():
    app = QApplication(sys.argv)
    mainwindow = DarkSoulsParameterEditor()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
