#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
from pathlib import Path

def check_status():
    print("=== 音频文件状态检查 ===\n")
    
    # 检查当前目录的音频文件
    wav_files = glob.glob("*.wav")
    mp3_files = glob.glob("*.mp3")
    
    print("当前目录音频文件：")
    if wav_files:
        for wav in wav_files:
            size = os.path.getsize(wav) / (1024 * 1024)  # MB
            print(f"  ✓ {wav} ({size:.1f} MB)")
    if mp3_files:
        for mp3 in mp3_files:
            size = os.path.getsize(mp3) / (1024 * 1024)  # MB
            print(f"  ✓ {mp3} ({size:.1f} MB)")
    
    if not wav_files and not mp3_files:
        print("  ❌ 没有找到音频文件")
    
    # 检查临时文件夹
    if os.path.exists("temp_audio_chunks"):
        chunks = glob.glob("temp_audio_chunks/chunk_*.wav")
        print(f"\n临时音频块文件：{len(chunks)} 个")
        
        if chunks:
            total_size = sum(os.path.getsize(chunk) for chunk in chunks) / (1024 * 1024)
            print(f"  总大小：{total_size:.1f} MB")
    
    # 显示完整路径
    print(f"\n文件位置：{os.path.abspath('.')}")

if __name__ == "__main__":
    check_status()
    input("\n按回车键退出...")