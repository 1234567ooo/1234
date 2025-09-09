#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TXT转MP3工具启动器
帮助用户选择最合适的转换方案
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filename):
    """检查文件是否存在"""
    return Path(filename).exists()

def check_python_package(package_name):
    """检查Python包是否已安装"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

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
    except:
        return False

def run_script(script_name):
    """运行指定的脚本"""
    if not check_file_exists(script_name):
        print(f"❌ 错误：找不到脚本文件 {script_name}")
        return False
    
    try:
        print(f"🚀 正在启动 {script_name}...")
        subprocess.run([sys.executable, script_name], check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ 脚本 {script_name} 运行失败")
        return False
    except KeyboardInterrupt:
        print(f"\n👋 用户取消了 {script_name} 的运行")
        return False

def show_system_status():
    """显示系统状态"""
    print("🔍 系统环境检查:")
    print("="*40)
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"🐍 Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查依赖包
    pyttsx3_status = "✅ 已安装" if check_python_package("pyttsx3") else "❌ 未安装"
    pydub_status = "✅ 已安装" if check_python_package("pydub") else "❌ 未安装"
    
    print(f"📦 pyttsx3: {pyttsx3_status}")
    print(f"📦 pydub: {pydub_status}")
    
    # 检查FFmpeg
    ffmpeg_status = "✅ 可用" if check_ffmpeg() else "❌ 不可用"
    print(f"🎬 FFmpeg: {ffmpeg_status}")
    
    # 检查txt文件
    txt_files = list(Path(".").glob("*.txt"))
    print(f"📄 当前目录txt文件: {len(txt_files)} 个")
    
    if txt_files:
        print("   发现的文件:")
        for i, file in enumerate(txt_files[:3], 1):  # 只显示前3个
            file_size = file.stat().st_size / 1024  # KB
            print(f"   {i}. {file.name} ({file_size:.1f} KB)")
        if len(txt_files) > 3:
            print(f"   ... 还有 {len(txt_files) - 3} 个文件")
    
    print("="*40)

def show_recommendations():
    """显示推荐方案"""
    pyttsx3_installed = check_python_package("pyttsx3")
    pydub_installed = check_python_package("pydub")
    ffmpeg_available = check_ffmpeg()
    
    print("\n💡 推荐方案:")
    print("="*40)
    
    if not pyttsx3_installed:
        print("🔧 首先需要安装依赖:")
        print("   推荐运行: 改进版依赖安装脚本")
        print("   或手动安装: pip install pyttsx3")
        return "install"
    
    elif not ffmpeg_available:
        print("🌟 推荐使用: 简化版WAV转换")
        print("   原因: 无需FFmpeg，避免依赖问题")
        print("   输出: WAV格式（可在线转MP3）")
        return "simple"
    
    elif ffmpeg_available and pydub_installed:
        print("🎯 推荐使用: 改进版完整功能")
        print("   原因: 所有依赖已安装")
        print("   输出: 支持MP3和WAV格式")
        return "improved"
    
    else:
        print("⚡ 推荐使用: 简化版WAV转换")
        print("   原因: 快速可靠，兼容性好")
        return "simple"

def main():
    """主函数"""
    print("🎵 TXT转MP3工具启动器")
    print("="*50)
    print("帮助您选择最合适的转换方案")
    
    # 显示系统状态
    show_system_status()
    
    # 显示推荐方案
    recommendation = show_recommendations()
    
    print("\n📋 可用的转换脚本:")
    print("="*40)
    
    scripts = [
        ("install_requirements_improved.py", "🔧 改进版依赖安装", "安装所有必要依赖"),
        ("txt_to_wav_simple.py", "🌟 简化版WAV转换", "推荐：无需FFmpeg"),
        ("txt_to_mp3_improved.py", "🎯 改进版完整功能", "支持MP3，需要FFmpeg"),
        ("txt_to_mp3_advanced.py", "⚡ 高级版大文件处理", "处理超大文件"),
        ("txt_to_mp3.py", "📝 原版基础转换", "基本功能"),
        ("示例_简单转换.py", "🎓 快速示例", "学习和测试")
    ]
    
    available_scripts = []
    for i, (script, name, desc) in enumerate(scripts, 1):
        if check_file_exists(script):
            print(f"{i}. {name}")
            print(f"   文件: {script}")
            print(f"   说明: {desc}")
            available_scripts.append((i, script, name))
            print()
    
    if not available_scripts:
        print("❌ 没有找到可用的转换脚本")
        return
    
    # 根据推荐给出建议
    if recommendation == "install":
        print("💡 建议: 先运行选项 1 安装依赖")
    elif recommendation == "simple":
        print("💡 建议: 选择选项 2 (简化版WAV转换)")
    elif recommendation == "improved":
        print("💡 建议: 选择选项 3 (改进版完整功能)")
    
    print("\n" + "="*50)
    
    # 用户选择
    try:
        choice = input("请选择要运行的脚本编号 (直接回车使用推荐方案): ").strip()
        
        if not choice:
            # 使用推荐方案
            if recommendation == "install":
                script_to_run = "install_requirements_improved.py"
            elif recommendation == "simple":
                script_to_run = "txt_to_wav_simple.py"
            elif recommendation == "improved":
                script_to_run = "txt_to_mp3_improved.py"
            else:
                script_to_run = "txt_to_wav_simple.py"
            
            print(f"🎯 使用推荐方案: {script_to_run}")
        else:
            choice_num = int(choice)
            script_found = False
            for num, script, name in available_scripts:
                if num == choice_num:
                    script_to_run = script
                    script_found = True
                    break
            
            if not script_found:
                print("❌ 无效选择")
                return
        
        # 运行选择的脚本
        success = run_script(script_to_run)
        
        if success:
            print(f"\n✅ {script_to_run} 运行完成")
        else:
            print(f"\n❌ {script_to_run} 运行失败")
            
    except ValueError:
        print("❌ 请输入有效的数字")
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")

def show_quick_help():
    """显示快速帮助"""
    print("\n" + "="*50)
    print("📚 快速帮助")
    print("="*50)
    print("🌟 新手推荐流程:")
    print("   1. 运行启动器 → python 启动器.py")
    print("   2. 选择简化版WAV转换")
    print("   3. 转换完成后在线转MP3")
    print()
    print("🎯 进阶用户流程:")
    print("   1. 先安装依赖 → 改进版依赖安装")
    print("   2. 使用完整功能 → 改进版完整功能")
    print()
    print("💡 在线MP3转换推荐:")
    print("   - https://convertio.co/zh/wav-mp3/")
    print("   - https://www.online-convert.com/")
    print()
    print("📖 详细说明请查看: 使用说明_改进版.md")

if __name__ == "__main__":
    try:
        main()
        
        # 询问是否需要帮助
        help_choice = input("\n是否需要查看快速帮助？(y/n): ").lower().strip()
        if help_choice in ['y', 'yes', '是']:
            show_quick_help()
            
    except Exception as e:
        print(f"\n❌ 启动器出现错误: {e}")
    finally:
        input("\n按回车键退出...")