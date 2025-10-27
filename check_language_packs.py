"""
本地化JSON语言包key比较工具，用于比较不同文件中key的差异，返回json格式？
"""

import json
from pathlib import Path
import sys
from typing import Any, Set
from typing import Dict


# from typing import Dict,Set,Tuple

def compare_json_keys(file1:Path, file2:Path):
    """
    比较两个文件的key差异，分别返回仅在file1中的key、仅在file2中的key、共有的key
    """

    # 分别加载json文件
    data1 = load_json_file(file1)
    data2 = load_json_file(file2)

    # 分别加载key
    key1 = extract_keys(data1)
    key2 = extract_keys(data2)

    # 比较key
    only_in_file1 = key1 - key2
    only_in_file2 = key2 - key1
    common_keys = key1 & key2

    return only_in_file1, only_in_file2, common_keys


def load_json_file(file_path: Path) -> Dict:
    """
    从文件中读取json文件
    """

    try:
        with open(file_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"error:'{file_path}'不存在")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"error:'{file_path}格式有误{e}")
        sys.exit(1)
    except Exception as e:
        print(f"error:{file_path}文件有误{e}")
        sys.exit(1)


def extract_keys(data: Dict, prefix: str = "") -> Set[str]:
    """
    从json文件中获取所有key
    """

    key_list = set()
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            nested_keys = extract_keys(value, full_key)
            key_list.update(nested_keys)
        else:
            key_list.add(full_key)

    return key_list


def print_comparison_results():
    """
    打印比较结果
    """


def main(file1: Path, file2: Path):
    # 校验文件是否存在
    for file_path in [file1, file2]:
        if not Path(file_path).exists():
            print(f"error:文件{file_path}不存在")

    try:
        only_in_file1,only_in_file2,common_keys = compare_json_keys(file1, file2)


    except Exception as e:
        print(f"error:{e}")
        sys.exit(1)



