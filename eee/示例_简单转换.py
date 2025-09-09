#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的TXT转MP3示例脚本
这个脚本演示了如何快速将文本转换为语音
"""

import os
import sys
from pathlib import Path

def create_sample_text():
    """创建一个示例文本文件"""
    sample_text = """
欢迎使用TXT转MP3工具！

这是一个示例文本，用来演示文本转语音功能。

本工具支持以下功能：
1. 将任何中文或英文文本转换为语音
2. 支持调节语音速度和音量
3. 支持大文件分块处理
4. 支持批量转换多个文件

使用方法很简单：
- 准备好你的txt文件
- 运行转换脚本
- 等待转换完成
- 享受你的有声读物！

希望这个工具能帮助你更好地"听"文字内容。
"""
    
    with open("示例文本.txt", "w", encoding="utf-8") as f:
        f.write(sample_text.strip())
    
    print("✓ 已创建示例文本文件：示例文本.txt")

def simple_convert():
    """简单转换示例"""
    try:
        # 导入转换函数
        sys.path.append('.')
        from txt_to_mp3 import txt_to_mp3
        
        # 检查示例文件是否存在
        if not os.path.exists("示例文本.txt"):
            create_sample_text()
        
        print("开始转换示例文本...")
        
        # 执行转换
        success = txt_to_mp3(
            txt_file_path="示例文本.txt",
            output_mp3_path="示例音频.wav",  # 使用WAV格式（不需要FFmpeg）
            voice_rate=180,  # 适中的语速
            voice_volume=0.9  # 较高的音量
        )
        
        if success:
            print("✓ 转换成功！")
            print("生成的音频文件：示例音频.wav")
            print("你可以用任何音频播放器打开这个文件")
        else:
            print("✗ 转换失败！")
            print("请检查是否已安装必要的依赖包")
            
    except ImportError:
        print("错误：无法导入转换模块")
        print("请先运行：python install_requirements.py")
    except Exception as e:
        print(f"转换过程中出现错误：{e}")

def main():
    print("=== TXT转MP3 简单示例 ===\n")
    
    print("这个脚本将演示如何使用TXT转MP3工具")
    print("1. 创建示例文本文件")
    print("2. 将文本转换为语音文件")
    print("3. 生成可播放的音频文件\n")
    
    choice = input("是否开始演示？(y/n): ").lower().strip()
    
    if choice in ['y', 'yes', '是', '好']:
        simple_convert()
    else:
        print("演示已取消")
    
    print("\n如需转换你自己的文件，请使用：")
    print("- python txt_to_mp3.py (普通文件)")
    print("- python txt_to_mp3_advanced.py (大文件)")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")