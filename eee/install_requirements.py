import subprocess
import sys
import os

def install_package(package):
    """安装Python包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ {package} 安装失败")
        return False

def check_ffmpeg():
    """检查ffmpeg是否已安装"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✓ FFmpeg 已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ FFmpeg 未安装")
        return False

def main():
    print("=== TXT转MP3工具 - 依赖安装 ===\n")
    
    # 需要安装的Python包
    packages = [
        "pyttsx3",  # 文本转语音
        "pydub",    # 音频处理
    ]
    
    print("正在安装Python依赖包...")
    success_count = 0
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\nPython包安装完成: {success_count}/{len(packages)} 成功")
    
    # 检查FFmpeg
    print("\n检查FFmpeg（用于MP3转换）...")
    if not check_ffmpeg():
        print("\n注意：FFmpeg未安装，无法直接生成MP3文件")
        print("程序将生成WAV格式的音频文件")
        print("\n如需MP3格式，请按以下方式安装FFmpeg：")
        print("1. 访问 https://ffmpeg.org/download.html")
        print("2. 下载适合你系统的版本")
        print("3. 将ffmpeg.exe添加到系统PATH环境变量中")
        print("\n或者使用在线工具将WAV转换为MP3")
    
    print("\n安装完成！现在可以运行 txt_to_mp3.py 了")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")