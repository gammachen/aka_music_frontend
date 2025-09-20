#!/usr/bin/env python3
"""
文件重命名脚本
按照最后修改时间升序排序，添加序号前缀，并将相关文件分组
"""

import os
import json
from datetime import datetime
from pathlib import Path

def get_file_info(directory):
    """获取目录下所有文件的信息"""
    files_info = []
    
    for file_path in Path(directory).iterdir():
        if file_path.is_file() and file_path.name != 'rename_files.py':
            stat = file_path.stat()
            files_info.append({
                'original_name': file_path.name,
                'full_path': str(file_path),
                'mtime': stat.st_mtime,
                'ctime': stat.st_ctime,
                'size': stat.st_size,
                'stem': file_path.stem.lower(),
                'suffix': file_path.suffix.lower()
            })
    
    return sorted(files_info, key=lambda x: x['mtime'])

def find_related_files(files_info):
    """识别相关的文件组"""
    groups = []
    processed = set()
    
    # 定义关键词匹配规则
    keywords = {
        'sequential_chain': ['sequential', 'chain'],
        'ollama': ['ollama'],
        'output_parsers': ['output', 'parser'],
        'partial_templates': ['partial', 'template'],
        'rag': ['rag', 'retriever'],
        'token': ['token'],
        'cache': ['cache'],
        'prompt': ['prompt'],
        'test': ['test'],
        'guide': ['guide', 'guide.md'],
        'doctran': ['doctran'],
        'finetune': ['finetune', 'fine_tune'],
        'vs': ['vs', 'comparison']
    }
    
    for file_info in files_info:
        if file_info['original_name'] in processed:
            continue
            
        stem = file_info['stem']
        
        # 寻找相关文件
        related = [file_info]
        processed.add(file_info['original_name'])
        
        # 基于文件名匹配相关文件
        for other in files_info:
            if other['original_name'] in processed:
                continue
                
            other_stem = other['stem']
            
            # 直接匹配文件名前缀
            if stem.startswith(other_stem) or other_stem.startswith(stem):
                if abs(file_info['mtime'] - other['mtime']) < 3600:  # 1小时内修改的文件
                    related.append(other)
                    processed.add(other['original_name'])
                    continue
            
            # 基于关键词匹配
            for key, words in keywords.items():
                if any(word in stem for word in words) and any(word in other_stem for word in words):
                    if abs(file_info['mtime'] - other['mtime']) < 7200:  # 2小时内
                        related.append(other)
                        processed.add(other['original_name'])
                        break
        
        # 按时间排序相关文件
        related.sort(key=lambda x: x['mtime'])
        groups.append(related)
    
    return groups

def generate_new_names(groups):
    """生成新的文件名"""
    counter = 1
    renames = []
    
    for group in groups:
        for file_info in group:
            # 生成新的文件名
            stem = file_info['stem']
            suffix = file_info['suffix']
            
            # 为不同类型的文件添加描述性后缀
            if suffix == '.md':
                desc = 'doc'
            elif suffix == '.py':
                desc = 'py'
            elif suffix == '.json':
                desc = 'json'
            elif suffix == '.png':
                desc = 'img'
            else:
                desc = 'file'
            
            new_name = f"{counter:02d}_{stem}{suffix}"
            
            renames.append({
                'original': file_info['original_name'],
                'new': new_name,
                'full_path': file_info['full_path'],
                'mtime': file_info['mtime'],
                'group': counter
            })
            
            counter += 1
    
    return renames

def main():
    directory = "/Users/shhaofu/Code/cursor-projects/aka_music/frontend/public/llm_langchain"
    
    print("正在分析文件信息...")
    files_info = get_file_info(directory)
    
    print("正在识别相关文件组...")
    groups = find_related_files(files_info)
    
    print("正在生成新的文件名...")
    renames = generate_new_names(groups)
    
    # 保存重命名计划
    rename_plan = []
    for rename in renames:
        rename_plan.append({
            "original": rename['original'],
            "new": rename['new'],
            "mtime": datetime.fromtimestamp(rename['mtime']).strftime('%Y-%m-%d %H:%M:%S'),
            "group": rename['group']
        })
    
    with open('rename_plan.json', 'w', encoding='utf-8') as f:
        json.dump(rename_plan, f, ensure_ascii=False, indent=2)
    
    print(f"发现 {len(files_info)} 个文件，分为 {len(groups)} 个相关组")
    print("\n重命名计划:")
    for rename in renames:
        print(f"{rename['original']} -> {rename['new']}")
    
    # 执行重命名
    confirm = input("\n是否执行重命名？(y/N): ")
    if confirm.lower() == 'y':
        for rename in renames:
            try:
                original_path = rename['full_path']
                new_path = os.path.join(directory, rename['new'])
                os.rename(original_path, new_path)
                print(f"✓ {rename['original']} -> {rename['new']}")
            except Exception as e:
                print(f"✗ 重命名失败 {rename['original']}: {e}")
        
        print("重命名完成！")
    else:
        print("重命名已取消")

if __name__ == "__main__":
    main()