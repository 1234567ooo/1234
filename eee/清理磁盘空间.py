#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
磁盘空间清理工具
帮助释放磁盘空间以完成音频合并
"""

import os
import shutil
import tempfile
import glob

def get_disk_usage():
    """获取磁盘使用情况"""
    try:
        total, used, free = shutil.disk_usage(".")
        return {
            'total': total / (1024**3),  # GB
            'used': used / (1024**3),
            'free': free / (1024**3)
        }
    except:
        return None

def clean_temp_files():
    """清理系统临时文件"""
    cleaned_size = 0
    temp_dir = tempfile.gettempdir()
    
    print(f"正在清理临时文件夹: {temp_dir}")
    
    try:
        # 清理临时文件
        temp_files = glob.glob(os.path.join(temp_dir, "tmp*"))
        temp_files.extend(glob.glob(os.path.join(temp_dir, "*.tmp")))
        
        for temp_file in temp_files:
            try:
                if os.path.isfile(temp_file):
                    size = os.path.getsize(temp_file)
                    os.remove(temp_file)
                    cleaned_size += size
                elif os.path.isdir(temp_file):
                    size = get_folder_size(temp_file)
                    shutil.rmtree(temp_file)
                    cleaned_size += size
            except:
                continue
                
    except Exception as e:
        print(f"清理临时文件时出错: {e}")
    
    return cleaned_size

def get_folder_size(folder_path):
    """获取文件夹大小"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    continue
    except:
        pass
    return total_size

def find_large_files():
    """查找大文件"""
    print("正在扫描大文件...")
    large_files = []
    
    # 扫描常见位置的大文件
    scan_paths = [
        "C:\\Users\\123\\Downloads",
        "C:\\Users\\123\\Desktop", 
        "C:\\Users\\123\\Documents",
        "C:\\Windows\\Temp",
        "."
    ]
    
    for scan_path in scan_paths:
        if os.path.exists(scan_path):
            try:
                for root, dirs, files in os.walk(scan_path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        try:
                            size = os.path.getsize(filepath)
                            if size > 100 * 1024 * 1024:  # 大于100MB
                                large_files.append({
                                    'path': filepath,
                                    'size': size / (1024 * 1024)  # MB
                                })
                        except:
                            continue
                    
                    # 只扫描前几层目录，避免太深
                    if root.count(os.sep) - scan_path.count(os.sep) > 2:
                        dirs.clear()
            except:
                continue
    
    # 按大小排序
    large_files.sort(key=lambda x: x['size'], reverse=True)
    return large_files[:20]  # 返回前20个最大的文件

def clean_recycle_bin():
    """清空回收站"""
    try:
        import winshell
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        return True
    except:
        # 如果winshell不可用，尝试命令行方式
        try:
            os.system('rd /s /q C:\\$Recycle.Bin')
            return True
        except:
            return False

def main():
    print("=== 磁盘空间清理工具 ===\n")
    
    # 显示当前磁盘使用情况
    disk_info = get_disk_usage()
    if disk_info:
        print(f"磁盘使用情况:")
        print(f"  总容量: {disk_info['total']:.1f} GB")
        print(f"  已使用: {disk_info['used']:.1f} GB")
        print(f"  可用空间: {disk_info['free']:.1f} GB")
        
        if disk_info['free'] < 2:
            print("⚠️  可用空间不足2GB，建议清理")
        print()
    
    print("选择清理选项:")
    print("1. 清理系统临时文件")
    print("2. 查找并显示大文件")
    print("3. 清空回收站")
    print("4. 全部执行")
    print("5. 退出")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    if choice == "1" or choice == "4":
        print("\n正在清理临时文件...")
        cleaned_size = clean_temp_files()
        print(f"✓ 清理临时文件完成，释放空间: {cleaned_size / (1024*1024):.1f} MB")
    
    if choice == "2" or choice == "4":
        print("\n正在查找大文件...")
        large_files = find_large_files()
        if large_files:
            print("发现的大文件:")
            for i, file_info in enumerate(large_files[:10], 1):
                print(f"  {i}. {file_info['path']} ({file_info['size']:.1f} MB)")
            
            if choice == "2":
                delete_choice = input("\n是否要删除某些大文件？(y/n): ").lower()
                if delete_choice == 'y':
                    file_nums = input("输入要删除的文件编号(用逗号分隔): ").strip()
                    try:
                        nums = [int(x.strip()) for x in file_nums.split(',')]
                        for num in nums:
                            if 1 <= num <= len(large_files):
                                file_path = large_files[num-1]['path']
                                try:
                                    os.remove(file_path)
                                    print(f"✓ 已删除: {file_path}")
                                except Exception as e:
                                    print(f"✗ 删除失败: {file_path} - {e}")
                    except:
                        print("输入格式错误")
        else:
            print("没有发现大文件")
    
    if choice == "3" or choice == "4":
        print("\n正在清空回收站...")
        if clean_recycle_bin():
            print("✓ 回收站清空完成")
        else:
            print("✗ 清空回收站失败")
    
    if choice == "5":
        print("退出清理工具")
        return
    
    # 显示清理后的磁盘情况
    print("\n清理完成！")
    disk_info_after = get_disk_usage()
    if disk_info and disk_info_after:
        freed_space = disk_info_after['free'] - disk_info['free']
        print(f"释放空间: {freed_space:.1f} GB")
        print(f"当前可用空间: {disk_info_after['free']:.1f} GB")
        
        if disk_info_after['free'] >= 2:
            print("✓ 空间充足，可以继续音频合并")
        else:
            print("⚠️  空间仍然不足，建议继续清理")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")