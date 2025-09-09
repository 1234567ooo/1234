#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
改进版TXT转MP3工具
解决FFmpeg依赖问题，提供更好的错误处理和用户体验
"""

import pyttsx3
import os
import sys
import subprocess
from pathlib import Path
import time
import warnings

# 抑制pydub的FFmpeg警告
warnings.filterwarnings("ignore", message="Couldn't find ffmpeg or avconv")

def check_ffmpeg():
    """检查FFmpeg是否可用"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            check=True, 
            timeout=5
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False

def check_pydub():
    """检查pydub是否可用"""
    try:
        import pydub
        return True
    except ImportError:
        return False

def txt_to_audio_improved(txt_file_path, output_path=None, voice_rate=180, voice_volume=0.9, prefer_mp3=False):
    """
    改进版文本转音频函数
    
    参数:
    txt_file_path: 输入文本文件路径
    output_path: 输出音频文件路径
    voice_rate: 语音速度 (50-300)
    voice_volume: 音量 (0.0-1.0)
    prefer_mp3: 是否优先生成MP3格式
    """
    
    # 检查输入文件
    if not os.path.exists(txt_file_path):
        print(f"❌ 错误：找不到文件 {txt_file_path}")
        return False
    
    # 检查系统环境
    ffmpeg_available = check_ffmpeg()
    pydub_available = check_pydub()
    
    print(f"🔍 系统检查:")
    print(f"   FFmpeg: {'✅ 可用' if ffmpeg_available else '❌ 不可用'}")
    print(f"   Pydub: {'✅ 可用' if pydub_available else '❌ 不可用'}")
    
    # 确定输出格式和路径
    txt_path = Path(txt_file_path)
    if output_path is None:
        if prefer_mp3 and ffmpeg_available:
            output_path = txt_path.with_suffix('.mp3')
        else:
            output_path = txt_path.with_suffix('.wav')
    else:
        output_path = Path(output_path)
    
    # 如果用户要求MP3但FFmpeg不可用，给出提示
    if str(output_path).endswith('.mp3') and not ffmpeg_available:
        print("⚠️  警告：FFmpeg不可用，将生成WAV格式")
        output_path = output_path.with_suffix('.wav')
    
    try:
        # 读取文本文件
        print(f"📖 正在读取文件: {txt_file_path}")
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        if not text.strip():
            print("❌ 错误：文件内容为空")
            return False
        
        print(f"📝 文件内容长度: {len(text)} 字符")
        
        # 初始化TTS引擎
        print("🎤 正在初始化语音引擎...")
        engine = pyttsx3.init()
        
        # 设置语音属性
        engine.setProperty('rate', voice_rate)
        engine.setProperty('volume', voice_volume)
        
        # 选择最佳语音
        voices = engine.getProperty('voices')
        if voices:
            chinese_voice = None
            for voice in voices:
                voice_name = voice.name.lower()
                if any(keyword in voice_name for keyword in ['chinese', 'mandarin', 'zh', '中文']):
                    chinese_voice = voice
                    break
            
            if chinese_voice:
                engine.setProperty('voice', chinese_voice.id)
                print(f"🗣️  使用中文语音: {chinese_voice.name}")
            else:
                engine.setProperty('voice', voices[0].id)
                print(f"🗣️  使用默认语音: {voices[0].name}")
                print("💡 提示：如需更好的中文发音，请安装中文语音包")
        
        # 转换为音频
        print(f"🔄 正在转换为音频文件...")
        print(f"📁 输出路径: {output_path}")
        print("⏳ 请耐心等待，转换可能需要一些时间...")
        
        start_time = time.time()
        
        # 直接保存为目标格式
        if str(output_path).endswith('.wav'):
            # 直接保存为WAV
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()
            
        elif str(output_path).endswith('.mp3') and ffmpeg_available:
            # 先保存为WAV，再转换为MP3
            temp_wav = output_path.with_suffix('.wav')
            engine.save_to_file(text, str(temp_wav))
            engine.runAndWait()
            
            print("🔄 正在转换为MP3格式...")
            try:
                subprocess.run([
                    'ffmpeg', '-i', str(temp_wav), 
                    '-acodec', 'libmp3lame', 
                    '-b:a', '128k',
                    str(output_path), '-y'
                ], check=True, capture_output=True)
                
                # 删除临时WAV文件
                os.remove(temp_wav)
                
            except subprocess.CalledProcessError as e:
                print(f"❌ MP3转换失败: {e}")
                print(f"💾 WAV文件已保存: {temp_wav}")
                return False
        
        end_time = time.time()
        
        # 检查输出文件
        if output_path.exists():
            file_size = output_path.stat().st_size / 1024 / 1024  # MB
            print(f"✅ 转换成功！")
            print(f"📁 输出文件: {output_path}")
            print(f"📊 文件大小: {file_size:.2f} MB")
            print(f"⏱️  耗时: {end_time - start_time:.1f} 秒")
            return True
        else:
            print("❌ 转换失败：输出文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 转换过程中出现错误: {str(e)}")
        return False

