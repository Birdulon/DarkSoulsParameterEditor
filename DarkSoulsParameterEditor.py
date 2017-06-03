'''
Documentation, License etc.

@package DarkSoulsParameterEditor
'''

import sys
import os
import ctypes
import struct
import re
import itertools

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
            QAbstractItemView, QHeaderView,
            QListWidget, QListWidgetItem,
            QTableWidget, QTableWidgetItem,
            QTreeWidget, QTreeWidgetItem,
            QFrame, QScrollArea, QTabWidget,
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
            QAbstractItemView, QHeaderView,
            QListWidget, QListWidgetItem,
            QTableWidget, QTableWidgetItem,
            QTreeWidget, QTreeWidgetItem,
            QFrame, QScrollArea, QTabWidget,
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

"""
We use some magic numbers to find the string data.
Horribly crude but it does the job.
"""
STRING_LIST_KEYS = {
    b'\x60\x2F\x00': 'Goods Names',
    b'\xF0\xD7\x06': 'Weapon Names',
    b'\x24\x14\x01': 'Protector Names',
    b'\xC8\x07\x00': 'Acc. Names',
    b'\x2C\x10\x00': 'Magic Names',
    b'\x2C\x07\x00': 'NPC Names',
    b'\x5C\x08\x00': 'Game Area Names',
    b'\xB4\x4B\x00': 'Tooltips',
    b'\xC8\xAA\x00': 'Weapon Types',
    b'\x14\x0B\x00': 'Acc. Tooltips',
    b'\xEC\xAD\x01': 'Goods Desc.',
    b'\x00\x4A\x09': 'Weapon Desc.',
    b'\x88\x7E\x01': 'Protector Desc.',
    b'\x6C\x48\x00': 'Acc. Desc.',
    b'\x1C\x19\x00': 'Magic Tooltips',
    b'\xB0\x7A\x00': 'Magic Desc.',          # Missing in old memdump
    b'\xDC\xC8\x03': 'Subtitles',
    b'\x60\x35\x00': 'Signs',
    b'\xCC\x0B\x00': 'Intro Subs',
    b'\x48\x6B\x00': 'UI Messages',
    b'\xF4\x07\x00': 'UI Labels',
    b'\xA0\x89\x00': 'Misc. Tooltips',       # Missing in old memdump
    b'\x60\x56\x00': 'Character Creation',
    b'\x80\x27\x00': 'UI Messages 2',
    b'\x04\x47\x00': 'unk',
    b'\x6C\x17\x00': 'UI Labels 2',
    b'\xD4\x0C\x00': 'Moon',
    b'\xE8\x02\x00': 'unk1',
    b'\x10\x01\x00': 'unk2',                 # Missing in old memdump
    b'\xC0\x49\x00': 'Main Menu',            # Missing in old memdump
    b'\xEC\x48\x00': 'Goods Desc.',
    b'\xA0\x1C\x00': 'Messages DLC',
    b'\x84\x07\x00': 'unk3',                 # Missing in old memdump
    b'\xD8\x04\x00': 'unk4',
    b'\x24\x8E\x00': 'Subtitles DLC',
    b'\xC0\x1B\x00': 'Magic Desc. DLC',
    b'\xCC\x76\x00': 'Weapon Desc. DLC',
    b'\x0C\x0A\x00': 'DLC Arena',
    b'\x84\x2F\x00': 'Protector Desc. DLC',  # Missing in old memdump
    b'\xCC\x03\x00': 'Acc. Desc. DLC',
    b'\xF8\x04\x00': 'Goods Tooltips DLC',
    b'\xA0\x03\x00': 'Goods Names DLC',
    b'\x94\x00\x00': 'Acc. Tooltips DLC',
    b'\x58\x00\x00': 'Acc. Names DLC',
    b'\xC4\x12\x00': 'Weapon Types DLC',
    b'\xC0\x39\x00': 'Weapon Names DLC',
    #'unk5':        mks(b'\xD4\x01\x00', MAX_LEN=1024),  # Empty
    b'\x78\x12\x00': 'Protector Names DLC',
    b'\x18\x01\x00': 'Magic Names DLC',
    b'\x2C\x01\x00': 'Boss Names DLC',
    b'\x4C\x03\x00': 'Game Area Names DLC',
    b'\x54\x07\x00': 'unk6',
    b'\xA0\x07\x00': 'unk7',                 # Missing in old memdump
    b'\x60\x07\x00': 'unk8',                 # Missing in old memdump
}


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
        self.setWindowTitle("Dark Souls Parameter Editor")

        file1 = open(filename, 'rb')
        MEM = file1.read()
        MEMv = memoryview(MEM)

        strings_re = re.compile(b"\x00\x00\x01\x00(...)\x00\x01\x00\x00\x00")
        string_lists = {}
        i = 0
        while i < len(MEMv)-16:
            match = strings_re.search(MEMv[i:])
            if not match:
                break
            print('Strings match at 0x{:07x}'.format(match.start()+i))
            if match.group(1) in STRING_LIST_KEYS:
                result = make_strings(MEMv[i+match.start():])
                string_lists[STRING_LIST_KEYS[match.group(1)]] = result[0]
                i += result[1] + match.start()
                print(result[1])
            else:
                i += match.end() + 2
        print('String matches done')

        #weapon_names = {k: v for (k, o, v) in itertools.chain(string_lists['Weapon Names'], string_lists['Weapon Names DLC'])}

        #weapons = make_struct(MEMv, 'EQUIP_PARAM_WEAPON_ST', structs.EQUIP_PARAM_WEAPON_ST)
        param_lists = {}
        params_re = re.compile(b'|'.join(structs.structs.keys()))
        print(params_re)
        i = 0
        while i < len(MEMv)-64:
            match = params_re.search(MEMv[i:])
            if not match:
                break
            print('Structs match at 0x{:07x} - {}'.format(match.start()+i, match.group(0)))
            result = make_struct(MEMv[i+match.start()-2:], structs.structs[match.group(0)])
            key = str(match.group(0), 'utf8').rstrip('\x00 ')
            if key in param_lists:
                param_lists[key] += [result[0]]
            else:
                param_lists[key] = [result[0]]
            i += match.start() + result[1] - 2
            print(result[1])
        print('Struct matches done')

        str_headers = ['ID', 'Offset', 'String']

        self.tabwidget = QTabWidget()
        structs_tab = TreeWidgetSingle()
        strings_tab = TreeWidgetSingle()
        editor_tab = TreeWidgetSingle()
        self.tabwidget.addTab(structs_tab, "Structs")
        self.tabwidget.addTab(strings_tab, "Strings")
        #self.tabwidget.addTab(editor_tab, "Editors")

        self.stackedwidget = QStackedWidget()

        def switch_widget(item, col):
            if item:
                self.stackedwidget.setCurrentIndex(item.data(col, QtCore.Qt.UserRole))

        structs_tab.itemActivated.connect(switch_widget)
        strings_tab.itemActivated.connect(switch_widget)
        editor_tab.itemActivated.connect(switch_widget)

        #structs_tab.addTab(make_param_table(weapons, IDs=weapon_names), "Weapons")
        for name, lst in sorted(param_lists.items()):
            if len(lst) > 1:
                folder = QTreeWidgetItem([name])
                structs_tab.addTopLevelItem(folder)
                for i, sub in enumerate(lst):
                    #index = self.stackedwidget.addWidget(make_param_table(sub))
                    index = self.stackedwidget.addWidget(DeferredTable(sub))
                    widget = QTreeWidgetItem([str(i)])
                    widget.setData(0, QtCore.Qt.UserRole, index)
                    folder.addChild(widget)
            else:
                #index = self.stackedwidget.addWidget(make_param_table(lst[0]))
                index = self.stackedwidget.addWidget(DeferredTable(lst[0]))
                widget = QTreeWidgetItem([name])
                widget.setData(0, QtCore.Qt.UserRole, index)
                structs_tab.addTopLevelItem(widget)
        for name, lst in sorted(string_lists.items()):
            index = self.stackedwidget.addWidget(make_table(str_headers, lst))
            widget = QTreeWidgetItem([name])
            widget.setData(0, QtCore.Qt.UserRole, index)
            strings_tab.addTopLevelItem(widget)

        layout = QHBoxLayout()
        layout.addWidget(self.tabwidget)
        layout.addWidget(self.stackedwidget)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        self.main_widget = QWidget(self)
        self.main_widget.setLayout(layout)
        self.main_widget.setMinimumSize(800, 600)
        self.setCentralWidget(self.main_widget)
        self.show()


