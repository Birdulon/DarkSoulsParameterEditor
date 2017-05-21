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
filename = "DarkSoulsDump.m0000"

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
        def mks(pattern, **kwargs):
            return make_strings(MEM, b'\x00\x00\x01\x00' + pattern + b'\x01\x00\x00\x00', **kwargs)

        string_lists = {
            'Goods Names':         mks(b'\x60\x2F\x00\x00'),
            'Weapon Names':        mks(b'\xF0\xD7\x06\x00'),
            'Protector Names':     mks(b'\x24\x14\x01\x00'),
            'Acc. Names':          mks(b'\xC8\x07\x00\x00'),
            'Magic Names':         mks(b'\x2C\x10\x00\x00'),
            'NPC Names':           mks(b'\x2C\x07\x00\x00'),
            'Game Area Names':     mks(b'\x5C\x08\x00\x00'),
            'Tooltips':            mks(b'\xB4\x4B\x00\x00'),
            'Weapon Types':        mks(b'\xC8\xAA\x00\x00'),
            'Acc. Tooltips':       mks(b'\x14\x0B\x00\x00'),
            'Goods Desc.':         mks(b'\xEC\xAD\x01\x00', MAX_LEN=1024),
            'Weapon Desc.':        mks(b'\x00\x4A\x09\x00', MAX_LEN=1024),
            'Protector Desc.':     mks(b'\x88\x7E\x01\x00', MAX_LEN=1024),
            'Acc. Desc.':          mks(b'\x6C\x48\x00\x00', MAX_LEN=1024),
            'Magic Tooltips':      mks(b'\x1C\x19\x00\x00', MAX_LEN=1024),
            'Magic Desc.':         mks(b'\xB0\x7A\x00\x00', MAX_LEN=1024),  # Missing in old memdump
            'Subtitles':           mks(b'\xDC\xC8\x03\x00', MAX_LEN=1024),
            'Signs':               mks(b'\x60\x35\x00\x00', MAX_LEN=1024),
            'Intro Subs':          mks(b'\xCC\x0B\x00\x00', MAX_LEN=1024),
            'UI Messages':         mks(b'\x48\x6B\x00\x00', MAX_LEN=1024),
            'UI Labels':           mks(b'\xF4\x07\x00\x00', MAX_LEN=1024),
            'Misc. Tooltips':      mks(b'\xA0\x89\x00\x00', MAX_LEN=1024),  # Missing in old memdump
            'Character Creation':  mks(b'\x60\x56\x00\x00', MAX_LEN=1024),
            'UI Messages 2':       mks(b'\x80\x27\x00\x00', MAX_LEN=1024),
            'unk':                 mks(b'\x04\x47\x00\x00', MAX_LEN=1024),
            'UI Labels 2':         mks(b'\x6C\x17\x00\x00', MAX_LEN=1024),
            'Moon':                mks(b'\xD4\x0C\x00\x00', MAX_LEN=1024),
            'unk1':                mks(b'\xE8\x02\x00\x00', MAX_LEN=1024),
            'unk2':                mks(b'\x10\x01\x00\x00', MAX_LEN=1024),  # Missing in old memdump
            'Main Menu':           mks(b'\xC0\x49\x00\x00', MAX_LEN=1024),  # Missing in old memdump
            'Goods Desc.':         mks(b'\xEC\x48\x00\x00', MAX_LEN=1024),
            'Messages DLC':        mks(b'\xA0\x1C\x00\x00', MAX_LEN=1024),
            'unk3':                mks(b'\x84\x07\x00\x00', MAX_LEN=1024),  # Missing in old memdump
            'unk4':                mks(b'\xD8\x04\x00\x00', MAX_LEN=1024),
            'Subtitles DLC':       mks(b'\x24\x8E\x00\x00', MAX_LEN=1024),
            'Magic Desc. DLC':     mks(b'\xC0\x1B\x00\x00', MAX_LEN=1024),
            'Weapon Desc. DLC':    mks(b'\xCC\x76\x00\x00', MAX_LEN=1024),
            'DLC Arena':           mks(b'\x0C\x0A\x00\x00', MAX_LEN=1024),
            'Protector Desc. DLC': mks(b'\x84\x2F\x00\x00', MAX_LEN=1024),  # Missing in old memdump
            'Acc. Desc. DLC':      mks(b'\xCC\x03\x00\x00', MAX_LEN=1024),
            'Goods Tooltips DLC':  mks(b'\xF8\x04\x00\x00', MAX_LEN=1024),
            'Goods Names DLC':     mks(b'\xA0\x03\x00\x00', MAX_LEN=1024),
            'Acc. Tooltips DLC':   mks(b'\x94\x00\x00\x00', MAX_LEN=1024),
            'Acc. Names DLC':      mks(b'\x58\x00\x00\x00', MAX_LEN=1024),
            'Weapon Types DLC':    mks(b'\xC4\x12\x00\x00', MAX_LEN=1024),
            'Weapon Names DLC':    mks(b'\xC0\x39\x00\x00', MAX_LEN=1024),
            #'unk5':        mks(b'\xD4\x01\x00\x00', MAX_LEN=1024),  # Empty
            'Protector Names DLC': mks(b'\x78\x12\x00\x00', MAX_LEN=1024),
            'Magic Names DLC':     mks(b'\x18\x01\x00\x00', MAX_LEN=1024),
            'Boss Names DLC':      mks(b'\x2C\x01\x00\x00', MAX_LEN=1024),
            'Game Area Names DLC': mks(b'\x4C\x03\x00\x00', MAX_LEN=1024),
            'unk6':                mks(b'\x54\x07\x00\x00', MAX_LEN=1024),
            'unk7':                mks(b'\xA0\x07\x00\x00', MAX_LEN=1024),  # Missing in old memdump
            'unk8':                mks(b'\x60\x07\x00\x00', MAX_LEN=1024),  # Missing in old memdump
        }
        weapon_names = {k: v for (k, o, v) in string_lists['Weapon Names'] + string_lists['Weapon Names DLC']}

        weapons = make_weapons(MEM)
        param_lists = {}
        for k, v in structs.structs.items():
            try:
                param_lists[k] = make_struct(MEM, k, v)
            except BaseException as e:
                print(e)

        str_headers = ['ID', 'Offset', 'String']

        self.tabwidget = QTabWidget()
        structs_tab = QTabWidget()
        strings_tab = QTabWidget()
        editor_tab = QTabWidget()
        self.tabwidget.addTab(structs_tab, "Structs")
        self.tabwidget.addTab(strings_tab, "Strings")
        #self.tabwidget.addTab(editor_tab, "Editors")

        structs_tab.addTab(make_param_table(weapons, IDs=weapon_names), "Weapons")
        for name, lst in sorted(param_lists.items()):
            structs_tab.addTab(make_param_table(lst), name)
        for name, lst in sorted(string_lists.items()):
            strings_tab.addTab(make_table(str_headers, lst), name)

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
    (u?)int16 holds number of entries
    After that, "EQUIP_PARAM_WEAPON_ST" in UTF-8
    14 bytes after null terminator, ID of first entry (uint32) followed by offset to struct (uint32) and 4 unk bytes (old name id?)
    repeat 12 byte struct for all entries
    """
    idx = memory.find("EQUIP_PARAM_WEAPON_ST".encode('utf_8'))
    if idx < 0:
        raise ValueError('Weapon params not found.')
    num_structs = int.from_bytes(memory[idx-2:idx], 'little')
    start = idx + 0x24
    off_start = start + 12*num_structs
    size = ctypes.sizeof(structs.EQUIP_PARAM_WEAPON_ST)
    ids = []
    for i in range(start, start+(12*num_structs), 12):
        ids.append(struct.unpack('III', memory[i:i+12]))
    params = []
    for i in range(off_start, off_start+(size*num_structs), size):
        params.append(structs.EQUIP_PARAM_WEAPON_ST.from_buffer_copy(memory[i:i+size]))
    return list(zip(ids, params))


def make_struct(memory, string, cls):
    """
    Try same as weapon param structs
    """
    idx = memory.find(string.encode('utf_8'))
    if idx < 0:
        raise ValueError(string+' Params not found.')
    num_structs = int.from_bytes(memory[idx-2:idx], 'little')
    start = idx + 0x24
    off_start = start + 12*num_structs
    size = ctypes.sizeof(cls)
    ids = []
    for i in range(start, start+(12*num_structs), 12):
        ids.append(struct.unpack('III', memory[i:i+12]))
    params = []
    for i in range(off_start, off_start+(size*num_structs), size):
        params.append(cls.from_buffer_copy(memory[i:i+size]))
    return list(zip(ids, params))


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


INT_TYPES = (
    int,
    ctypes.c_int8,
    ctypes.c_int16,
    ctypes.c_int32,
    ctypes.c_int64,
    ctypes.c_uint8,
    ctypes.c_uint16,
    ctypes.c_uint32,
    ctypes.c_uint64,
    )


def make_param_table(items, IDs=None, sortable=True, row_labels=True, scale=2):
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
            q_item = QTableWidgetItem()
            q_item.setData(QtCore.Qt.DisplayRole, val)
            table.setItem(row, col, q_item)
        if IDs:
            table.setItem(row, 3, QTableWidgetItem(str(IDs.get(item[0][0], ''))))
        for col, value in [(i+reserved_cols, getattr(item[1], fields[i])) for i in range(len(fields))]:
            if isinstance(value, QPixmap):
                lab = QLabel()
                lab.setPixmap(value.scaled(value.size() * scale))
                table.setCellWidget(row, col, lab)
            elif isinstance(value, (float, ctypes.c_float)):
                #q_item = QTableWidgetItem("{0:.2f}".format(value))
                q_item = QTableWidgetItem()
                q_item.setData(QtCore.Qt.DisplayRole, float(value))
                table.setItem(row, col, q_item)
            elif isinstance(value, INT_TYPES):
                q_item = QTableWidgetItem()
                q_item.setData(QtCore.Qt.DisplayRole, int(value))
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
