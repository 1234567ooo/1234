#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速音频合并工具 - 优化版
专门处理大量音频文件的合并
"""

import os
import wave
import glob
import time

def merge_audio_fast():
    """
    快速合并音频文件
    """
    print("=== 快速音频合并工具 ===\n")
    
    # 检查临时文件夹
    if not os.path.exists("temp_audio_chunks"):
        print("错误：找不到 temp_audio_chunks 文件夹")
        input("按回车键退出...")
        return
    
    # 获取所有音频块文件
    print("正在扫描音频文件...")
    wav_files = glob.glob("temp_audio_chunks/chunk_*.wav")
    
    if not wav_files:
        print("错误：没有找到音频块文件")
        input("按回车键退出...")
        return
    
    # 按文件名排序
    wav_files.sort(key=lambda x: int(os.path.basename(x).split('_')[1].split('.')[0]))
    
    print(f"找到 {len(wav_files)} 个音频文件")
    
    # 输出文件名
    output_file = "镇国驸马爷-完整音频.wav"
    
    print(f"开始合并到: {output_file}")
    print("这可能需要几分钟时间，请耐心等待...\n")
    
    start_time = time.time()
    
    try:
        # 获取第一个文件的参数
        with wave.open(wav_files[0], 'rb') as first_wav:
            params = first_wav.getparams()
        
        print(f"音频参数: {params.nchannels}声道, {params.framerate}Hz")
        
        # 创建输出文件
        with wave.open(output_file, 'wb') as output_wav:
            output_wav.setparams(params)
            
            # 分批处理文件
            batch_size = 50  # 每批处理50个文件
            total_batches = (len(wav_files) + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, len(wav_files))
                batch_files = wav_files[start_idx:end_idx]
                
                print(f"处理批次 {batch_num + 1}/{total_batches} ({len(batch_files)} 个文件)")
                
                for wav_file in batch_files:
                    try:
                        with wave.open(wav_file, 'rb') as input_wav:
                            frames = input_wav.readframes(input_wav.getnframes())
                            output_wav.writeframes(frames)
                    except Exception as e:
                        print(f"跳过损坏文件: {os.path.basename(wav_file)}")
                        continue
                
                # 显示进度
                progress = (batch_num + 1) / total_batches * 100
                print(f"进度: {progress:.1f}%")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n✓ 合并完成！")
        print(f"耗时: {duration:.1f} 秒")
        print(f"输出文件: {output_file}")
        
        # 显示文件信息
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)
            print(f"文件大小: {file_size:.1f} MB")
            print(f"文件位置: {os.path.abspath(output_file)}")
            
            # 计算音频时长
            try:
                with wave.open(output_file, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    audio_duration = frames / float(rate)
                    hours = int(audio_duration // 3600)
                    minutes = int((audio_duration % 3600) // 60)
                    seconds = int(audio_duration % 60)
                    print(f"音频时长: {hours:02d}:{minutes:02d}:{seconds:02d}")
            except:
                pass
        
        # 询问是否删除临时文件
        print("\n是否删除临时音频块文件以节省空间？")
        choice = input("输入 y 删除，其他键保留: ").lower().strip()
        
        if choice == 'y':
            try:
                for wav_file in wav_files:
                    os.remove(wav_file)
                
                # 删除空文件夹
                if os.path.exists("temp_audio_chunks") and not os.listdir("temp_audio_chunks"):
                    os.rmdir("temp_audio_chunks")
                
                print(f"✓ 已删除 {len(wav_files)} 个临时文件")
            except Exception as e:
                print(f"删除临时文件时出错: {e}")
        
        print("\n🎉 任务完成！你现在可以播放音频文件了。")
        
    except Exception as e:
        print(f"合并过程中出现错误: {e}")
        print("请检查磁盘空间是否足够")

if __name__ == "__main__":
    merge_audio_fast()
    input("\n按回车键退出...")