def make_struct(memory, struct_type):
    """
    Try same as weapon param structs
    (u?)int16 holds number of entries
    After that, "EQUIP_PARAM_WEAPON_ST" in UTF-8
    14 bytes after null terminator, ID of first entry (uint32) followed by offset to struct (uint32) and 4 unk bytes (old name id?)
    repeat 12 byte struct for all entries
    """
    idx = 2
    num_structs = int.from_bytes(memory[idx-2:idx], 'little')
    start = idx + 0x24
    off_start = start + 12*num_structs
    size = ctypes.sizeof(struct_type)
    ids = []
    for i in range(start, start+(12*num_structs), 12):
        ids.append(struct.unpack('III', memory[i:i+12]))
    params = []
    end = off_start+(size*num_structs)
    for i in range(off_start, end, size):
        params.append(struct_type.from_buffer_copy(memory[i:i+size]))
    return zip(ids, params), end


def make_strings(memory, MAX_LEN=1024):
    idx = 0  # Start of the memory passed is now the header
    end_max = 16
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
                end = i+2
                break
        strings.append(str(memory[s:end], 'utf_16_le'))
        end_max = max(end, end_max)
    return zip(IDs, str_offsets, strings), end_max


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
    if not isinstance(items, list):
        items = list(items)
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


class DeferredTable(QWidget):
    """
    Generate a table only when shown
    """
    def __init__(self, *args):
        super().__init__()
        self.generate_args = args

    def make_table(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(make_param_table(*self.generate_args))
        self.setLayout(layout)
        self.generate_args = False

    def showEvent(self, event):
        super().showEvent(event)
        if self.generate_args:
            self.make_table()


def make_param_table(items, IDs=None, sortable=True, row_labels=True, scale=2):
    """
    Helper function to tabulate 2d lists
    """
    if not isinstance(items, list):
        items = list(items)
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
    for i, title in enumerate(headers):
        if title[:3] == 'pad' or title[:7] == 'reserve':
            table.setColumnHidden(i, True)
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


def TreeWidgetSingle():
    widget = QTreeWidget()
    widget.setColumnCount(1)
    if pyqt_version == 4:
        widget.header().setResizeMode(QHeaderView.ResizeToContents)
    else:
        widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
    widget.header().setStretchLastSection(False)
    widget.header().close()
    return widget


def main():
    app = QApplication(sys.argv)
    mainwindow = DarkSoulsParameterEditor()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
