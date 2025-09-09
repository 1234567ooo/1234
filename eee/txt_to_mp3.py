import pyttsx3
import os
from pathlib import Path
import time

def txt_to_mp3(txt_file_path, output_mp3_path=None, voice_rate=200, voice_volume=0.9):
    """
    将txt文件转换为MP3音频文件
    
    参数:
    txt_file_path: txt文件路径
    output_mp3_path: 输出MP3文件路径（可选，默认与txt文件同名）
    voice_rate: 语音速度（默认200，范围50-300）
    voice_volume: 音量（默认0.9，范围0.0-1.0）
    """
    
    # 检查txt文件是否存在
    if not os.path.exists(txt_file_path):
        print(f"错误：找不到文件 {txt_file_path}")
        return False
    
    # 如果没有指定输出路径，使用与txt文件相同的名称
    if output_mp3_path is None:
        txt_path = Path(txt_file_path)
        output_mp3_path = txt_path.with_suffix('.mp3')
    
    try:
        # 读取txt文件内容
        print(f"正在读取文件: {txt_file_path}")
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        if not text.strip():
            print("错误：文件内容为空")
            return False
        
        print(f"文件内容长度: {len(text)} 字符")
        
        # 初始化TTS引擎
        print("正在初始化语音引擎...")
        engine = pyttsx3.init()
        
        # 设置语音属性
        engine.setProperty('rate', voice_rate)  # 语音速度
        engine.setProperty('volume', voice_volume)  # 音量
        
        # 获取可用的语音
        voices = engine.getProperty('voices')
        if voices:
            # 尝试选择中文语音（如果有的话）
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    print(f"使用语音: {voice.name}")
                    break
            else:
                # 如果没有中文语音，使用默认语音
                engine.setProperty('voice', voices[0].id)
                print(f"使用默认语音: {voices[0].name}")
        
        # 将文本转换为语音并保存为MP3
        print(f"正在转换为语音文件: {output_mp3_path}")
        print("这可能需要一些时间，请耐心等待...")
        
        # 保存为wav文件（pyttsx3不直接支持MP3）
        wav_path = str(Path(output_mp3_path).with_suffix('.wav'))
        engine.save_to_file(text, wav_path)
        engine.runAndWait()
        
        print(f"语音文件已生成: {wav_path}")
        
        # 如果需要MP3格式，需要转换（需要安装ffmpeg）
        if str(output_mp3_path).endswith('.mp3'):
            try:
                import subprocess
                print("正在转换为MP3格式...")
                subprocess.run([
                    'ffmpeg', '-i', wav_path, '-acodec', 'mp3', 
                    str(output_mp3_path), '-y'
                ], check=True, capture_output=True)
                
                # 删除临时wav文件
                os.remove(wav_path)
                print(f"MP3文件已生成: {output_mp3_path}")
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("注意：无法转换为MP3格式（需要安装ffmpeg）")
                print(f"WAV格式的音频文件已保存: {wav_path}")
                print("你可以使用在线工具将WAV转换为MP3")
        
        return True
        
    except Exception as e:
        print(f"转换过程中出现错误: {str(e)}")
        return False

def batch_convert(folder_path, output_folder=None):
    """
    批量转换文件夹中的所有txt文件
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"错误：文件夹 {folder_path} 不存在")
        return
    
    if output_folder is None:
        output_folder = folder / "audio_output"
    else:
        output_folder = Path(output_folder)
    
    # 创建输出文件夹
    output_folder.mkdir(exist_ok=True)
    
    txt_files = list(folder.glob("*.txt"))
    if not txt_files:
        print("在指定文件夹中没有找到txt文件")
        return
    
    print(f"找到 {len(txt_files)} 个txt文件")
    
    for i, txt_file in enumerate(txt_files, 1):
        print(f"\n正在处理第 {i}/{len(txt_files)} 个文件: {txt_file.name}")
        output_path = output_folder / f"{txt_file.stem}.mp3"
        txt_to_mp3(str(txt_file), str(output_path))

if __name__ == "__main__":
    print("=== TXT转MP3工具 ===")
    print("1. 转换单个文件")
    print("2. 批量转换文件夹中的所有txt文件")
    
    choice = input("请选择操作 (1/2): ").strip()
    
    if choice == "1":
        # 单个文件转换
        txt_file = input("请输入txt文件路径: ").strip()
        if not txt_file:
            txt_file = "镇国驸马爷-魔力阅读网(MOLIYD.COM).txt"  # 默认文件
        
        output_file = input("请输入输出MP3文件路径（直接回车使用默认路径）: ").strip()
        if not output_file:
            output_file = None
        
        # 设置语音参数
        try:
            rate = int(input("请输入语音速度 (50-300, 默认200): ").strip() or "200")
            volume = float(input("请输入音量 (0.0-1.0, 默认0.9): ").strip() or "0.9")
        except ValueError:
            rate, volume = 200, 0.9
        
        success = txt_to_mp3(txt_file, output_file, rate, volume)
        if success:
            print("\n转换完成！")
        else:
            print("\n转换失败！")
    
    elif choice == "2":
        # 批量转换
        folder = input("请输入包含txt文件的文件夹路径（直接回车使用当前目录）: ").strip()
        if not folder:
            folder = "."
        
        output_folder = input("请输入输出文件夹路径（直接回车使用默认路径）: ").strip()
        if not output_folder:
            output_folder = None
        
        batch_convert(folder, output_folder)
        print("\n批量转换完成！")
    
    else:
        print("无效选择！")
    
    input("\n按回车键退出...")