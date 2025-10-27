#!/usr/bin/env python3
"""
JSON语言包key比较工具
用于比较两个JSON文件中的key差异
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Set, Tuple


def load_json_file(file_path: str) -> Dict:
    """
    加载JSON文件
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：文件 '{file_path}' 不存在")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误：文件 '{file_path}' 不是有效的JSON格式: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误：读取文件 '{file_path}' 时发生错误: {e}")
        sys.exit(1)

def extract_keys(data: Dict, prefix: str = "") -> Set[str]:
    """
    递归提取JSON中的所有key，支持嵌套结构
    """
    keys = set()
    
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            # 递归处理嵌套字典
            nested_keys = extract_keys(value, full_key)
            keys.update(nested_keys)
        else:
            keys.add(full_key)
    
    return keys

def compare_json_keys(file1: str, file2: str) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    比较两个JSON文件的key
    返回：(file1独有的key, file2独有的key, 共有的key)
    """
    # 加载JSON数据
    data1 = load_json_file(file1)
    data2 = load_json_file(file2)
    
    # 提取所有key
    keys1 = extract_keys(data1)
    keys2 = extract_keys(data2)
    
    # 计算差异
    only_in_file1 = keys1 - keys2
    only_in_file2 = keys2 - keys1
    common_keys = keys1 & keys2
    
    return only_in_file1, only_in_file2, common_keys

def print_comparison_results(file1: str, file2: str, only_in_file1: Set[str], 
                           only_in_file2: Set[str], common_keys: Set[str], 
                           output_file: str = None):
    """
    打印比较结果
    """
    output_lines = []
    
    # 标题
    title = f"JSON Key 比较报告: {file1} vs {file2}"
    output_lines.append(title)
    output_lines.append("=" * len(title))
    output_lines.append("")
    
    # 统计信息
    output_lines.append(f"统计信息:")
    output_lines.append(f"  {file1} 总key数: {len(only_in_file1) + len(common_keys)}")
    output_lines.append(f"  {file2} 总key数: {len(only_in_file2) + len(common_keys)}")
    output_lines.append(f"  共有key数: {len(common_keys)}")
    output_lines.append(f"  仅存在于 {file1} 的key数: {len(only_in_file1)}")
    output_lines.append(f"  仅存在于 {file2} 的key数: {len(only_in_file2)}")
    output_lines.append("")
    
    # 仅存在于file1的key，输出为json
    if only_in_file1:
        output_lines.append(f"仅存在于 {file1} 的key:")
        output_lines.append("-" * 40)
        for key in only_in_file1:
            output_lines.append(f"  {key}")
        output_lines.append("")
    
    # 仅存在于file2的key，输出为json
    if only_in_file2:
        output_lines.append(f"仅存在于 {file2} 的key:")
        output_lines.append("-" * 40)
        for key in only_in_file2:
            output_lines.append(f"  {key}")
        output_lines.append("")
    
    # 输出到控制台
    for line in output_lines:
        print(line)
    
    # 输出到文件
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            print(f"\n详细报告已保存到: {output_file}")
        except Exception as e:
            print(f"警告：无法保存报告到文件 '{output_file}': {e}")

def main():
    parser = argparse.ArgumentParser(
        description="比较两个JSON语言包的key差异",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s en.json zh.json
  %(prog)s file1.json file2.json --output report.txt
  %(prog)s --help
        """
    )
    
    parser.add_argument(
        'file1',
        help='第一个JSON文件路径'
    )
    
    parser.add_argument(
        'file2', 
        help='第二个JSON文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='将详细报告输出到指定文件'
    )
    
    parser.add_argument(
        '--ignore-case',
        action='store_true',
        help='忽略key的大小写（注意：这可能会影响嵌套结构的准确性）'
    )
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    for file_path in [args.file1, args.file2]:
        if not Path(file_path).exists():
            print(f"错误：文件 '{file_path}' 不存在")
            sys.exit(1)
    
    # 执行比较
    try:
        only_in_file1, only_in_file2, common_keys = compare_json_keys(args.file1, args.file2)
        
        # 输出结果
        print_comparison_results(
            args.file1, args.file2, 
            only_in_file1, only_in_file2, common_keys,
            args.output
        )
        
        # 如果有缺失的key，以非零状态退出
        if only_in_file1 or only_in_file2:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"比较过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()