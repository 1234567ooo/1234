#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版TXT转WAV工具
无需FFmpeg依赖，直接生成WAV格式音频
专门解决FFmpeg警告问题
"""

import pyttsx3
import os
import sys
import warnings
from pathlib import Path
import time

# 抑制所有警告
warnings.filterwarnings("ignore")

def txt_to_wav_simple(txt_file_path, output_wav_path=None, voice_rate=180, voice_volume=0.9):
    """
    简单的文本转WAV函数，无需FFmpeg
    
    参数:
    txt_file_path: 输入文本文件路径
    output_wav_path: 输出WAV文件路径
    voice_rate: 语音速度 (50-300)
    voice_volume: 音量 (0.0-1.0)
    """
    
    # 检查输入文件
    if not os.path.exists(txt_file_path):
        print(f"❌ 错误：找不到文件 {txt_file_path}")
        return False
    
    # 确定输出路径
    if output_wav_path is None:
        txt_path = Path(txt_file_path)
        output_wav_path = txt_path.with_suffix('.wav')
    else:
        output_wav_path = Path(output_wav_path)
        # 确保输出文件是WAV格式
        if not str(output_wav_path).endswith('.wav'):
            output_wav_path = output_wav_path.with_suffix('.wav')
    
    try:
        # 读取文本文件
        print(f"📖 正在读取文件: {txt_file_path}")
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        if not text.strip():
            print("❌ 错误：文件内容为空")
            return False
        
        print(f"📝 文件内容长度: {len(text)} 字符")
        
        # 如果文本太长，给出提示
        if len(text) > 10000:
            print("⚠️  文件较大，转换可能需要较长时间")
            choice = input("是否继续？(y/n): ").lower().strip()
            if choice not in ['y', 'yes', '是']:
                print("❌ 用户取消转换")
                return False
        
        # 初始化TTS引擎
        print("🎤 正在初始化语音引擎...")
        engine = pyttsx3.init()
        
        # 设置语音属性
        engine.setProperty('rate', voice_rate)
        engine.setProperty('volume', voice_volume)
        
        # 选择最佳语音
        voices = engine.getProperty('voices')
        if voices:
            print(f"🔍 发现 {len(voices)} 个可用语音:")
            
            chinese_voice = None
            for i, voice in enumerate(voices):
                voice_name = voice.name
                print(f"   {i+1}. {voice_name}")
                
                # 检查是否为中文语音
                if any(keyword in voice_name.lower() for keyword in ['chinese', 'mandarin', 'zh', '中文', 'china']):
                    chinese_voice = voice
            
            if chinese_voice:
                engine.setProperty('voice', chinese_voice.id)
                print(f"🗣️  自动选择中文语音: {chinese_voice.name}")
            else:
                engine.setProperty('voice', voices[0].id)
                print(f"🗣️  使用默认语音: {voices[0].name}")
                print("💡 提示：如需更好的中文发音，请在系统中安装中文语音包")
        else:
            print("⚠️  未发现可用语音，使用系统默认设置")
        
        # 转换为音频
        print(f"🔄 正在转换为WAV音频文件...")
        print(f"📁 输出路径: {output_wav_path}")
        print("⏳ 请耐心等待，转换可能需要一些时间...")
        
        start_time = time.time()
        
        # 保存为WAV文件
        engine.save_to_file(text, str(output_wav_path))
        engine.runAndWait()
        
        end_time = time.time()
        
        # 检查输出文件
        if output_wav_path.exists():
            file_size = output_wav_path.stat().st_size / 1024 / 1024  # MB
            print(f"✅ 转换成功！")
            print(f"📁 输出文件: {output_wav_path}")
            print(f"📊 文件大小: {file_size:.2f} MB")
            print(f"⏱️  耗时: {end_time - start_time:.1f} 秒")
            print(f"🎵 可以使用任何音频播放器播放WAV文件")
            return True
        else:
            print("❌ 转换失败：输出文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 转换过程中出现错误: {str(e)}")
        print("💡 可能的解决方案:")
        print("   1. 检查文件编码是否为UTF-8")
        print("   2. 确保有足够的磁盘空间")
        print("   3. 检查文件路径是否包含特殊字符")
        return False

def batch_convert_simple(folder_path=".", output_folder=None):
    """简单批量转换函数"""
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ 错误：文件夹 {folder_path} 不存在")
        return
    
    if output_folder is None:
        output_folder = folder / "wav_output"
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
        if txt_to_wav_simple(str(txt_file), str(output_path)):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"🎉 批量转换完成！")
    print(f"✅ 成功: {success_count}/{len(txt_files)} 个文件")

def check_dependencies():
    """检查依赖"""
    try:
        import pyttsx3
        print("✅ pyttsx3 可用")
        return True
    except ImportError:
        print("❌ pyttsx3 未安装")
        print("📦 请运行: pip install pyttsx3")
        return False

def main():
    """主函数"""
    print("🎵 简化版TXT转WAV工具")
    print("="*40)
    print("💡 此版本无需FFmpeg，直接生成WAV格式音频")
    print("💡 WAV文件可以用任何播放器播放，也可在线转换为MP3")
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 缺少必要依赖，程序无法运行")
        input("按回车键退出...")
        return
    
    print("\n请选择操作模式:")
    print("1. 转换单个文件")
    print("2. 批量转换当前目录所有txt文件")
    print("3. 快速转换（自动处理当前目录第一个txt文件）")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        # 单文件转换
        print("\n📄 单文件转换模式")
        
        # 显示当前目录的txt文件
        txt_files = list(Path(".").glob("*.txt"))
        if txt_files:
            print(f"📁 当前目录发现的txt文件:")
            for i, file in enumerate(txt_files, 1):
                file_size = file.stat().st_size / 1024  # KB
                print(f"   {i}. {file.name} ({file_size:.1f} KB)")
        
        txt_file = input("\n请输入txt文件路径（或直接回车选择第一个文件）: ").strip()
        if not txt_file and txt_files:
            txt_file = str(txt_files[0])
            print(f"📄 自动选择: {txt_file}")
        
        if not txt_file:
            print("❌ 未指定文件")
            return
        
        output_file = input("输出WAV文件路径（回车使用默认）: ").strip() or None
        
        try:
            rate = int(input("语音速度 (50-300, 默认180): ").strip() or "180")
            volume = float(input("音量 (0.0-1.0, 默认0.9): ").strip() or "0.9")
        except ValueError:
            rate, volume = 180, 0.9
            print("⚠️  输入无效，使用默认参数")
        
        success = txt_to_wav_simple(txt_file, output_file, rate, volume)
        print(f"\n{'✅ 转换完成！' if success else '❌ 转换失败！'}")
    
    elif choice == "2":
        # 批量转换
        print("\n📁 批量转换模式")
        
        try:
            rate = int(input("语音速度 (50-300, 默认180): ").strip() or "180")
            volume = float(input("音量 (0.0-1.0, 默认0.9): ").strip() or "0.9")
        except ValueError:
            rate, volume = 180, 0.9
        
        # 临时修改全局参数（简化版本）
        batch_convert_simple()
    
    elif choice == "3":
        # 快速转换
        print("\n🚀 快速转换模式")
        txt_files = list(Path(".").glob("*.txt"))
        if not txt_files:
            print("❌ 当前目录没有找到txt文件")
            return
        
        txt_file = txt_files[0]
        print(f"📄 自动选择文件: {txt_file.name}")
        
        success = txt_to_wav_simple(str(txt_file))
        print(f"\n{'✅ 快速转换完成！' if success else '❌ 转换失败！'}")
    
    else:
        print("❌ 无效选择")
    
    # 转换完成后的提示
    print(f"\n💡 转换完成后的建议:")
    print(f"   - WAV文件可以直接播放")
    print(f"   - 如需MP3格式，可使用在线转换工具:")
    print(f"     https://convertio.co/zh/wav-mp3/")
    print(f"     https://www.online-convert.com/")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序出现错误: {e}")
    finally:
        input("\n按回车键退出...")