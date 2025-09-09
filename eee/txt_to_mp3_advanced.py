import pyttsx3
import os
from pathlib import Path
import time
import re

def split_text_into_chunks(text, max_chunk_size=1000):
    """
    将长文本分割成较小的块，以便更好地处理大文件
    """
    # 按句子分割（中文句号、英文句号、问号、感叹号）
    sentences = re.split(r'[。！？.!?]', text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # 如果当前块加上新句子不超过限制，就添加
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + "。"
        else:
            # 保存当前块，开始新块
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + "。"
    
    # 添加最后一块
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def txt_to_mp3_large_file(txt_file_path, output_mp3_path=None, voice_rate=200, voice_volume=0.9, chunk_size=1000):
    """
    处理大文件的txt转MP3功能
    将大文件分块处理，避免内存问题
    """
    
    if not os.path.exists(txt_file_path):
        print(f"错误：找不到文件 {txt_file_path}")
        return False
    
    if output_mp3_path is None:
        txt_path = Path(txt_file_path)
        output_mp3_path = txt_path.with_suffix('.wav')  # 默认生成WAV
    
    try:
        # 读取文件大小
        file_size = os.path.getsize(txt_file_path)
        print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
        
        # 分块读取文件
        print("正在分块读取大文件...")
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        if not text.strip():
            print("错误：文件内容为空")
            return False
        
        print(f"文件内容长度: {len(text)} 字符")
        
        # 将文本分割成块
        print("正在分割文本...")
        chunks = split_text_into_chunks(text, chunk_size)
        print(f"文本已分割为 {len(chunks)} 个块")
        
        # 初始化TTS引擎
        print("正在初始化语音引擎...")
        engine = pyttsx3.init()
        engine.setProperty('rate', voice_rate)
        engine.setProperty('volume', voice_volume)
        
        # 设置语音
        voices = engine.getProperty('voices')
        if voices:
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    print(f"使用语音: {voice.name}")
                    break
            else:
                engine.setProperty('voice', voices[0].id)
                print(f"使用默认语音: {voices[0].name}")
        
        # 创建临时文件夹
        temp_folder = Path("temp_audio_chunks")
        temp_folder.mkdir(exist_ok=True)
        
        # 逐块转换
        chunk_files = []
        for i, chunk in enumerate(chunks):
            print(f"正在处理第 {i+1}/{len(chunks)} 块...")
            
            chunk_file = temp_folder / f"chunk_{i:04d}.wav"
            engine.save_to_file(chunk, str(chunk_file))
            engine.runAndWait()
            
            chunk_files.append(str(chunk_file))
            
            # 显示进度
            progress = (i + 1) / len(chunks) * 100
            print(f"进度: {progress:.1f}%")
        
        print("正在合并音频文件...")
        
        # 合并音频文件（需要pydub库）
        try:
            from pydub import AudioSegment
            
            # 合并所有音频块
            combined = AudioSegment.empty()
            for chunk_file in chunk_files:
                audio_chunk = AudioSegment.from_wav(chunk_file)
                combined += audio_chunk
                combined += AudioSegment.silent(duration=500)  # 添加0.5秒静音间隔
            
            # 导出最终文件
            if str(output_mp3_path).endswith('.mp3'):
                combined.export(str(output_mp3_path), format="mp3")
            else:
                combined.export(str(output_mp3_path), format="wav")
            
            print(f"音频文件已生成: {output_mp3_path}")
            
        except ImportError:
            print("警告：未安装pydub库，无法合并音频文件")
            print("音频块文件保存在 temp_audio_chunks 文件夹中")
            print("请安装pydub库: pip install pydub")
            return False
        
        # 清理临时文件
        print("正在清理临时文件...")
        for chunk_file in chunk_files:
            try:
                os.remove(chunk_file)
            except:
                pass
        
        try:
            temp_folder.rmdir()
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"转换过程中出现错误: {str(e)}")
        return False

def show_file_preview(txt_file_path, lines=10):
    """
    显示文件前几行内容预览
    """
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            preview_lines = []
            for i, line in enumerate(file):
                if i >= lines:
                    break
                preview_lines.append(line.strip())
        
        print(f"\n文件预览（前{lines}行）:")
        print("-" * 50)
        for i, line in enumerate(preview_lines, 1):
            print(f"{i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
        print("-" * 50)
        
    except Exception as e:
        print(f"无法预览文件: {str(e)}")

if __name__ == "__main__":
    print("=== 大文件TXT转MP3工具 ===")
    
    # 默认使用当前目录的txt文件
    txt_files = list(Path(".").glob("*.txt"))
    
    if txt_files:
        print(f"\n找到以下txt文件:")
        for i, file in enumerate(txt_files, 1):
            file_size = os.path.getsize(file) / 1024 / 1024
            print(f"{i}. {file.name} ({file_size:.2f} MB)")
        
        try:
            choice = int(input(f"\n请选择要转换的文件 (1-{len(txt_files)}): "))
            if 1 <= choice <= len(txt_files):
                selected_file = txt_files[choice - 1]
            else:
                print("无效选择，使用第一个文件")
                selected_file = txt_files[0]
        except ValueError:
            print("无效输入，使用第一个文件")
            selected_file = txt_files[0]
    else:
        selected_file = input("请输入txt文件路径: ").strip()
        if not selected_file:
            print("未指定文件")
            exit()
        selected_file = Path(selected_file)
    
    # 显示文件预览
    show_file_preview(selected_file)
    
    # 设置参数
    print(f"\n选择的文件: {selected_file}")
    
    output_file = input("输出文件名（直接回车使用默认）: ").strip()
    if not output_file:
        output_file = selected_file.with_suffix('.wav')
    
    try:
        rate = int(input("语音速度 (50-300, 默认180): ").strip() or "180")
        volume = float(input("音量 (0.0-1.0, 默认0.9): ").strip() or "0.9")
        chunk_size = int(input("分块大小 (500-2000字符, 默认800): ").strip() or "800")
    except ValueError:
        rate, volume, chunk_size = 180, 0.9, 800
    
    print(f"\n开始转换...")
    print(f"输入文件: {selected_file}")
    print(f"输出文件: {output_file}")
    print(f"语音速度: {rate}")
    print(f"音量: {volume}")
    print(f"分块大小: {chunk_size}")
    
    start_time = time.time()
    success = txt_to_mp3_large_file(str(selected_file), str(output_file), rate, volume, chunk_size)
    end_time = time.time()
    
    if success:
        print(f"\n✓ 转换完成！")
        print(f"耗时: {end_time - start_time:.1f} 秒")
    else:
        print(f"\n✗ 转换失败！")
    
    input("\n按回车键退出...")