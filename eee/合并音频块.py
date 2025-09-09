#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频块合并工具
将temp_audio_chunks文件夹中的WAV文件合并为一个完整的音频文件
"""

import os
import wave
import glob
from pathlib import Path

def merge_wav_files(input_folder="temp_audio_chunks", output_file="合并后的音频.wav"):
    """
    合并WAV文件，不依赖FFmpeg
    """
    print(f"正在合并 {input_folder} 文件夹中的音频文件...")
    
    # 获取所有WAV文件并按文件名排序
    wav_files = glob.glob(os.path.join(input_folder, "chunk_*.wav"))
    
    if not wav_files:
        print("错误：没有找到音频块文件")
        return False
    
    # 按文件名中的数字排序
    wav_files.sort(key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))
    
    print(f"找到 {len(wav_files)} 个音频块文件")
    
    try:
        # 打开第一个文件获取音频参数
        with wave.open(wav_files[0], 'rb') as first_wav:
            params = first_wav.getparams()
            print(f"音频参数: {params.nchannels}声道, {params.sampwidth}字节采样, {params.framerate}Hz采样率")
        
        # 创建输出文件
        with wave.open(output_file, 'wb') as output_wav:
            output_wav.setparams(params)
            
            # 逐个读取并写入音频数据
            for i, wav_file in enumerate(wav_files):
                if i % 100 == 0:  # 每100个文件显示一次进度
                    print(f"正在处理: {i+1}/{len(wav_files)} ({(i+1)/len(wav_files)*100:.1f}%)")
                
                try:
                    with wave.open(wav_file, 'rb') as input_wav:
                        # 检查参数是否一致
                        if input_wav.getparams()[:4] != params[:4]:
                            print(f"警告: {wav_file} 的音频参数不一致，跳过")
                            continue
                        
                        # 读取并写入音频数据
                        frames = input_wav.readframes(input_wav.getnframes())
                        output_wav.writeframes(frames)
                        
                except Exception as e:
                    print(f"处理 {wav_file} 时出错: {e}")
                    continue
        
        print(f"✓ 合并完成！输出文件: {output_file}")
        
        # 显示文件信息
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        print(f"文件大小: {file_size:.1f} MB")
        
        # 计算音频时长
        with wave.open(output_file, 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            print(f"音频时长: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        return True
        
    except Exception as e:
        print(f"合并过程中出现错误: {e}")
        return False

def clean_temp_files(input_folder="temp_audio_chunks"):
    """
    清理临时文件
    """
    choice = input("\n是否删除临时音频块文件？(y/n): ").lower().strip()
    if choice in ['y', 'yes', '是', '好']:
        try:
            wav_files = glob.glob(os.path.join(input_folder, "chunk_*.wav"))
            for wav_file in wav_files:
                os.remove(wav_file)
            
            # 如果文件夹为空，删除文件夹
            if os.path.exists(input_folder) and not os.listdir(input_folder):
                os.rmdir(input_folder)
            
            print(f"✓ 已删除 {len(wav_files)} 个临时文件")
        except Exception as e:
            print(f"删除临时文件时出错: {e}")

def main():
    print("=== 音频块合并工具 ===\n")
    
    # 检查临时文件夹是否存在
    if not os.path.exists("temp_audio_chunks"):
        print("错误：找不到 temp_audio_chunks 文件夹")
        return
    
    # 获取音频块文件数量
    wav_files = glob.glob("temp_audio_chunks/chunk_*.wav")
    if not wav_files:
        print("错误：temp_audio_chunks 文件夹中没有音频块文件")
        return
    
    print(f"发现 {len(wav_files)} 个音频块文件")
    
    # 询问输出文件名
    output_name = input("请输入输出文件名（直接回车使用默认名称）: ").strip()
    if not output_name:
        output_name = "镇国驸马爷-完整音频.wav"
    
    if not output_name.endswith('.wav'):
        output_name += '.wav'
    
    # 开始合并
    success = merge_wav_files("temp_audio_chunks", output_name)
    
    if success:
        print(f"\n🎉 音频合并成功！")
        print(f"输出文件: {output_name}")
        print(f"文件位置: {os.path.abspath(output_name)}")
        
        # 询问是否清理临时文件
        clean_temp_files()
    else:
        print("\n❌ 音频合并失败")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")