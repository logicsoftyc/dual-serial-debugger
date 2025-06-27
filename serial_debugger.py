#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双串口调试器
版本: 1.0.0
构建时间: 2024-12-19 15:30:00
"""

import sys
import os
import json
import re
import time
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import serial
import serial.tools.list_ports

# 导入版本信息
try:
    from version_info import VERSION, BUILD_TIME
except ImportError:
    # 如果版本信息文件不存在，使用默认值
    VERSION = "1.0.0"
    BUILD_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

CONFIG_FILE = 'serial_debugger_config.json'

class SerialThread(QThread):
    """串口数据接收线程"""
    data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True
        
    def run(self):
        while self.running and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        # 发送接收到的原始字节数据
                        self.data_received.emit(data)
                time.sleep(0.01)  # 10ms延时
            except Exception as e:
                self.error_occurred.emit(f"串口读取错误: {str(e)}")
                break
                
    def stop(self):
        self.running = False

class SerialDebugger(QWidget):
    def __init__(self):
        super().__init__()
        # 串口1
        self.serial_port1 = None
        self.serial_thread1 = None
        self.received_count1 = 0
        self.sent_count1 = 0
        
        # 串口2
        self.serial_port2 = None
        self.serial_thread2 = None
        self.received_count2 = 0
        self.sent_count2 = 0
        
        # 自动发送定时器
        self.auto_send_timer1 = None
        self.auto_send_timer2 = None
        
        # 记忆自动换行状态
        self.newline_state1 = True  # 默认启用
        self.newline_state2 = True  # 默认启用
        
        # 发送历史记录
        self.send_history1_text = []    # 串口1文本发送历史
        self.send_history1_hex = []     # 串口1十六进制发送历史
        self.send_history2_text = []    # 串口2文本发送历史
        self.send_history2_hex = []     # 串口2十六进制发送历史
        self.max_history = 20           # 最大历史记录数量
        
        # 多条字符串功能
        self.quick_strings1 = []  # 串口1快速字符串
        self.quick_strings2 = []  # 串口2快速字符串
        
        # 初始化40个空词条
        for i in range(40):
            self.quick_strings1.append({"label": f"字符串{i+1}", "content": "", "hex": False})
            self.quick_strings2.append({"label": f"字符串{i+1}", "content": "", "hex": False})
        
        # 设置一些默认词条
        if len(self.quick_strings1) >= 4:
            self.quick_strings1[0] = {"label": "字符串1", "content": "Hello", "hex": False}
            self.quick_strings1[1] = {"label": "字符串2", "content": "World", "hex": False}
            self.quick_strings1[2] = {"label": "字符串3", "content": "48 65 6C 6C 6F", "hex": True}
            self.quick_strings1[3] = {"label": "字符串4", "content": "57 6F 72 6C 64", "hex": True}
        
        if len(self.quick_strings2) >= 4:
            self.quick_strings2[0] = {"label": "字符串1", "content": "Test1", "hex": False}
            self.quick_strings2[1] = {"label": "字符串2", "content": "Test2", "hex": False}
            self.quick_strings2[2] = {"label": "字符串3", "content": "AA BB CC", "hex": True}
            self.quick_strings2[3] = {"label": "字符串4", "content": "DD EE FF", "hex": True}
        
        self.quick_string_buttons1 = []        # 串口1快速发送按钮
        self.quick_string_buttons2 = []        # 串口2快速发送按钮
        
        self.init_ui()
        self.scan_ports()
        self.load_config()
        
        # 显示版本信息
        self.log_message(f"双串口调试器 v{VERSION} 启动成功", color='blue')
        self.log_message(f"构建时间: {BUILD_TIME}", color='blue')
        self.log_message(f"作者: logicsoft@qq.com", color='blue')
        self.log_message("支持从SSCOM.ini文件导入词条配置", color='blue')
        
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题
        self.setWindowTitle(f'双串口调试器 v{VERSION} - {BUILD_TIME} - logicsoft@qq.com')
        self.setGeometry(100, 100, 1200, 800)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 创建两个串口的标签页
        tab_widget = QTabWidget()
        
        # 串口1标签页
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        
        # 串口1设置组
        serial_group1 = QGroupBox('串口1设置')
        serial_layout1 = QGridLayout()
        
        # 串口选择
        serial_layout1.addWidget(QLabel('串口:'), 0, 0)
        self.combo_port1 = QComboBox()
        self.combo_port1.setMinimumWidth(150)
        serial_layout1.addWidget(self.combo_port1, 0, 1)
        
        # 刷新串口按钮
        self.btn_refresh1 = QPushButton('刷新串口')
        self.btn_refresh1.clicked.connect(self.scan_ports)
        serial_layout1.addWidget(self.btn_refresh1, 0, 2)
        
        # 连接按钮（与刷新按钮同一行）
        self.btn_connect1 = QPushButton('连接')
        self.btn_connect1.clicked.connect(lambda: self.toggle_connection(1))
        serial_layout1.addWidget(self.btn_connect1, 0, 3)
        
        # 导入SSCOM配置按钮
        self.btn_import_sscom1 = QPushButton('导入词条')
        self.btn_import_sscom1.clicked.connect(lambda: self.import_sscom_config(1))
        self.btn_import_sscom1.setMaximumWidth(80)
        self.btn_import_sscom1.setToolTip('从SSCOM.ini文件导入词条配置')
        serial_layout1.addWidget(self.btn_import_sscom1, 0, 4)
        
        # 波特率
        serial_layout1.addWidget(QLabel('波特率:'), 0, 5)
        self.combo_baud1 = QComboBox()
        self.combo_baud1.addItems(['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600'])
        self.combo_baud1.setCurrentText('115200')
        serial_layout1.addWidget(self.combo_baud1, 0, 6)
        
        # 数据位
        serial_layout1.addWidget(QLabel('数据位:'), 1, 0)
        self.combo_data1 = QComboBox()
        self.combo_data1.addItems(['5', '6', '7', '8'])
        self.combo_data1.setCurrentText('8')
        serial_layout1.addWidget(self.combo_data1, 1, 1)
        
        # 停止位
        serial_layout1.addWidget(QLabel('停止位:'), 1, 2)
        self.combo_stop1 = QComboBox()
        self.combo_stop1.addItems(['1', '1.5', '2'])
        self.combo_stop1.setCurrentText('1')
        serial_layout1.addWidget(self.combo_stop1, 1, 3)
        
        # 校验位
        serial_layout1.addWidget(QLabel('校验位:'), 1, 4)
        self.combo_parity1 = QComboBox()
        self.combo_parity1.addItems(['无', '奇校验', '偶校验'])
        self.combo_parity1.setCurrentText('无')
        serial_layout1.addWidget(self.combo_parity1, 1, 5)
        
        serial_group1.setLayout(serial_layout1)
        tab1_layout.addWidget(serial_group1)
        
        # 串口1发送组
        send_group1 = QGroupBox('串口1发送')
        send_layout1 = QVBoxLayout()
        
        # 发送输入
        send_input_layout1 = QHBoxLayout()
        send_input_layout1.addWidget(QLabel('发送数据:'))
        self.edit_send1 = QLineEdit()
        self.edit_send1.setPlaceholderText('输入要发送的数据')
        send_input_layout1.addWidget(self.edit_send1)
        
        # 添加历史记录下拉框
        self.combo_history1 = QComboBox()
        self.combo_history1.setMaximumWidth(150)
        self.combo_history1.setEditable(False)
        self.combo_history1.setToolTip('发送历史记录')
        self.combo_history1.currentTextChanged.connect(lambda text: self.on_history_selected(text, 1))
        send_input_layout1.addWidget(self.combo_history1)
        
        # 发送选项
        self.check_hex_send1 = QCheckBox('十六进制发送')
        self.check_hex_send1.toggled.connect(self.on_hex_send_toggled)
        send_input_layout1.addWidget(self.check_hex_send1)
        
        self.check_newline1 = QCheckBox('自动换行')
        self.check_newline1.setChecked(True)
        send_input_layout1.addWidget(self.check_newline1)
        
        # 添加发送编码选择
        send_input_layout1.addWidget(QLabel('编码:'))
        self.combo_send_encoding1 = QComboBox()
        self.combo_send_encoding1.addItems(['UTF-8', 'GBK', 'GB2312', 'BIG5', 'ISO-8859-1', 'ASCII'])
        self.combo_send_encoding1.setCurrentText('UTF-8')
        self.combo_send_encoding1.setMaximumWidth(100)
        send_input_layout1.addWidget(self.combo_send_encoding1)
        
        # 发送按钮
        self.btn_send1 = QPushButton('发送')
        self.btn_send1.clicked.connect(lambda: self.send_data(1))
        send_input_layout1.addWidget(self.btn_send1)
        
        send_layout1.addLayout(send_input_layout1)
        
        # 自动发送
        auto_send_layout1 = QHBoxLayout()
        auto_send_layout1.addWidget(QLabel('自动发送间隔(ms):'))
        self.spin_interval1 = QSpinBox()
        self.spin_interval1.setRange(100, 10000)
        self.spin_interval1.setValue(1000)
        auto_send_layout1.addWidget(self.spin_interval1)
        
        self.check_auto_send1 = QCheckBox('启用自动发送')
        auto_send_layout1.addWidget(self.check_auto_send1)
        self.check_auto_send1.toggled.connect(lambda enabled: self.toggle_auto_send(enabled, 1))
        
        send_layout1.addLayout(auto_send_layout1)
        
        # 快速字符串按钮组
        quick_strings_group1 = QGroupBox('快速字符串')
        quick_strings_layout1 = QVBoxLayout()  # 改为垂直布局
        
        # 第一行按钮
        quick_strings_row1 = QHBoxLayout()
        for i in range(20):
            btn = QPushButton(f'字符串{i+1}')
            btn.setMaximumWidth(80)
            btn.clicked.connect(lambda checked, idx=i, port=1: self.quick_send_string(idx, port))
            # 添加右键菜单
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, idx=i, port=1: self.show_quick_string_menu(pos, idx, port))
            self.quick_string_buttons1.append(btn)
            quick_strings_row1.addWidget(btn)
        
        quick_strings_row1.addStretch()
        quick_strings_layout1.addLayout(quick_strings_row1)
        
        # 第二行按钮
        quick_strings_row2 = QHBoxLayout()
        for i in range(20, 40):
            btn = QPushButton(f'字符串{i+1}')
            btn.setMaximumWidth(80)
            btn.clicked.connect(lambda checked, idx=i, port=1: self.quick_send_string(idx, port))
            # 添加右键菜单
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, idx=i, port=1: self.show_quick_string_menu(pos, idx, port))
            self.quick_string_buttons1.append(btn)
            quick_strings_row2.addWidget(btn)
        
        quick_strings_row2.addStretch()
        quick_strings_layout1.addLayout(quick_strings_row2)
        
        quick_strings_group1.setLayout(quick_strings_layout1)
        send_layout1.addWidget(quick_strings_group1)
        
        send_group1.setLayout(send_layout1)
        tab1_layout.addWidget(send_group1)
        
        # 串口1接收组
        receive_group1 = QGroupBox('串口1接收')
        receive_layout1 = QVBoxLayout()
        
        # 接收控制按钮
        receive_control_layout1 = QHBoxLayout()
        self.btn_clear1 = QPushButton('清除接收')
        self.btn_clear1.clicked.connect(lambda: self.clear_receive(1))
        receive_control_layout1.addWidget(self.btn_clear1)
        
        self.check_hex_display1 = QCheckBox('十六进制显示')
        self.check_hex_display1.toggled.connect(lambda: self.update_display_format(1))
        receive_control_layout1.addWidget(self.check_hex_display1)
        
        # 添加编码选择
        receive_control_layout1.addWidget(QLabel('编码:'))
        self.combo_encoding1 = QComboBox()
        self.combo_encoding1.addItems(['UTF-8', 'GBK', 'GB2312', 'BIG5', 'ISO-8859-1', 'ASCII'])
        self.combo_encoding1.setCurrentText('UTF-8')
        self.combo_encoding1.setMaximumWidth(100)
        receive_control_layout1.addWidget(self.combo_encoding1)
        
        self.check_show_time1 = QCheckBox('显示时间戳')
        self.check_show_time1.setChecked(True)
        receive_control_layout1.addWidget(self.check_show_time1)
        
        self.check_auto_scroll1 = QCheckBox('自动滚动')
        self.check_auto_scroll1.setChecked(True)
        receive_control_layout1.addWidget(self.check_auto_scroll1)
        
        receive_layout1.addLayout(receive_control_layout1)
        
        # 接收数据显示
        self.text_receive1 = QTextEdit()
        self.text_receive1.setReadOnly(True)
        self.text_receive1.setFont(QFont('Consolas', 10))
        receive_layout1.addWidget(self.text_receive1)
        
        # 统计信息
        stats_layout1 = QHBoxLayout()
        self.label_received1 = QLabel('接收: 0 字节')
        stats_layout1.addWidget(self.label_received1)
        self.label_sent1 = QLabel('发送: 0 字节')
        stats_layout1.addWidget(self.label_sent1)
        stats_layout1.addStretch()
        
        receive_layout1.addLayout(stats_layout1)
        receive_group1.setLayout(receive_layout1)
        tab1_layout.addWidget(receive_group1)
        
        tab1.setLayout(tab1_layout)
        tab_widget.addTab(tab1, "串口1")
        
        # 串口2标签页
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        
        # 串口2设置组
        serial_group2 = QGroupBox('串口2设置')
        serial_layout2 = QGridLayout()
        
        # 串口选择
        serial_layout2.addWidget(QLabel('串口:'), 0, 0)
        self.combo_port2 = QComboBox()
        self.combo_port2.setMinimumWidth(150)
        serial_layout2.addWidget(self.combo_port2, 0, 1)
        
        # 刷新串口按钮
        self.btn_refresh2 = QPushButton('刷新串口')
        self.btn_refresh2.clicked.connect(self.scan_ports)
        serial_layout2.addWidget(self.btn_refresh2, 0, 2)
        
        # 连接按钮（与刷新按钮同一行）
        self.btn_connect2 = QPushButton('连接')
        self.btn_connect2.clicked.connect(lambda: self.toggle_connection(2))
        serial_layout2.addWidget(self.btn_connect2, 0, 3)
        
        # 导入SSCOM配置按钮
        self.btn_import_sscom2 = QPushButton('导入词条')
        self.btn_import_sscom2.clicked.connect(lambda: self.import_sscom_config(2))
        self.btn_import_sscom2.setMaximumWidth(80)
        self.btn_import_sscom2.setToolTip('从SSCOM.ini文件导入词条配置')
        serial_layout2.addWidget(self.btn_import_sscom2, 0, 4)
        
        # 波特率
        serial_layout2.addWidget(QLabel('波特率:'), 0, 5)
        self.combo_baud2 = QComboBox()
        self.combo_baud2.addItems(['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600'])
        self.combo_baud2.setCurrentText('115200')
        serial_layout2.addWidget(self.combo_baud2, 0, 6)
        
        # 数据位
        serial_layout2.addWidget(QLabel('数据位:'), 1, 0)
        self.combo_data2 = QComboBox()
        self.combo_data2.addItems(['5', '6', '7', '8'])
        self.combo_data2.setCurrentText('8')
        serial_layout2.addWidget(self.combo_data2, 1, 1)
        
        # 停止位
        serial_layout2.addWidget(QLabel('停止位:'), 1, 2)
        self.combo_stop2 = QComboBox()
        self.combo_stop2.addItems(['1', '1.5', '2'])
        self.combo_stop2.setCurrentText('1')
        serial_layout2.addWidget(self.combo_stop2, 1, 3)
        
        # 校验位
        serial_layout2.addWidget(QLabel('校验位:'), 1, 4)
        self.combo_parity2 = QComboBox()
        self.combo_parity2.addItems(['无', '奇校验', '偶校验'])
        self.combo_parity2.setCurrentText('无')
        serial_layout2.addWidget(self.combo_parity2, 1, 5)
        
        serial_group2.setLayout(serial_layout2)
        tab2_layout.addWidget(serial_group2)
        
        # 串口2发送组
        send_group2 = QGroupBox('串口2发送')
        send_layout2 = QVBoxLayout()
        
        # 发送输入
        send_input_layout2 = QHBoxLayout()
        send_input_layout2.addWidget(QLabel('发送数据:'))
        self.edit_send2 = QLineEdit()
        self.edit_send2.setPlaceholderText('输入要发送的数据')
        send_input_layout2.addWidget(self.edit_send2)
        
        # 添加历史记录下拉框
        self.combo_history2 = QComboBox()
        self.combo_history2.setMaximumWidth(150)
        self.combo_history2.setEditable(False)
        self.combo_history2.setToolTip('发送历史记录')
        self.combo_history2.currentTextChanged.connect(lambda text: self.on_history_selected(text, 2))
        send_input_layout2.addWidget(self.combo_history2)
        
        # 发送选项
        self.check_hex_send2 = QCheckBox('十六进制发送')
        self.check_hex_send2.toggled.connect(self.on_hex_send_toggled)
        send_input_layout2.addWidget(self.check_hex_send2)
        
        self.check_newline2 = QCheckBox('自动换行')
        self.check_newline2.setChecked(True)
        send_input_layout2.addWidget(self.check_newline2)
        
        # 添加发送编码选择
        send_input_layout2.addWidget(QLabel('编码:'))
        self.combo_send_encoding2 = QComboBox()
        self.combo_send_encoding2.addItems(['UTF-8', 'GBK', 'GB2312', 'BIG5', 'ISO-8859-1', 'ASCII'])
        self.combo_send_encoding2.setCurrentText('UTF-8')
        self.combo_send_encoding2.setMaximumWidth(100)
        send_input_layout2.addWidget(self.combo_send_encoding2)
        
        # 发送按钮
        self.btn_send2 = QPushButton('发送')
        self.btn_send2.clicked.connect(lambda: self.send_data(2))
        send_input_layout2.addWidget(self.btn_send2)
        
        send_layout2.addLayout(send_input_layout2)
        
        # 自动发送
        auto_send_layout2 = QHBoxLayout()
        auto_send_layout2.addWidget(QLabel('自动发送间隔(ms):'))
        self.spin_interval2 = QSpinBox()
        self.spin_interval2.setRange(100, 10000)
        self.spin_interval2.setValue(1000)
        auto_send_layout2.addWidget(self.spin_interval2)
        
        self.check_auto_send2 = QCheckBox('启用自动发送')
        auto_send_layout2.addWidget(self.check_auto_send2)
        self.check_auto_send2.toggled.connect(lambda enabled: self.toggle_auto_send(enabled, 2))
        
        send_layout2.addLayout(auto_send_layout2)
        
        # 快速字符串按钮组
        quick_strings_group2 = QGroupBox('快速字符串')
        quick_strings_layout2 = QVBoxLayout()  # 改为垂直布局
        
        # 第一行按钮
        quick_strings_row1_2 = QHBoxLayout()
        for i in range(20):
            btn = QPushButton(f'字符串{i+1}')
            btn.setMaximumWidth(80)
            btn.clicked.connect(lambda checked, idx=i, port=2: self.quick_send_string(idx, port))
            # 添加右键菜单
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, idx=i, port=2: self.show_quick_string_menu(pos, idx, port))
            self.quick_string_buttons2.append(btn)
            quick_strings_row1_2.addWidget(btn)
        
        quick_strings_row1_2.addStretch()
        quick_strings_layout2.addLayout(quick_strings_row1_2)
        
        # 第二行按钮
        quick_strings_row2_2 = QHBoxLayout()
        for i in range(20, 40):
            btn = QPushButton(f'字符串{i+1}')
            btn.setMaximumWidth(80)
            btn.clicked.connect(lambda checked, idx=i, port=2: self.quick_send_string(idx, port))
            # 添加右键菜单
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, idx=i, port=2: self.show_quick_string_menu(pos, idx, port))
            self.quick_string_buttons2.append(btn)
            quick_strings_row2_2.addWidget(btn)
        
        quick_strings_row2_2.addStretch()
        quick_strings_layout2.addLayout(quick_strings_row2_2)
        
        quick_strings_group2.setLayout(quick_strings_layout2)
        send_layout2.addWidget(quick_strings_group2)
        
        send_group2.setLayout(send_layout2)
        tab2_layout.addWidget(send_group2)
        
        # 串口2接收组
        receive_group2 = QGroupBox('串口2接收')
        receive_layout2 = QVBoxLayout()
        
        # 接收控制按钮
        receive_control_layout2 = QHBoxLayout()
        self.btn_clear2 = QPushButton('清除接收')
        self.btn_clear2.clicked.connect(lambda: self.clear_receive(2))
        receive_control_layout2.addWidget(self.btn_clear2)
        
        self.check_hex_display2 = QCheckBox('十六进制显示')
        self.check_hex_display2.toggled.connect(lambda: self.update_display_format(2))
        receive_control_layout2.addWidget(self.check_hex_display2)
        
        # 添加编码选择
        receive_control_layout2.addWidget(QLabel('编码:'))
        self.combo_encoding2 = QComboBox()
        self.combo_encoding2.addItems(['UTF-8', 'GBK', 'GB2312', 'BIG5', 'ISO-8859-1', 'ASCII'])
        self.combo_encoding2.setCurrentText('UTF-8')
        self.combo_encoding2.setMaximumWidth(100)
        receive_control_layout2.addWidget(self.combo_encoding2)
        
        self.check_show_time2 = QCheckBox('显示时间戳')
        self.check_show_time2.setChecked(True)
        receive_control_layout2.addWidget(self.check_show_time2)
        
        self.check_auto_scroll2 = QCheckBox('自动滚动')
        self.check_auto_scroll2.setChecked(True)
        receive_control_layout2.addWidget(self.check_auto_scroll2)
        
        receive_layout2.addLayout(receive_control_layout2)
        
        # 接收数据显示
        self.text_receive2 = QTextEdit()
        self.text_receive2.setReadOnly(True)
        self.text_receive2.setFont(QFont('Consolas', 10))
        receive_layout2.addWidget(self.text_receive2)
        
        # 统计信息
        stats_layout2 = QHBoxLayout()
        self.label_received2 = QLabel('接收: 0 字节')
        stats_layout2.addWidget(self.label_received2)
        self.label_sent2 = QLabel('发送: 0 字节')
        stats_layout2.addWidget(self.label_sent2)
        stats_layout2.addStretch()
        
        receive_layout2.addLayout(stats_layout2)
        receive_group2.setLayout(receive_layout2)
        tab2_layout.addWidget(receive_group2)
        
        tab2.setLayout(tab2_layout)
        tab_widget.addTab(tab2, "串口2")
        
        main_layout.addWidget(tab_widget)
        
        # 日志区域
        log_group = QGroupBox('程序日志')
        log_layout = QVBoxLayout()
        
        # 日志控制按钮
        log_control_layout = QHBoxLayout()
        
        # 串口选择复选框
        self.check_log_port1 = QCheckBox('串口1')
        self.check_log_port1.setChecked(True)
        log_control_layout.addWidget(self.check_log_port1)
        
        self.check_log_port2 = QCheckBox('串口2')
        self.check_log_port2.setChecked(True)
        log_control_layout.addWidget(self.check_log_port2)
        
        log_control_layout.addStretch()
        
        # 清除日志按钮
        self.btn_clear_log = QPushButton('清除日志')
        self.btn_clear_log.clicked.connect(self.clear_log)
        log_control_layout.addWidget(self.btn_clear_log)
        
        # 保存日志按钮
        self.btn_save_log = QPushButton('保存日志')
        self.btn_save_log.clicked.connect(self.save_log)
        log_control_layout.addWidget(self.btn_save_log)
        
        # 关于按钮
        self.btn_about = QPushButton('关于')
        self.btn_about.clicked.connect(self.show_about)
        log_control_layout.addWidget(self.btn_about)
        
        log_layout.addLayout(log_control_layout)
        
        # 日志显示区域
        self.text_log = QTextEdit()
        self.text_log.setReadOnly(True)
        self.text_log.setMinimumHeight(400)  # 增大最小高度
        self.text_log.setMaximumHeight(600)  # 增大最大高度
        self.text_log.setFont(QFont('Consolas', 9))
        log_layout.addWidget(self.text_log)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        self.setLayout(main_layout)
        
        # 设置默认焦点
        self.edit_send1.setFocus()
        
    def scan_ports(self):
        """扫描可用串口"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.combo_port1.clear()
        self.combo_port1.addItems(ports)
        self.combo_port2.clear()
        self.combo_port2.addItems(ports)
        if ports:
            self.log_message(f"发现 {len(ports)} 个串口: {', '.join(ports)}")
        else:
            self.log_message("未发现可用串口")
            
    def toggle_connection(self, port_index):
        """切换串口连接状态"""
        if port_index == 1:
            if self.serial_port1 is None or not self.serial_port1.is_open:
                self.connect_serial(1)
            else:
                self.disconnect_serial(1)
        elif port_index == 2:
            if self.serial_port2 is None or not self.serial_port2.is_open:
                self.connect_serial(2)
            else:
                self.disconnect_serial(2)
            
    def connect_serial(self, port_index):
        """连接串口"""
        if port_index == 1:
            port = self.combo_port1.currentText()
            if not port:
                QMessageBox.warning(self, '警告', '请选择串口1')
                return
        else:
            port = self.combo_port2.currentText()
            if not port:
                QMessageBox.warning(self, '警告', '请选择串口2')
                return
            
        try:
            # 获取串口参数
            if port_index == 1:
                baud_rate = int(self.combo_baud1.currentText())
                data_bits = int(self.combo_data1.currentText())
                stop_bits_map = {'1': serial.STOPBITS_ONE, '1.5': serial.STOPBITS_ONE_POINT_FIVE, '2': serial.STOPBITS_TWO}
                stop_bits = stop_bits_map[self.combo_stop1.currentText()]
                parity_map = {'无': serial.PARITY_NONE, '奇校验': serial.PARITY_ODD, '偶校验': serial.PARITY_EVEN}
                parity = parity_map[self.combo_parity1.currentText()]
            else:
                baud_rate = int(self.combo_baud2.currentText())
                data_bits = int(self.combo_data2.currentText())
                stop_bits_map = {'1': serial.STOPBITS_ONE, '1.5': serial.STOPBITS_ONE_POINT_FIVE, '2': serial.STOPBITS_TWO}
                stop_bits = stop_bits_map[self.combo_stop2.currentText()]
                parity_map = {'无': serial.PARITY_NONE, '奇校验': serial.PARITY_ODD, '偶校验': serial.PARITY_EVEN}
                parity = parity_map[self.combo_parity2.currentText()]
            
            # 打开串口
            if port_index == 1:
                self.serial_port1 = serial.Serial(
                    port=port,
                    baudrate=baud_rate,
                    bytesize=data_bits,
                    stopbits=stop_bits,
                    parity=parity,
                    timeout=1
                )
                
                # 启动接收线程
                self.serial_thread1 = SerialThread(self.serial_port1)
                self.serial_thread1.data_received.connect(lambda data: self.on_data_received(data, 1))
                self.serial_thread1.error_occurred.connect(self.on_serial_error)
                self.serial_thread1.start()
                
                # 更新界面状态
                self.btn_connect1.setText('断开')
                self.combo_port1.setEnabled(False)
                self.combo_baud1.setEnabled(False)
                self.combo_data1.setEnabled(False)
                self.combo_stop1.setEnabled(False)
                self.combo_parity1.setEnabled(False)
                self.btn_refresh1.setEnabled(False)
            else:
                self.serial_port2 = serial.Serial(
                    port=port,
                    baudrate=baud_rate,
                    bytesize=data_bits,
                    stopbits=stop_bits,
                    parity=parity,
                    timeout=1
                )
                
                # 启动接收线程
                self.serial_thread2 = SerialThread(self.serial_port2)
                self.serial_thread2.data_received.connect(lambda data: self.on_data_received(data, 2))
                self.serial_thread2.error_occurred.connect(self.on_serial_error)
                self.serial_thread2.start()
                
                # 更新界面状态
                self.btn_connect2.setText('断开')
                self.combo_port2.setEnabled(False)
                self.combo_baud2.setEnabled(False)
                self.combo_data2.setEnabled(False)
                self.combo_stop2.setEnabled(False)
                self.combo_parity2.setEnabled(False)
                self.btn_refresh2.setEnabled(False)
            
            self.log_message(f"串口{port_index} {port} 连接成功")
            
            # 保存当前串口配置
            self.save_config()
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'连接串口失败: {str(e)}')
            self.log_message(f"串口{port_index}连接失败: {str(e)}", color='red')
        
    def disconnect_serial(self, port_index):
        """断开串口连接"""
        if port_index == 1:
            if self.auto_send_timer1:
                self.auto_send_timer1.stop()
                self.check_auto_send1.setChecked(False)
                
            if self.serial_thread1:
                self.serial_thread1.stop()
                self.serial_thread1.wait()
                self.serial_thread1 = None
                
            if self.serial_port1 and self.serial_port1.is_open:
                self.serial_port1.close()
                self.serial_port1 = None
                
            # 恢复界面状态
            self.btn_connect1.setText('连接')
            self.combo_port1.setEnabled(True)
            self.combo_baud1.setEnabled(True)
            self.combo_data1.setEnabled(True)
            self.combo_stop1.setEnabled(True)
            self.combo_parity1.setEnabled(True)
            self.btn_refresh1.setEnabled(True)
        else:
            if self.auto_send_timer2:
                self.auto_send_timer2.stop()
                self.check_auto_send2.setChecked(False)
                
            if self.serial_thread2:
                self.serial_thread2.stop()
                self.serial_thread2.wait()
                self.serial_thread2 = None
                
            if self.serial_port2 and self.serial_port2.is_open:
                self.serial_port2.close()
                self.serial_port2 = None
                
            # 恢复界面状态
            self.btn_connect2.setText('连接')
            self.combo_port2.setEnabled(True)
            self.combo_baud2.setEnabled(True)
            self.combo_data2.setEnabled(True)
            self.combo_stop2.setEnabled(True)
            self.combo_parity2.setEnabled(True)
            self.btn_refresh2.setEnabled(True)
        
        self.log_message(f"串口{port_index}已断开")
        
    def send_data(self, port_index):
        """发送数据"""
        if port_index == 1:
            if not self.serial_port1 or not self.serial_port1.is_open:
                QMessageBox.warning(self, '警告', '请先连接串口1')
                return
                
            data = self.edit_send1.text().strip()
            if not data:
                return
                
            try:
                if self.check_hex_send1.isChecked():
                    # 十六进制发送
                    data = data.replace(' ', '')
                    if len(data) % 2 != 0:
                        QMessageBox.warning(self, '警告', '十六进制数据长度必须为偶数')
                        return
                    try:
                        send_bytes = bytes.fromhex(data)
                    except ValueError:
                        QMessageBox.warning(self, '警告', '无效的十六进制数据')
                        return
                else:
                    # 文本发送 - 根据选择的编码编码数据
                    encoding = self.combo_send_encoding1.currentText()
                    try:
                        send_bytes = data.encode(encoding, errors='replace')
                    except LookupError:
                        QMessageBox.warning(self, '警告', f'不支持的编码格式: {encoding}')
                        return
                    except Exception as e:
                        QMessageBox.warning(self, '警告', f'编码失败: {str(e)}')
                        return
                        
                if self.check_hex_send1.isChecked():
                    # 十六进制发送时不添加换行符
                    pass
                elif self.check_newline1.isChecked():
                    send_bytes += b'\r\n'
                    
                self.serial_port1.write(send_bytes)
                self.sent_count1 += len(send_bytes)
                self.label_sent1.setText(f'发送: {self.sent_count1} 字节')
                
                # 添加到发送历史
                self.add_to_history(data, 1, self.check_hex_send1.isChecked())
                
                # 显示发送的数据
                if self.check_hex_send1.isChecked():
                    display_data = ' '.join([f'{b:02X}' for b in send_bytes])
                else:
                    # 显示发送的数据（使用接收编码显示）
                    receive_encoding = self.combo_encoding1.currentText()
                    try:
                        display_data = send_bytes.decode(receive_encoding, errors='replace')
                    except:
                        display_data = send_bytes.decode('utf-8', errors='replace')
                    
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3] if self.check_show_time1.isChecked() else ''
                send_msg = f"[串口1发送] {timestamp} {display_data}"
                # 根据串口1选择复选框决定是否显示
                if self.check_log_port1.isChecked():
                    self.log_message(send_msg, color='blue')
                
            except Exception as e:
                QMessageBox.critical(self, '错误', f'发送数据失败: {str(e)}')
        else:
            if not self.serial_port2 or not self.serial_port2.is_open:
                QMessageBox.warning(self, '警告', '请先连接串口2')
                return
                
            data = self.edit_send2.text().strip()
            if not data:
                return
                
            try:
                if self.check_hex_send2.isChecked():
                    # 十六进制发送
                    data = data.replace(' ', '')
                    if len(data) % 2 != 0:
                        QMessageBox.warning(self, '警告', '十六进制数据长度必须为偶数')
                        return
                    try:
                        send_bytes = bytes.fromhex(data)
                    except ValueError:
                        QMessageBox.warning(self, '警告', '无效的十六进制数据')
                        return
                else:
                    # 文本发送 - 根据选择的编码编码数据
                    encoding = self.combo_send_encoding2.currentText()
                    try:
                        send_bytes = data.encode(encoding, errors='replace')
                    except LookupError:
                        QMessageBox.warning(self, '警告', f'不支持的编码格式: {encoding}')
                        return
                    except Exception as e:
                        QMessageBox.warning(self, '警告', f'编码失败: {str(e)}')
                        return
                        
                if self.check_hex_send2.isChecked():
                    # 十六进制发送时不添加换行符
                    pass
                elif self.check_newline2.isChecked():
                    send_bytes += b'\r\n'
                    
                self.serial_port2.write(send_bytes)
                self.sent_count2 += len(send_bytes)
                self.label_sent2.setText(f'发送: {self.sent_count2} 字节')
                
                # 添加到发送历史
                self.add_to_history(data, 2, self.check_hex_send2.isChecked())
                
                # 显示发送的数据
                if self.check_hex_send2.isChecked():
                    display_data = ' '.join([f'{b:02X}' for b in send_bytes])
                else:
                    # 显示发送的数据（使用接收编码显示）
                    receive_encoding = self.combo_encoding2.currentText()
                    try:
                        display_data = send_bytes.decode(receive_encoding, errors='replace')
                    except:
                        display_data = send_bytes.decode('utf-8', errors='replace')
                    
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3] if self.check_show_time2.isChecked() else ''
                send_msg = f"[串口2发送] {timestamp} {display_data}"
                # 根据串口2选择复选框决定是否显示
                if self.check_log_port2.isChecked():
                    self.log_message(send_msg, color='blue')
                
            except Exception as e:
                QMessageBox.critical(self, '错误', f'发送数据失败: {str(e)}')
            
    def on_data_received(self, data, port_index):
        """接收数据回调"""
        if port_index == 1:
            self.received_count1 += len(data)
            self.label_received1.setText(f'接收: {self.received_count1} 字节')
            
            # 格式化显示数据
            if self.check_hex_display1.isChecked():
                display_data = ' '.join([f'{b:02X}' for b in data])
            else:
                # 根据选择的编码解码数据
                encoding = self.combo_encoding1.currentText()
                try:
                    decoded_data = data.decode(encoding, errors='replace')
                    # 将换行符替换为HTML换行标签
                    display_data = decoded_data.replace('\n', '<br>').replace('\r', '')
                except Exception as e:
                    display_data = ' '.join([f'{b:02X}' for b in data]) + f' (解码失败: {e})'
            
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3] if self.check_show_time1.isChecked() else ''
            receive_msg = f"[串口1接收] {timestamp} {display_data}"
            # 根据串口1选择复选框决定是否显示
            if self.check_log_port1.isChecked():
                self.log_message(receive_msg, color='green')
        else:
            self.received_count2 += len(data)
            self.label_received2.setText(f'接收: {self.received_count2} 字节')
            
            # 格式化显示数据
            if self.check_hex_display2.isChecked():
                display_data = ' '.join([f'{b:02X}' for b in data])
            else:
                # 根据选择的编码解码数据
                encoding = self.combo_encoding2.currentText()
                try:
                    decoded_data = data.decode(encoding, errors='replace')
                    # 将换行符替换为HTML换行标签
                    display_data = decoded_data.replace('\n', '<br>').replace('\r', '')
                except Exception as e:
                    display_data = ' '.join([f'{b:02X}' for b in data]) + f' (解码失败: {e})'
            
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3] if self.check_show_time2.isChecked() else ''
            receive_msg = f"[串口2接收] {timestamp} {display_data}"
            # 根据串口2选择复选框决定是否显示
            if self.check_log_port2.isChecked():
                self.log_message(receive_msg, color='green')
        
    def on_serial_error(self, error_msg):
        """串口错误回调"""
        self.log_message(f"[错误] {error_msg}", color='red')
        self.disconnect_serial(1)
        self.disconnect_serial(2)
        
    def toggle_auto_send(self, enabled, port_index):
        """切换自动发送"""
        if enabled:
            if port_index == 1:
                if not self.serial_port1 or not self.serial_port1.is_open:
                    QMessageBox.warning(self, '警告', '请先连接串口1')
                    self.check_auto_send1.setChecked(False)
                    return
                    
                interval = self.spin_interval1.value()
                self.auto_send_timer1 = QTimer()
                self.auto_send_timer1.timeout.connect(lambda: self.send_data(1))
                self.auto_send_timer1.start(interval)
            else:
                if not self.serial_port2 or not self.serial_port2.is_open:
                    QMessageBox.warning(self, '警告', '请先连接串口2')
                    self.check_auto_send2.setChecked(False)
                    return
                    
                interval = self.spin_interval2.value()
                self.auto_send_timer2 = QTimer()
                self.auto_send_timer2.timeout.connect(lambda: self.send_data(2))
                self.auto_send_timer2.start(interval)
            # 根据串口选择复选框决定是否显示
            if (port_index == 1 and self.check_log_port1.isChecked()) or (port_index == 2 and self.check_log_port2.isChecked()):
                self.log_message(f"串口{port_index}自动发送已启用，间隔: {interval}ms")
        else:
            if port_index == 1:
                if self.auto_send_timer1:
                    self.auto_send_timer1.stop()
                    self.auto_send_timer1 = None
            else:
                if self.auto_send_timer2:
                    self.auto_send_timer2.stop()
                    self.auto_send_timer2 = None
            # 根据串口选择复选框决定是否显示
            if (port_index == 1 and self.check_log_port1.isChecked()) or (port_index == 2 and self.check_log_port2.isChecked()):
                self.log_message(f"串口{port_index}自动发送已禁用")
            
    def update_display_format(self, port_index):
        """更新显示格式"""
        # 这个方法可以用于实时更新显示格式，目前暂不实现
        pass
        
    def clear_receive(self, port_index):
        """清除接收区域"""
        if port_index == 1:
            self.text_receive1.clear()
            self.received_count1 = 0
            self.label_received1.setText('接收: 0 字节')
        else:
            self.text_receive2.clear()
            self.received_count2 = 0
            self.label_received2.setText('接收: 0 字节')
        
    def log_message(self, message, color='black'):
        """添加日志消息"""
        from PyQt5.QtCore import QDateTime
        
        # 获取当前时间
        current_time = QDateTime.currentDateTime().toString('hh:mm:ss.zzz')
        
        # 格式化消息
        formatted_message = f'[{current_time}] {message}'
        
        # 设置颜色
        if color == 'red':
            formatted_message = f'<span style="color: red;">{formatted_message}</span>'
        elif color == 'green':
            formatted_message = f'<span style="color: green;">{formatted_message}</span>'
        elif color == 'blue':
            formatted_message = f'<span style="color: blue;">{formatted_message}</span>'
        
        # 添加到日志区域
        self.text_log.append(formatted_message)
        
        # 自动滚动到底部
        scrollbar = self.text_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_log(self):
        """清除日志"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            '确认清除', 
            '确定要清除所有日志内容吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.text_log.clear()
            self.log_message("日志已清除")

    def save_log(self):
        """保存日志到文件"""
        from PyQt5.QtWidgets import QFileDialog
        from PyQt5.QtCore import QDateTime
        
        # 获取当前时间作为默认文件名
        current_time = QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')
        default_filename = f"serial_debug_log_{current_time}.txt"
        
        # 选择保存文件
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存日志文件",
            default_filename,
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if file_path:
            try:
                # 获取日志内容（纯文本）
                log_content = self.text_log.toPlainText()
                
                # 保存到文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                self.log_message(f"日志已保存到: {file_path}", color='green')
                
            except Exception as e:
                self.log_message(f"保存日志失败: {str(e)}", color='red')
                QMessageBox.critical(self, '错误', f'保存日志失败: {str(e)}')

    def save_config(self):
        """保存配置"""
        try:
            config = {
                'serial1': {
                    'port': self.combo_port1.currentText(),
                    'baud': int(self.combo_baud1.currentText()),
                    'data_bits': int(self.combo_data1.currentText()),
                    'stop_bits': self.combo_stop1.currentText(),
                    'parity': self.combo_parity1.currentText(),
                    'send_encoding': self.combo_send_encoding1.currentText(),
                    'recv_encoding': self.combo_encoding1.currentText(),
                    'auto_newline': self.check_newline1.isChecked(),
                    'send_history_text': self.send_history1_text,
                    'send_history_hex': self.send_history1_hex,
                    'quick_strings': self.quick_strings1
                },
                'serial2': {
                    'port': self.combo_port2.currentText(),
                    'baud': int(self.combo_baud2.currentText()),
                    'data_bits': int(self.combo_data2.currentText()),
                    'stop_bits': self.combo_stop2.currentText(),
                    'parity': self.combo_parity2.currentText(),
                    'send_encoding': self.combo_send_encoding2.currentText(),
                    'recv_encoding': self.combo_encoding2.currentText(),
                    'auto_newline': self.check_newline2.isChecked(),
                    'send_history_text': self.send_history2_text,
                    'send_history_hex': self.send_history2_hex,
                    'quick_strings': self.quick_strings2
                }
            }
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.log_message(f"保存配置失败: {e}")

    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # 加载串口1配置
                    if 'serial1' in config:
                        serial1_config = config['serial1']
                        if 'port' in serial1_config:
                            self.combo_port1.setCurrentText(serial1_config['port'])
                        if 'baud' in serial1_config:
                            self.combo_baud1.setCurrentText(str(serial1_config['baud']))
                        if 'data_bits' in serial1_config:
                            self.combo_data1.setCurrentText(str(serial1_config['data_bits']))
                        if 'stop_bits' in serial1_config:
                            self.combo_stop1.setCurrentText(str(serial1_config['stop_bits']))
                        if 'parity' in serial1_config:
                            self.combo_parity1.setCurrentText(serial1_config['parity'])
                        if 'send_encoding' in serial1_config:
                            self.combo_send_encoding1.setCurrentText(serial1_config['send_encoding'])
                        if 'recv_encoding' in serial1_config:
                            self.combo_encoding1.setCurrentText(serial1_config['recv_encoding'])
                        if 'auto_newline' in serial1_config:
                            self.check_newline1.setChecked(serial1_config['auto_newline'])
                        if 'send_history_text' in serial1_config:
                            self.send_history1_text = serial1_config['send_history_text']
                        if 'send_history_hex' in serial1_config:
                            self.send_history1_hex = serial1_config['send_history_hex']
                        if 'quick_strings' in serial1_config:
                            self.quick_strings1 = serial1_config['quick_strings']
                            # 确保列表有40个元素
                            while len(self.quick_strings1) < 40:
                                self.quick_strings1.append({"label": f"字符串{len(self.quick_strings1)+1}", "content": "", "hex": False})
                            self.update_quick_strings_buttons(1)
                    
                    # 加载串口2配置
                    if 'serial2' in config:
                        serial2_config = config['serial2']
                        if 'port' in serial2_config:
                            self.combo_port2.setCurrentText(serial2_config['port'])
                        if 'baud' in serial2_config:
                            self.combo_baud2.setCurrentText(str(serial2_config['baud']))
                        if 'data_bits' in serial2_config:
                            self.combo_data2.setCurrentText(str(serial2_config['data_bits']))
                        if 'stop_bits' in serial2_config:
                            self.combo_stop2.setCurrentText(str(serial2_config['stop_bits']))
                        if 'parity' in serial2_config:
                            self.combo_parity2.setCurrentText(serial2_config['parity'])
                        if 'send_encoding' in serial2_config:
                            self.combo_send_encoding2.setCurrentText(serial2_config['send_encoding'])
                        if 'recv_encoding' in serial2_config:
                            self.combo_encoding2.setCurrentText(serial2_config['recv_encoding'])
                        if 'auto_newline' in serial2_config:
                            self.check_newline2.setChecked(serial2_config['auto_newline'])
                        if 'send_history_text' in serial2_config:
                            self.send_history2_text = serial2_config['send_history_text']
                        if 'send_history_hex' in serial2_config:
                            self.send_history2_hex = serial2_config['send_history_hex']
                        if 'quick_strings' in serial2_config:
                            self.quick_strings2 = serial2_config['quick_strings']
                            # 确保列表有40个元素
                            while len(self.quick_strings2) < 40:
                                self.quick_strings2.append({"label": f"字符串{len(self.quick_strings2)+1}", "content": "", "hex": False})
                            self.update_quick_strings_buttons(2)
                
                # 更新历史记录下拉框
                self.update_history_combo(1)
                self.update_history_combo(2)
                
        except Exception as e:
            self.log_message(f"加载配置失败: {e}")
            
    def closeEvent(self, event):
        """程序关闭事件"""
        # 断开串口连接
        if self.serial_port1 and self.serial_port1.is_open:
            self.disconnect_serial(1)
        if self.serial_port2 and self.serial_port2.is_open:
            self.disconnect_serial(2)
        
        # 保存配置
        self.save_config()
        event.accept()

    def on_hex_send_toggled(self, checked):
        """十六进制发送选项切换事件"""
        # 获取发送信号的控件
        sender = self.sender()
        
        if sender == self.check_hex_send1:
            if checked:
                # 选择十六进制发送时，记住当前自动换行状态并禁用
                self.newline_state1 = self.check_newline1.isChecked()
                self.check_newline1.setChecked(False)
                self.check_newline1.setEnabled(False)
            else:
                # 取消十六进制发送时，恢复自动换行状态
                self.check_newline1.setEnabled(True)
                self.check_newline1.setChecked(self.newline_state1)
        elif sender == self.check_hex_send2:
            if checked:
                # 选择十六进制发送时，记住当前自动换行状态并禁用
                self.newline_state2 = self.check_newline2.isChecked()
                self.check_newline2.setChecked(False)
                self.check_newline2.setEnabled(False)
            else:
                # 取消十六进制发送时，恢复自动换行状态
                self.check_newline2.setEnabled(True)
                self.check_newline2.setChecked(self.newline_state2)
                
    def add_to_history(self, data, port_index, is_hex=False):
        """添加数据到发送历史"""
        if port_index == 1:
            if is_hex:
                history = self.send_history1_hex
            else:
                history = self.send_history1_text
            combo = self.combo_history1
        else:
            if is_hex:
                history = self.send_history2_hex
            else:
                history = self.send_history2_text
            combo = self.combo_history2
            
        # 如果数据已存在，先移除
        if data in history:
            history.remove(data)
            
        # 添加到开头
        history.insert(0, data)
        
        # 限制历史记录数量
        if len(history) > self.max_history:
            history.pop()
            
        # 更新下拉框
        self.update_history_combo(port_index)
        
    def update_history_combo(self, port_index):
        """更新历史记录下拉框"""
        if port_index == 1:
            combo = self.combo_history1
            text_history = self.send_history1_text
            hex_history = self.send_history1_hex
        else:
            combo = self.combo_history2
            text_history = self.send_history2_text
            hex_history = self.send_history2_hex
            
        combo.clear()
        
        # 添加文本历史记录
        if text_history:
            combo.addItem("--- 文本历史 ---")
            for item in text_history:
                combo.addItem(item)
                
        # 添加十六进制历史记录
        if hex_history:
            combo.addItem("--- 十六进制历史 ---")
            for item in hex_history:
                combo.addItem(item)

    def on_history_selected(self, text, port_index):
        """历史记录下拉框选择事件"""
        # 忽略分隔符
        if text.startswith("---") or not text:
            return
            
        if port_index == 1:
            self.edit_send1.setText(text)
        else:
            self.edit_send2.setText(text)
            
    def quick_send_string(self, string_index, port_index):
        """快速发送预设字符串"""
        if port_index == 1:
            if not self.serial_port1 or not self.serial_port1.is_open:
                QMessageBox.warning(self, '警告', '请先连接串口1')
                return
            # 检查索引是否有效
            if string_index >= len(self.quick_strings1):
                QMessageBox.warning(self, '警告', f'词条{string_index+1}不存在')
                return
            string_info = self.quick_strings1[string_index]
            edit_send = self.edit_send1
            check_hex = self.check_hex_send1
            check_newline = self.check_newline1
            combo_encoding = self.combo_send_encoding1
            combo_receive_encoding = self.combo_encoding1
            check_show_time = self.check_show_time1
            serial_port = self.serial_port1
            sent_count = self.sent_count1
            label_sent = self.label_sent1
        else:
            if not self.serial_port2 or not self.serial_port2.is_open:
                QMessageBox.warning(self, '警告', '请先连接串口2')
                return
            # 检查索引是否有效
            if string_index >= len(self.quick_strings2):
                QMessageBox.warning(self, '警告', f'词条{string_index+1}不存在')
                return
            string_info = self.quick_strings2[string_index]
            edit_send = self.edit_send2
            check_hex = self.check_hex_send2
            check_newline = self.check_newline2
            combo_encoding = self.combo_send_encoding2
            combo_receive_encoding = self.combo_encoding2
            check_show_time = self.check_show_time2
            serial_port = self.serial_port2
            sent_count = self.sent_count2
            label_sent = self.label_sent2
            
        # 检查词条内容是否为空
        if not string_info['content']:
            QMessageBox.warning(self, '警告', f'词条{string_index+1}内容为空')
            return
            
        # 获取字符串内容
        data = string_info["content"]
        is_hex = string_info["hex"]
        
        try:
            if is_hex:
                # 十六进制发送
                data = data.replace(' ', '')
                if len(data) % 2 != 0:
                    QMessageBox.warning(self, '警告', '十六进制数据长度必须为偶数')
                    return
                try:
                    send_bytes = bytes.fromhex(data)
                except ValueError:
                    QMessageBox.warning(self, '警告', '无效的十六进制数据')
                    return
            else:
                # 文本发送
                encoding = combo_encoding.currentText()
                try:
                    send_bytes = data.encode(encoding, errors='replace')
                except LookupError:
                    QMessageBox.warning(self, '警告', f'不支持的编码格式: {encoding}')
                    return
                except Exception as e:
                    QMessageBox.warning(self, '警告', f'编码失败: {str(e)}')
                    return
                    
            # 根据当前设置决定是否添加换行符
            if is_hex:
                # 十六进制发送时不添加换行符
                pass
            elif check_newline.isChecked():
                send_bytes += b'\r\n'
                
            # 发送数据
            serial_port.write(send_bytes)
            sent_count += len(send_bytes)
            label_sent.setText(f'发送: {sent_count} 字节')
            
            # 更新计数
            if port_index == 1:
                self.sent_count1 = sent_count
            else:
                self.sent_count2 = sent_count
            
            # 添加到发送历史
            self.add_to_history(data, port_index, is_hex)
            
            # 显示发送的数据
            if is_hex:
                display_data = ' '.join([f'{b:02X}' for b in send_bytes])
            else:
                # 显示发送的数据（使用接收编码显示）
                receive_encoding = combo_receive_encoding.currentText()
                try:
                    display_data = send_bytes.decode(receive_encoding, errors='replace')
                except:
                    display_data = send_bytes.decode('utf-8', errors='replace')
                
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3] if check_show_time.isChecked() else ''
            send_msg = f"[串口{port_index}快速发送] {timestamp} {display_data}"
            self.log_message(send_msg, color='blue')
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'快速发送失败: {str(e)}')
            
    def update_quick_strings_buttons(self, port_index):
        """更新快速字符串按钮的标签"""
        if port_index == 1:
            # 更新串口1的按钮
            for i, button in enumerate(self.quick_string_buttons1):
                if i < len(self.quick_strings1) and self.quick_strings1[i]['content']:
                    content = self.quick_strings1[i]['content']
                    is_hex = self.quick_strings1[i].get('hex', False)
                    if len(content) > 10:
                        display_text = content[:8] + ".."
                    else:
                        display_text = content
                    type_text = "十六进制" if is_hex else "文本"
                    button.setText(display_text)
                    button.setToolTip(f"词条{i+1}: {content}\n类型: {type_text}\n右键点击可编辑词条")
                    button.setVisible(True)
                else:
                    button.setVisible(False)
        else:
            # 更新串口2的按钮
            for i, button in enumerate(self.quick_string_buttons2):
                if i < len(self.quick_strings2) and self.quick_strings2[i]['content']:
                    content = self.quick_strings2[i]['content']
                    is_hex = self.quick_strings2[i].get('hex', False)
                    if len(content) > 10:
                        display_text = content[:8] + ".."
                    else:
                        display_text = content
                    type_text = "十六进制" if is_hex else "文本"
                    button.setText(display_text)
                    button.setToolTip(f"词条{i+1}: {content}\n类型: {type_text}\n右键点击可编辑词条")
                    button.setVisible(True)
                else:
                    button.setVisible(False)

    def import_sscom_config(self, port_num):
        """导入SSCOM配置文件"""
        from PyQt5.QtWidgets import QFileDialog
        
        # 选择SSCOM配置文件
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"选择SSCOM.ini配置文件 - 串口{port_num}",
            "",
            "SSCOM配置文件 (*.ini);;所有文件 (*)"
        )
        
        if file_path:
            try:
                # 解析SSCOM配置文件
                quick_strings = self.parse_sscom_quick_strings(file_path)
                
                if quick_strings:
                    # 只导入多条字符串配置
                    if port_num == 1:
                        self.quick_strings1 = quick_strings
                        self.update_quick_strings_buttons(1)
                    else:
                        self.quick_strings2 = quick_strings
                        self.update_quick_strings_buttons(2)
                    
                    # 立即保存配置
                    self.save_config()
                    
                    self.log_message(f"串口{port_num}：成功从SSCOM.ini导入{len(quick_strings)}个词条")
                else:
                    self.log_message(f"串口{port_num}：未在SSCOM.ini文件中找到有效的词条配置")
                    
            except Exception as e:
                self.log_message(f"串口{port_num}：导入SSCOM.ini词条失败 - {e}")

    def parse_sscom_quick_strings(self, file_path):
        """解析SSCOM配置文件中的多条字符串"""
        quick_strings = []
        try:
            with open(file_path, 'r', encoding='gbk') as f:  # SSCOM通常使用GBK编码
                content = f.read()
                
            # 尝试解析新的SSCOM格式：N1xx定义词条信息，Nx定义词条内容
            for i in range(1, 101):  # 支持最多100个快速字符串
                # 查找词条信息行 N1xx=类型,名称,延时
                info_match = re.search(rf'N1{i:02d}=(\d+),([^,]*),(\d+)', content)
                if info_match:
                    # 查找对应的词条内容行 Nx=类型,内容
                    content_match = re.search(rf'N{i}=([HA]),([^\r\n]*)', content)
                    if content_match:
                        content_type = content_match.group(1)  # H=十六进制, A=ASCII
                        content_data = content_match.group(2).strip()
                        name = info_match.group(2).strip()
                        
                        if content_data:  # 只处理有内容的词条
                            # 判断是否为十六进制
                            is_hex = (content_type == 'H')
                            
                            # 创建与程序期望格式一致的数据结构
                            quick_strings.append({
                                'content': content_data,  # 内容
                                'hex': is_hex,           # 是否十六进制
                                'label': f'字符串{i}'    # 按钮标签
                            })
            
            # 如果没有找到新格式，尝试解析旧格式
            if not quick_strings:
                for i in range(1, 41):  # 支持40个快速字符串
                    # 查找字符串内容
                    str_match = re.search(rf'Str{i}=(.+)', content)
                    if str_match:
                        str_content = str_match.group(1).strip()
                        if str_content:
                            # 检查是否为十六进制
                            is_hex = False
                            hex_match = re.search(rf'Hex{i}=(\w+)', content)
                            if hex_match and hex_match.group(1).lower() == 'true':
                                is_hex = True
                            
                            # 创建与程序期望格式一致的数据结构
                            quick_strings.append({
                                'content': str_content,  # 内容
                                'hex': is_hex,           # 是否十六进制
                                'label': f'字符串{i}'    # 按钮标签
                            })
            
            return quick_strings
            
        except Exception as e:
            self.log_message(f"解析SSCOM快速字符串失败: {e}")
            return []

    def show_quick_string_menu(self, pos, string_index, port_index):
        """显示快速字符串右键菜单"""
        from PyQt5.QtWidgets import QMenu
        
        menu = QMenu()
        
        # 编辑词条
        edit_action = menu.addAction("编辑词条")
        edit_action.triggered.connect(lambda: self.edit_quick_string(string_index, port_index))
        
        # 删除词条
        delete_action = menu.addAction("删除词条")
        delete_action.triggered.connect(lambda: self.delete_quick_string(string_index, port_index))
        
        # 显示菜单
        if port_index == 1:
            button = self.quick_string_buttons1[string_index]
        else:
            button = self.quick_string_buttons2[string_index]
        
        menu.exec_(button.mapToGlobal(pos))

    def edit_quick_string(self, string_index, port_index):
        """编辑快速字符串"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton
        
        # 获取当前词条信息
        if port_index == 1:
            if string_index < len(self.quick_strings1):
                current_string = self.quick_strings1[string_index]
            else:
                current_string = {'content': '', 'hex': False, 'label': f'字符串{string_index+1}'}
        else:
            if string_index < len(self.quick_strings2):
                current_string = self.quick_strings2[string_index]
            else:
                current_string = {'content': '', 'hex': False, 'label': f'字符串{string_index+1}'}
        
        # 创建编辑对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑词条 - {current_string['label']}")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QVBoxLayout()
        
        # 内容输入
        content_layout = QHBoxLayout()
        content_layout.addWidget(QLabel("内容:"))
        content_edit = QLineEdit(current_string['content'])
        content_layout.addWidget(content_edit)
        layout.addLayout(content_layout)
        
        # 十六进制选项
        hex_check = QCheckBox("十六进制")
        hex_check.setChecked(current_string['hex'])
        layout.addWidget(hex_check)
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        cancel_button = QPushButton("取消")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 连接信号
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            # 保存修改
            new_content = content_edit.text().strip()
            new_hex = hex_check.isChecked()
            
            if port_index == 1:
                # 确保列表长度足够
                while len(self.quick_strings1) <= string_index:
                    self.quick_strings1.append({'content': '', 'hex': False, 'label': f'字符串{len(self.quick_strings1)+1}'})
                
                self.quick_strings1[string_index] = {
                    'content': new_content,
                    'hex': new_hex,
                    'label': f'字符串{string_index+1}'
                }
                self.update_quick_strings_buttons(1)
            else:
                # 确保列表长度足够
                while len(self.quick_strings2) <= string_index:
                    self.quick_strings2.append({'content': '', 'hex': False, 'label': f'字符串{len(self.quick_strings2)+1}'})
                
                self.quick_strings2[string_index] = {
                    'content': new_content,
                    'hex': new_hex,
                    'label': f'字符串{string_index+1}'
                }
                self.update_quick_strings_buttons(2)
            
            # 保存配置
            self.save_config()
            
            self.log_message(f"串口{port_index}：词条{string_index+1}已更新")

    def delete_quick_string(self, string_index, port_index):
        """删除快速字符串"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 
            '确认删除', 
            f'确定要删除词条{string_index+1}吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if port_index == 1:
                if string_index < len(self.quick_strings1):
                    # 删除当前词条，后面的词条自动递进
                    del self.quick_strings1[string_index]
                    # 在末尾添加一个空词条，保持列表长度
                    self.quick_strings1.append({'content': '', 'hex': False, 'label': f'字符串{len(self.quick_strings1)+1}'})
                    self.update_quick_strings_buttons(1)
            else:
                if string_index < len(self.quick_strings2):
                    # 删除当前词条，后面的词条自动递进
                    del self.quick_strings2[string_index]
                    # 在末尾添加一个空词条，保持列表长度
                    self.quick_strings2.append({'content': '', 'hex': False, 'label': f'字符串{len(self.quick_strings2)+1}'})
                    self.update_quick_strings_buttons(2)
            
            # 保存配置
            self.save_config()
            
            self.log_message(f"串口{port_index}：词条{string_index+1}已删除，后续词条已递进")

    def show_about(self):
        """显示关于对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        from PyQt5.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle("关于 - 双串口调试器")
        dialog.setModal(True)
        dialog.resize(450, 250)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("双串口调试器")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 版本信息
        version_label = QLabel(f"版本: {VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # 构建时间
        build_time_label = QLabel(f"构建时间: {BUILD_TIME}")
        build_time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(build_time_label)
        
        # 功能描述
        desc_label = QLabel("功能完整的双串口通信调试工具")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        desc2_label = QLabel("支持多种编码、历史记录、快速字符串等功能")
        desc2_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc2_label)
        
        # SSCOM导入说明
        sscom_label = QLabel("支持从SSCOM.ini文件导入词条配置")
        sscom_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(sscom_label)
        
        # 作者信息
        author_label = QLabel("<b>作者：</b> logicsoft@qq.com")
        author_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_label)
        
        layout.addStretch()
        
        # 按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.setFixedWidth(80)
        ok_button.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        
        # 显示对话框
        dialog.exec_()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('COM口串口调试器')
    
    # 设置样式
    app.setStyle('Fusion')
    
    window = SerialDebugger()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
