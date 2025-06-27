#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COM口串口调试器演示脚本
展示程序的主要功能和使用方法
"""

import sys
import time
import serial
import serial.tools.list_ports

def demo_serial_scan():
    """演示串口扫描功能"""
    print("=== 串口扫描演示 ===")
    ports = list(serial.tools.list_ports.comports())
    print(f"发现 {len(ports)} 个串口设备:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port.device}: {port.description}")
    return ports

def demo_data_formats():
    """演示数据格式转换"""
    print("\n=== 数据格式演示 ===")
    
    # 文本转十六进制
    text = "Hello World"
    hex_data = ' '.join([f'{ord(c):02X}' for c in text])
    print(f"文本: '{text}'")
    print(f"十六进制: {hex_data}")
    
    # 十六进制转文本
    hex_bytes = bytes.fromhex(hex_data.replace(' ', ''))
    decoded_text = hex_bytes.decode('utf-8')
    print(f"解码后: '{decoded_text}'")
    
    # 特殊字符演示
    special_chars = "中文测试123!@#"
    hex_special = ' '.join([f'{ord(c):02X}' for c in special_chars])
    print(f"\n特殊字符: '{special_chars}'")
    print(f"十六进制: {hex_special}")

def demo_serial_parameters():
    """演示串口参数"""
    print("\n=== 串口参数演示 ===")
    
    params = {
        '波特率': ['9600', '19200', '38400', '57600', '115200', '230400', '460800', '921600'],
        '数据位': ['5', '6', '7', '8'],
        '停止位': ['1', '1.5', '2'],
        '校验位': ['无', '奇校验', '偶校验']
    }
    
    for param_name, values in params.items():
        print(f"{param_name}: {', '.join(values)}")

def demo_common_commands():
    """演示常用AT指令"""
    print("\n=== 常用AT指令演示 ===")
    
    commands = [
        ("AT", "测试AT连接"),
        ("AT+RST", "重置模块"),
        ("AT+CWMODE=1", "设置WiFi模式为Station"),
        ("AT+CWJAP=\"SSID\",\"PASSWORD\"", "连接到WiFi网络"),
        ("AT+CIPSTART=\"TCP\",\"192.168.1.100\",8080", "建立TCP连接"),
        ("AT+CIPSEND=5", "发送5字节数据"),
        ("AT+CWJAP?", "查询WiFi连接状态")
    ]
    
    for cmd, desc in commands:
        print(f"{cmd:<35} - {desc}")

def demo_usage_scenarios():
    """演示使用场景"""
    print("\n=== 使用场景演示 ===")
    
    scenarios = [
        {
            "场景": "WiFi模组调试",
            "用途": "配置ESP8266/ESP32等WiFi模组",
            "常用指令": ["AT", "AT+RST", "AT+CWMODE=1", "AT+CWJAP"],
            "波特率": "115200"
        },
        {
            "场景": "蓝牙模块调试",
            "用途": "配置HC-05/HC-06等蓝牙模块",
            "常用指令": ["AT", "AT+NAME", "AT+PSWD", "AT+UART"],
            "波特率": "9600"
        },
        {
            "场景": "GPS模块调试",
            "用途": "读取NMEA数据",
            "常用指令": ["$PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*28"],
            "波特率": "9600"
        },
        {
            "场景": "传感器数据读取",
            "用途": "读取温湿度、压力等传感器数据",
            "常用指令": ["自定义协议"],
            "波特率": "9600-115200"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['场景']}")
        print(f"   用途: {scenario['用途']}")
        print(f"   常用指令: {', '.join(scenario['常用指令'])}")
        print(f"   推荐波特率: {scenario['波特率']}")

def main():
    """主演示函数"""
    print("COM口串口调试器 - 功能演示")
    print("=" * 50)
    
    # 运行各个演示
    demo_serial_scan()
    demo_data_formats()
    demo_serial_parameters()
    demo_common_commands()
    demo_usage_scenarios()
    
    print("\n" + "=" * 50)
    print("演示完成！")
    print("\n使用说明:")
    print("1. 运行 'python serial_debugger.py' 启动程序")
    print("2. 选择串口并设置参数")
    print("3. 点击连接按钮")
    print("4. 在发送区域输入数据并发送")
    print("5. 观察接收区域的数据")
    
    print("\n快捷键:")
    print("- Enter: 发送数据")
    print("- Ctrl+C: 复制")
    print("- Ctrl+V: 粘贴")
    print("- Ctrl+A: 全选")

if __name__ == '__main__':
    main() 