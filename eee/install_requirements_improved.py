#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
改进版依赖安装脚本
解决FFmpeg和Python包的安装问题
"""

import subprocess
import sys
import os
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

def run_command(command, capture_output=True, check=True):
    """安全地运行命令"""
    try:
        result = subprocess.run(
            command, 
            capture_output=capture_output, 
            check=check, 
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print("⏰ 命令执行超时")
        return False, "", "超时"
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except FileNotFoundError:
        return False, "", "命令未找到"

def install_python_package(package_name, display_name=None):
    """安装Python包"""
    if display_name is None:
        display_name = package_name
    
    print(f"📦 正在安装 {display_name}...")
    
    # 尝试多种安装方式
    install_commands = [
        [sys.executable, "-m", "pip", "install", package_name],
        [sys.executable, "-m", "pip", "install", "--user", package_name],
        ["pip", "install", package_name],
        ["pip3", "install", package_name]
    ]
    
    for cmd in install_commands:
        success, stdout, stderr = run_command(cmd)
        if success:
            print(f"✅ {display_name} 安装成功")
            return True
        else:
            print(f"⚠️  尝试命令失败: {' '.join(cmd)}")
    
    print(f"❌ {display_name} 安装失败")
    print(f"错误信息: {stderr}")
    return False

def check_python_package(package_name):
    """检查Python包是否已安装"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def check_ffmpeg():
    """检查FFmpeg是否已安装"""
    success, _, _ = run_command(["ffmpeg", "-version"])
    return success

