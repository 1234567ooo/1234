#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
大文件TXT转WAV工具 - 改进版
专门处理超大文件，无需FFmpeg依赖
支持智能分块、进度显示、内存优化
"""

import pyttsx3
import os
import sys
import warnings
import time
import re
from pathlib import Path

# 抑制所有警告
warnings.filterwarnings("ignore")

def get_file_size_mb(file_path):
    """获取文件大小（MB）"""
    return os.path.getsize(file_path) / 1024 / 1024

def split_text_smart(text, max_chunk_size=800):
    """
    智能分割文本，保持语句完整性
    优先按段落分割，再按句子分割
    """
    # 首先按段落分割
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # 如果段落本身就很大，需要进一步分割
        if len(paragraph) > max_chunk_size:
            # 按句子分割
            sentences = re.split(r'[。！？.!?]', paragraph)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # 添加标点
                if not sentence.endswith(('。', '！', '？', '.', '!', '?')):
                    sentence += '。'
                
                # 检查是否可以添加到当前块
                if len(current_chunk) + len(sentence) < max_chunk_size:
                    current_chunk += sentence
                else:
                    # 保存当前块，开始新块
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
        else:
            # 段落不大，直接处理
            if len(current_chunk) + len(paragraph) < max_chunk_size:
                current_chunk += paragraph + '\n'
            else:
                # 保存当前块，开始新块
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n'
    
    # 添加最后一块
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def txt_to_wav_large(txt_file_path, output_wav_path=None, voice_rate=180, voice_volume=0.9, chunk_size=800):
    """
    大文件TXT转WAV函数
    
    参数:
    txt_file_path: 输入文本文件路径
    output_wav_path: 输出WAV文件路径
    voice_rate: 语音速度 (50-300)
    voice_volume: 音量 (0.0-1.0)
    chunk_size: 分块大小（字符数）
    """
    
    # 检查输入文件
    if not os.path.exists(txt_file_path):
        print(f"❌ 错误：找不到文件 {txt_file_path}")
        return False
    
    # 获取文件信息
    file_size_mb = get_file_size_mb(txt_file_path)
    print(f"📁 文件大小: {file_size_mb:.2f} MB")
    
    if file_size_mb > 50:
        print("⚠️  这是一个超大文件，转换可能需要很长时间")
        choice = input("是否继续？(y/n): ").lower().strip()
        if choice not in ['y', 'yes', '是']:
            print("❌ 用户取消转换")
            return False
    
    # 确定输出路径
    if output_wav_path is None:
        txt_path = Path(txt_file_path)
        output_wav_path = txt_path.with_suffix('.wav')
    else:
        output_wav_path = Path(output_wav_path)
        if not str(output_wav_path).endswith('.wav'):
            output_wav_path = output_wav_path.with_suffix('.wav')
    
    try:
        # 读取文本文件
        print(f"📖 正在读取大文件...")
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        
        if not text.strip():
            print("❌ 错误：文件内容为空")
            return False
        
        print(f"📝 文件内容长度: {len(text):,} 字符")
        
        # 智能分割文本
        print(f"🔄 正在智能分割文本（块大小: {chunk_size} 字符）...")
        chunks = split_text_smart(text, chunk_size)
        print(f"📊 文本已分割为 {len(chunks)} 个块")
        
        # 显示分块信息
        total_chars = sum(len(chunk) for chunk in chunks)
        avg_chunk_size = total_chars / len(chunks) if chunks else 0
        print(f"📈 平均块大小: {avg_chunk_size:.0f} 字符")
        
        # 预估时间
        estimated_time = len(chunks) * 3  # 每块大约3秒
        print(f"⏱️  预估转换时间: {estimated_time // 60} 分 {estimated_time % 60} 秒")
        
        # 初始化TTS引擎
        print("🎤 正在初始化语音引擎...")
        engine = pyttsx3.init()
        engine.setProperty('rate', voice_rate)
        engine.setProperty('volume', voice_volume)
        
        # 选择最佳语音
        voices = engine.getProperty('voices')
        if voices:
            chinese_voice = None
            for voice in voices:
                if any(keyword in voice.name.lower() for keyword in ['chinese', 'mandarin', 'zh', '中文']):
                    chinese_voice = voice
                    break
            
            if chinese_voice:
                engine.setProperty('voice', chinese_voice.id)
                print(f"🗣️  使用中文语音: {chinese_voice.name}")
            else:
                engine.setProperty('voice', voices[0].id)
                print(f"🗣️  使用默认语音: {voices[0].name}")
        
        # 创建临时文件夹
        temp_folder = Path("temp_wav_chunks")
        temp_folder.mkdir(exist_ok=True)
        print(f"📁 临时文件夹: {temp_folder}")
        
        # 分块转换
        chunk_files = []
        start_time = time.time()
        
        print(f"\n🔄 开始分块转换...")
        print("="*60)
        
        for i, chunk in enumerate(chunks):
            chunk_start_time = time.time()
            
            print(f"📄 处理第 {i+1}/{len(chunks)} 块 ({len(chunk)} 字符)")
            
            # 生成临时文件名
            chunk_file = temp_folder / f"chunk_{i:04d}.wav"
            
            # 转换当前块
            engine.save_to_file(chunk, str(chunk_file))
            engine.runAndWait()
            
            chunk_files.append(str(chunk_file))
            
            # 显示进度
            progress = (i + 1) / len(chunks) * 100
            chunk_time = time.time() - chunk_start_time
            elapsed_time = time.time() - start_time
            
            if i > 0:
                avg_time_per_chunk = elapsed_time / (i + 1)
                remaining_chunks = len(chunks) - (i + 1)
                eta = remaining_chunks * avg_time_per_chunk
                eta_min = int(eta // 60)
                eta_sec = int(eta % 60)
                
                print(f"✅ 完成 ({chunk_time:.1f}s) | 进度: {progress:.1f}% | 剩余时间: {eta_min}:{eta_sec:02d}")
            else:
                print(f"✅ 完成 ({chunk_time:.1f}s) | 进度: {progress:.1f}%")
            
            # 每10块显示一次内存使用提示
            if (i + 1) % 10 == 0:
                print(f"💾 已处理 {i+1} 块，继续中...")
        
        print("="*60)
        print("🔗 正在合并音频文件...")
        
        # 合并音频文件
        try:
            # 尝试使用pydub合并
            try:
                from pydub import AudioSegment
                
                print("📦 使用pydub合并音频...")
                combined = AudioSegment.empty()
                
                for i, chunk_file in enumerate(chunk_files):
                    if i % 20 == 0:  # 每20个文件显示一次进度
                        print(f"🔗 合并进度: {i+1}/{len(chunk_files)}")
                    
                    audio_chunk = AudioSegment.from_wav(chunk_file)
                    combined += audio_chunk
                    
                    # 添加短暂停顿（0.3秒）
                    combined += AudioSegment.silent(duration=300)
                
                # 导出最终文件
                print(f"💾 正在保存最终文件...")
                combined.export(str(output_wav_path), format="wav")
                
            except ImportError:
                print("⚠️  pydub未安装，使用系统命令合并...")
                
                # 创建文件列表
                file_list_path = temp_folder / "file_list.txt"
                with open(file_list_path, 'w', encoding='utf-8') as f:
                    for chunk_file in chunk_files:
                        f.write(f"file '{Path(chunk_file).absolute()}'\n")
                
                # 使用ffmpeg合并（如果可用）
                import subprocess
                try:
                    subprocess.run([
                        'ffmpeg', '-f', 'concat', '-safe', '0',
                        '-i', str(file_list_path),
                        '-c', 'copy', str(output_wav_path), '-y'
                    ], check=True, capture_output=True)
                    print("✅ 使用FFmpeg合并成功")
                    
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("❌ 无法自动合并，音频块保存在临时文件夹中")
                    print(f"📁 临时文件夹: {temp_folder.absolute()}")
                    print("💡 您可以手动使用音频编辑软件合并这些文件")
                    return False
            
        except Exception as e:
            print(f"❌ 合并过程出现错误: {e}")
            print(f"📁 音频块保存在: {temp_folder.absolute()}")
            return False
        
        # 清理临时文件
        print("🧹 正在清理临时文件...")
        try:
            for chunk_file in chunk_files:
                os.remove(chunk_file)
            
            # 删除文件列表（如果存在）
            file_list_path = temp_folder / "file_list.txt"
            if file_list_path.exists():
                os.remove(file_list_path)
            
            temp_folder.rmdir()
            print("✅ 临时文件清理完成")
        except Exception as e:
            print(f"⚠️  清理临时文件时出现问题: {e}")
        
        # 检查最终结果
        end_time = time.time()
        total_time = end_time - start_time
        
        if output_wav_path.exists():
            final_size_mb = get_file_size_mb(output_wav_path)
            print(f"\n🎉 大文件转换成功！")
            print(f"📁 输出文件: {output_wav_path}")
            print(f"📊 音频文件大小: {final_size_mb:.2f} MB")
            print(f"⏱️  总耗时: {total_time // 60:.0f} 分 {total_time % 60:.0f} 秒")
            print(f"📈 处理速度: {len(text) / total_time:.0f} 字符/秒")
            return True
        else:
            print("❌ 转换失败：最终文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ 转换过程中出现错误: {str(e)}")
        return False

def main():
    """主函数"""
    print("🎵 大文件TXT转WAV工具 - 改进版")
    print("="*50)
    print("💡 专门处理超大文件，无需FFmpeg依赖")
    
    # 检查依赖
    try:
        import pyttsx3
        print("✅ pyttsx3 可用")
    except ImportError:
        print("❌ pyttsx3 未安装")
        print("📦 请运行: pip install pyttsx3")
        input("按回车键退出...")
        return
    
    # 扫描当前目录的txt文件
    txt_files = list(Path(".").glob("*.txt"))
    
    if txt_files:
        print(f"\n📁 发现 {len(txt_files)} 个txt文件:")
        for i, file in enumerate(txt_files, 1):
            file_size_mb = get_file_size_mb(file)
            print(f"   {i}. {file.name} ({file_size_mb:.2f} MB)")
        
        try:
            choice = input(f"\n请选择要转换的文件 (1-{len(txt_files)}, 回车选择第一个): ").strip()
            if not choice:
                selected_file = txt_files[0]
            else:
                choice_num = int(choice)
                if 1 <= choice_num <= len(txt_files):
                    selected_file = txt_files[choice_num - 1]
                else:
                    print("❌ 无效选择")
                    return
        except ValueError:
            print("❌ 无效输入")
            return
    else:
        file_path = input("请输入txt文件路径: ").strip()
        if not file_path:
            print("❌ 未指定文件")
            return
        selected_file = Path(file_path)
    
    print(f"\n📄 选择的文件: {selected_file.name}")
    print(f"📊 文件大小: {get_file_size_mb(selected_file):.2f} MB")
    
    # 设置参数
    output_file = input("输出WAV文件名（回车使用默认）: ").strip()
    if not output_file:
        output_file = selected_file.with_suffix('.wav')
    
    try:
        rate = int(input("语音速度 (50-300, 默认180): ").strip() or "180")
        volume = float(input("音量 (0.0-1.0, 默认0.9): ").strip() or "0.9")
        chunk_size = int(input("分块大小 (500-1500字符, 默认800): ").strip() or "800")
    except ValueError:
        rate, volume, chunk_size = 180, 0.9, 800
        print("⚠️  输入无效，使用默认参数")
    
    print(f"\n🚀 开始转换大文件...")
    print(f"📄 输入: {selected_file}")
    print(f"🎵 输出: {output_file}")
    print(f"⚡ 语速: {rate} | 音量: {volume} | 块大小: {chunk_size}")
    
    # 开始转换
    success = txt_to_wav_large(str(selected_file), str(output_file), rate, volume, chunk_size)
    
    if success:
        print(f"\n🎉 大文件转换完成！")
        print(f"💡 可以使用任何音频播放器播放WAV文件")
        print(f"💡 如需MP3格式，可使用在线转换:")
        print(f"   - https://convertio.co/zh/wav-mp3/")
    else:
        print(f"\n❌ 转换失败！")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序出现错误: {e}")
    finally:
        input("\n按回车键退出...")