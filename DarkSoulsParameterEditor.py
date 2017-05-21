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
        """
        We use some magic numbers here to find the string data.
        Horribly crude but it does the job.
        """
        itemnames_list = make_strings(MEM, b'\x00\x00\x01\x00\x60\x2F\x00\x00\x01\x00\x00\x00')
        item_names = {k: v for (k, o, v) in itemnames_list}
        wepnames_list = make_strings(MEM, b'\x00\x00\x01\x00\xF0\xD7\x06\x00\x01\x00\x00\x00')
        weapon_names = {k: v for (k, o, v) in wepnames_list}
        protnames_list = make_strings(MEM, b'\x00\x00\x01\x00\x24\x14\x01\x00\x01\x00\x00\x00')
        protector_names = {k: v for (k, o, v) in protnames_list}
        accnames_list = make_strings(MEM, b'\x00\x00\x01\x00\xC8\x07\x00\x00\x01\x00\x00\x00')
        accessory_names = {k: v for (k, o, v) in accnames_list}
        magicnames_list = make_strings(MEM, b'\x00\x00\x01\x00\x2C\x10\x00\x00\x01\x00\x00\x00')
        magic_names = {k: v for (k, o, v) in magicnames_list}
        npcnames_list = make_strings(MEM, b'\x00\x00\x01\x00\x2C\x07\x00\x00\x01\x00\x00\x00')
        npc_names = {k: v for (k, o, v) in npcnames_list}
        zonenames_list = make_strings(MEM, b'\x00\x00\x01\x00\x5C\x08\x00\x00\x01\x00\x00\x00')
        zone_names = {k: v for (k, o, v) in zonenames_list}
        tooltips_list = make_strings(MEM, b'\x00\x00\x01\x00\xB4\x4B\x00\x00\x01\x00\x00\x00')
        weptypes_list = make_strings(MEM, b'\x00\x00\x01\x00\xC8\xAA\x00\x00\x01\x00\x00\x00')
        acctips_list = make_strings(MEM, b'\x00\x00\x01\x00\x14\x0B\x00\x00\x01\x00\x00\x00')
        more_lists = [
            make_strings(MEM, b'\x00\x00\x01\x00\xEC\xAD\x01\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x00\x4A\x09\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x88\x7E\x01\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x6C\x48\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x1C\x19\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            #make_strings(MEM, b'\x00\x00\x01\x00\xB0\x7A\x00\x00\x01\x00\x00\x00', MAX_LEN=1024), # Missing in old memdump
            make_strings(MEM, b'\x00\x00\x01\x00\xDC\xC8\x03\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x60\x35\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xCC\x0B\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x48\x6B\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xF4\x07\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            #make_strings(MEM, b'\x00\x00\x01\x00\xA0\x89\x00\x00\x01\x00\x00\x00', MAX_LEN=1024), # Missing in old memdump
            make_strings(MEM, b'\x00\x00\x01\x00\x60\x56\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x80\x27\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x04\x47\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x6C\x17\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xD4\x0C\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xE8\x02\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            #make_strings(MEM, b'\x00\x00\x01\x00\x10\x01\x00\x00\x01\x00\x00\x00', MAX_LEN=1024), # Missing in old memdump
            #make_strings(MEM, b'\x00\x00\x01\x00\xC0\x49\x00\x00\x01\x00\x00\x00', MAX_LEN=1024), # Missing in old memdump
            make_strings(MEM, b'\x00\x00\x01\x00\xEC\x48\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xA0\x1C\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            #make_strings(MEM, b'\x00\x00\x01\x00\x84\x07\x00\x00\x01\x00\x00\x00', MAX_LEN=1024), # Missing in old memdump
            make_strings(MEM, b'\x00\x00\x01\x00\xD8\x04\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x24\x8E\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xC0\x1B\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xCC\x76\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x0C\x0A\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            #make_strings(MEM, b'\x00\x00\x01\x00\x84\x2F\x00\x00\x01\x00\x00\x00', MAX_LEN=1024), # Missing in old memdump
            make_strings(MEM, b'\x00\x00\x01\x00\xCC\x03\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xF8\x04\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xA0\x03\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x94\x00\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x58\x00\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xC4\x12\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xC0\x39\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\xD4\x01\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x78\x12\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x18\x01\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x2C\x01\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x4C\x03\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            make_strings(MEM, b'\x00\x00\x01\x00\x54\x07\x00\x00\x01\x00\x00\x00', MAX_LEN=1024),
            #make_strings(MEM, b'\x00\x00\x01\x00\xA0\x07\x00\x00\x01\x00\x00\x00', MAX_LEN=1024), # Missing in old memdump
            #make_strings(MEM, b'\x00\x00\x01\x00\x60\x07\x00\x00\x01\x00\x00\x00', MAX_LEN=1024), # Missing in old memdump
        ]

        weapons = make_weapons(MEM)

        str_headers = ['ID', 'Offset', 'String']

        self.tabwidget = QTabWidget()
        structs_tab = QTabWidget()
        strings_tab = QTabWidget()
        editor_tab = QTabWidget()
        self.tabwidget.addTab(structs_tab, "Structs")
        self.tabwidget.addTab(strings_tab, "Strings")
        #self.tabwidget.addTab(editor_tab, "Editors")

        structs_tab.addTab(make_param_table(weapons, IDs=weapon_names), "Weapons")
        strings_tab.addTab(make_table(str_headers, itemnames_list), "Item Names")
        strings_tab.addTab(make_table(str_headers, wepnames_list), "Weapon Names")
        strings_tab.addTab(make_table(str_headers, protnames_list), "Protector Names")
        strings_tab.addTab(make_table(str_headers, accnames_list), "Accessory Names")
        strings_tab.addTab(make_table(str_headers, magicnames_list), "Magic Names")
        strings_tab.addTab(make_table(str_headers, npcnames_list), "NPC Names")
        strings_tab.addTab(make_table(str_headers, zonenames_list), "Zone Names")
        strings_tab.addTab(make_table(str_headers, tooltips_list), "Tooltips")
        strings_tab.addTab(make_table(str_headers, weptypes_list), "Weapon Types")
        strings_tab.addTab(make_table(str_headers, acctips_list), "Accessory Tooltips")
        for i, lst in enumerate(more_lists):
            strings_tab.addTab(make_table(str_headers, lst), str(i))

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


def make_strings(memory, header, MAX_LEN=64):
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


def make_param_table(items, IDs=None, sortable=False, row_labels=True, scale=2):
    """
    Helper function to tabulate 2d lists
    """
    fields = [f[0] for f in items[0][1]._fields_]
    id_header = ['ID', 'ST Offset', 'OldNameOffset']
    if IDs:
        id_header.append('Name')
    headers = id_header + fields
    reserved_cols = len(id_header)
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
        for col, val in enumerate(item[0]):
            table.setItem(row, col, QTableWidgetItem(str(val)))
        if IDs:
            table.setItem(row, 3, QTableWidgetItem(str(IDs.get(item[0][0], ''))))
        for col, value in [(i+reserved_cols, getattr(item[1], fields[i])) for i in range(len(fields))]:
            if isinstance(value, QPixmap):
                lab = QLabel()
                lab.setPixmap(value.scaled(value.size() * scale))
                table.setCellWidget(row, col, lab)
            elif isinstance(value, (float, ctypes.c_float)):
                q_item = QTableWidgetItem("{0:.2f}".format(value))
                table.setItem(row, col, q_item)
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