def download_ffmpeg_windows():
    """为Windows下载FFmpeg"""
    print("🔽 正在下载FFmpeg for Windows...")
    
    # FFmpeg下载URL（使用GitHub releases）
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        # 创建临时目录
        temp_dir = Path("temp_ffmpeg")
        temp_dir.mkdir(exist_ok=True)
        
        zip_path = temp_dir / "ffmpeg.zip"
        
        print("📥 正在下载FFmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        print("📂 正在解压FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 查找ffmpeg.exe
        ffmpeg_exe = None
        for root, dirs, files in os.walk(temp_dir):
            if "ffmpeg.exe" in files:
                ffmpeg_exe = Path(root) / "ffmpeg.exe"
                break
        
        if ffmpeg_exe and ffmpeg_exe.exists():
            # 创建本地ffmpeg目录
            local_ffmpeg_dir = Path("ffmpeg_local")
            local_ffmpeg_dir.mkdir(exist_ok=True)
            
            # 复制ffmpeg.exe
            shutil.copy2(ffmpeg_exe, local_ffmpeg_dir / "ffmpeg.exe")
            
            print(f"✅ FFmpeg已下载到: {local_ffmpeg_dir.absolute()}")
            print("💡 请将此路径添加到系统PATH环境变量中")
            
            # 清理临时文件
            shutil.rmtree(temp_dir, ignore_errors=True)
            return True
        else:
            print("❌ 在下载的文件中未找到ffmpeg.exe")
            return False
            
    except Exception as e:
        print(f"❌ 下载FFmpeg失败: {e}")
        return False

def install_ffmpeg():
    """安装FFmpeg"""
    system = platform.system().lower()
    
    if system == "windows":
        print("🪟 检测到Windows系统")
        
        # 尝试使用chocolatey安装
        choco_success, _, _ = run_command(["choco", "--version"])
        if choco_success:
            print("🍫 尝试使用Chocolatey安装FFmpeg...")
            success, _, _ = run_command(["choco", "install", "ffmpeg", "-y"])
            if success:
                print("✅ 通过Chocolatey安装FFmpeg成功")
                return True
        
        # 尝试使用winget安装
        winget_success, _, _ = run_command(["winget", "--version"])
        if winget_success:
            print("📦 尝试使用Winget安装FFmpeg...")
            success, _, _ = run_command(["winget", "install", "FFmpeg"])
            if success:
                print("✅ 通过Winget安装FFmpeg成功")
                return True
        
        # 手动下载
        print("📥 尝试手动下载FFmpeg...")
        return download_ffmpeg_windows()
        
    elif system == "linux":
        print("🐧 检测到Linux系统")
        
        # 尝试不同的包管理器
        package_managers = [
            (["sudo", "apt", "update"], ["sudo", "apt", "install", "-y", "ffmpeg"]),
            (["sudo", "yum", "update"], ["sudo", "yum", "install", "-y", "ffmpeg"]),
            (["sudo", "dnf", "update"], ["sudo", "dnf", "install", "-y", "ffmpeg"]),
            (["sudo", "pacman", "-Sy"], ["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"])
        ]
        
        for update_cmd, install_cmd in package_managers:
            print(f"🔄 尝试使用 {install_cmd[1]} 安装FFmpeg...")
            update_success, _, _ = run_command(update_cmd, check=False)
            if update_success:
                install_success, _, _ = run_command(install_cmd)
                if install_success:
                    print("✅ FFmpeg安装成功")
                    return True
        
        print("❌ 无法通过包管理器安装FFmpeg")
        return False
        
    elif system == "darwin":
        print("🍎 检测到macOS系统")
        
        # 尝试使用Homebrew
        brew_success, _, _ = run_command(["brew", "--version"])
        if brew_success:
            print("🍺 使用Homebrew安装FFmpeg...")
            success, _, _ = run_command(["brew", "install", "ffmpeg"])
            if success:
                print("✅ 通过Homebrew安装FFmpeg成功")
                return True
        
        print("❌ 请先安装Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    
    else:
        print(f"❌ 不支持的操作系统: {system}")
        return False

def show_manual_install_guide():
    """显示手动安装指南"""
    print("\n" + "="*60)
    print("📋 手动安装指南")
    print("="*60)
    
    system = platform.system().lower()
    
    if system == "windows":
        print("🪟 Windows用户:")
        print("1. 访问 https://ffmpeg.org/download.html")
        print("2. 点击 'Windows' 下的 'Windows builds by BtbN'")
        print("3. 下载 'ffmpeg-master-latest-win64-gpl.zip'")
        print("4. 解压到文件夹（如 C:\\ffmpeg）")
        print("5. 将 C:\\ffmpeg\\bin 添加到系统PATH环境变量:")
        print("   - 右键'此电脑' -> 属性 -> 高级系统设置")
        print("   - 环境变量 -> 系统变量 -> Path -> 编辑 -> 新建")
        print("   - 输入 C:\\ffmpeg\\bin -> 确定")
        print("6. 重启命令提示符测试: ffmpeg -version")
        
    elif system == "linux":
        print("🐧 Linux用户:")
        print("Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
        print("CentOS/RHEL: sudo yum install ffmpeg")
        print("Fedora: sudo dnf install ffmpeg")
        print("Arch: sudo pacman -S ffmpeg")
        
    elif system == "darwin":
        print("🍎 macOS用户:")
        print("1. 安装Homebrew:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("2. 安装FFmpeg:")
        print("   brew install ffmpeg")

def main():
    """主函数"""
    print("🔧 TXT转MP3工具 - 改进版依赖安装")
    print("="*50)
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"🐍 Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 7):
        print("⚠️  警告：建议使用Python 3.7或更高版本")
    
    # 安装Python包
    print("\n📦 安装Python依赖包...")
    
    packages = [
        ("pyttsx3", "文本转语音引擎"),
        ("pydub", "音频处理库")
    ]
    
    python_success_count = 0
    for package, description in packages:
        if check_python_package(package):
            print(f"✅ {description} ({package}) 已安装")
            python_success_count += 1
        else:
            if install_python_package(package, description):
                python_success_count += 1
    
    print(f"\n📊 Python包安装结果: {python_success_count}/{len(packages)} 成功")
    
    # 检查和安装FFmpeg
    print("\n🎬 检查FFmpeg...")
    
    if check_ffmpeg():
        print("✅ FFmpeg已安装并可用")
        ffmpeg_success = True
    else:
        print("❌ FFmpeg未安装")
        
        choice = input("\n是否尝试自动安装FFmpeg？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            ffmpeg_success = install_ffmpeg()
            
            # 再次检查
            if not ffmpeg_success:
                ffmpeg_success = check_ffmpeg()
        else:
            ffmpeg_success = False
    
    # 显示最终结果
    print("\n" + "="*50)
    print("📋 安装结果总结")
    print("="*50)
    
    print(f"🐍 Python包: {python_success_count}/{len(packages)} 成功")
    for package, description in packages:
        status = "✅" if check_python_package(package) else "❌"
        print(f"   {status} {description} ({package})")
    
    print(f"🎬 FFmpeg: {'✅ 可用' if check_ffmpeg() else '❌ 不可用'}")
    
    if not check_ffmpeg():
        print("\n⚠️  FFmpeg未安装，程序将只能生成WAV格式音频")
        choice = input("是否查看手动安装指南？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            show_manual_install_guide()
    
    # 测试建议
    if python_success_count == len(packages):
        print(f"\n🎉 所有Python依赖已安装完成！")
        print(f"💡 现在可以运行: python txt_to_mp3_improved.py")
    else:
        print(f"\n⚠️  部分依赖安装失败，可能影响程序运行")
    
    print(f"\n💡 提示：")
    print(f"   - 如果遇到权限问题，尝试以管理员身份运行")
    print(f"   - 如果网络问题导致下载失败，可以使用国内镜像:")
    print(f"     pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ pyttsx3 pydub")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消安装")
    except Exception as e:
        print(f"\n❌ 安装过程出现错误: {e}")
    finally:
        input("\n按回车键退出...")