def batch_convert_improved(folder_path, output_folder=None, **kwargs):
    """改进版批量转换函数"""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ 错误：文件夹 {folder_path} 不存在")
        return
    
    if output_folder is None:
        output_folder = folder / "audio_output"
    else:
        output_folder = Path(output_folder)
    
    # 创建输出文件夹
    output_folder.mkdir(exist_ok=True)
    
    txt_files = list(folder.glob("*.txt"))
    if not txt_files:
        print("❌ 在指定文件夹中没有找到txt文件")
        return
    
    print(f"📁 找到 {len(txt_files)} 个txt文件")
    print(f"📁 输出文件夹: {output_folder}")
    
    success_count = 0
    for i, txt_file in enumerate(txt_files, 1):
        print(f"\n{'='*50}")
        print(f"📄 正在处理第 {i}/{len(txt_files)} 个文件: {txt_file.name}")
        
        output_path = output_folder / f"{txt_file.stem}.wav"
        if txt_to_audio_improved(str(txt_file), str(output_path), **kwargs):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"🎉 批量转换完成！")
    print(f"✅ 成功: {success_count}/{len(txt_files)} 个文件")

def install_missing_dependencies():
    """安装缺失的依赖"""
    print("🔧 正在检查和安装依赖...")
    
    try:
        import pyttsx3
        print("✅ pyttsx3 已安装")
    except ImportError:
        print("📦 正在安装 pyttsx3...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyttsx3"])
    
    try:
        import pydub
        print("✅ pydub 已安装")
    except ImportError:
        print("📦 正在安装 pydub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydub"])

def show_ffmpeg_install_guide():
    """显示FFmpeg安装指南"""
    print("\n" + "="*60)
    print("📋 FFmpeg 安装指南")
    print("="*60)
    print("FFmpeg用于生成MP3格式音频文件。如果您只需要WAV格式，可以跳过此步骤。")
    print("\n🪟 Windows用户:")
    print("1. 访问 https://ffmpeg.org/download.html")
    print("2. 下载 Windows 版本")
    print("3. 解压到文件夹（如 C:\\ffmpeg）")
    print("4. 将 C:\\ffmpeg\\bin 添加到系统PATH环境变量")
    print("5. 重启命令提示符")
    print("\n🐧 Linux用户:")
    print("sudo apt update && sudo apt install ffmpeg")
    print("\n🍎 macOS用户:")
    print("brew install ffmpeg")
    print("\n💡 或者使用在线工具将WAV转换为MP3:")
    print("- https://convertio.co/zh/wav-mp3/")
    print("- https://www.online-convert.com/")

def main():
    """主函数"""
    print("🎵 TXT转MP3工具 - 改进版")
    print("="*40)
    
    # 检查依赖
    try:
        install_missing_dependencies()
    except Exception as e:
        print(f"❌ 依赖安装失败: {e}")
        return
    
    # 检查FFmpeg
    if not check_ffmpeg():
        print("\n⚠️  FFmpeg未安装或不可用")
        choice = input("是否查看FFmpeg安装指南？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            show_ffmpeg_install_guide()
        print("\n💡 程序将生成WAV格式音频文件")
    
    print("\n请选择操作模式:")
    print("1. 转换单个文件")
    print("2. 批量转换文件夹")
    print("3. 快速转换（使用默认设置）")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        # 单文件转换
        txt_file = input("请输入txt文件路径: ").strip()
        if not txt_file:
            # 查找当前目录的txt文件
            txt_files = list(Path(".").glob("*.txt"))
            if txt_files:
                print(f"发现文件: {txt_files[0]}")
                txt_file = str(txt_files[0])
            else:
                print("❌ 未指定文件且当前目录无txt文件")
                return
        
        output_file = input("输出文件路径（回车使用默认）: ").strip() or None
        
        try:
            rate = int(input("语音速度 (50-300, 默认180): ").strip() or "180")
            volume = float(input("音量 (0.0-1.0, 默认0.9): ").strip() or "0.9")
            prefer_mp3 = input("优先生成MP3格式？(y/n, 默认n): ").lower().strip() in ['y', 'yes', '是']
        except ValueError:
            rate, volume, prefer_mp3 = 180, 0.9, False
        
        success = txt_to_audio_improved(txt_file, output_file, rate, volume, prefer_mp3)
        print(f"\n{'✅ 转换完成！' if success else '❌ 转换失败！'}")
    
    elif choice == "2":
        # 批量转换
        folder = input("输入包含txt文件的文件夹路径（回车使用当前目录）: ").strip() or "."
        output_folder = input("输出文件夹路径（回车使用默认）: ").strip() or None
        
        try:
            rate = int(input("语音速度 (50-300, 默认180): ").strip() or "180")
            volume = float(input("音量 (0.0-1.0, 默认0.9): ").strip() or "0.9")
        except ValueError:
            rate, volume = 180, 0.9
        
        batch_convert_improved(folder, output_folder, voice_rate=rate, voice_volume=volume)
    
    elif choice == "3":
        # 快速转换
        txt_files = list(Path(".").glob("*.txt"))
        if not txt_files:
            print("❌ 当前目录没有找到txt文件")
            return
        
        print(f"🚀 快速转换模式，发现 {len(txt_files)} 个文件")
        for txt_file in txt_files:
            print(f"\n📄 转换: {txt_file.name}")
            txt_to_audio_improved(str(txt_file))
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序出现错误: {e}")
    finally:
        input("\n按回车键退出...")