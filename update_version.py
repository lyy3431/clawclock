#!/usr/bin/env python3
"""
自动更新 ClawClock 版本号

使用方法:
    python update_version.py [新版本号]
    
例如:
    python update_version.py 1.6.5
    
如果不提供版本号，会自动递增 patch 版本（1.6.4 → 1.6.5）
"""

import re
import sys
import os
from pathlib import Path

def get_current_version(clock_py_path: str) -> str:
    """从 clock.py 读取当前版本号"""
    with open(clock_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(r'__version__ = "([\d.]+)"', content)
    if match:
        return match.group(1)
    raise ValueError("无法找到版本号")

def increment_patch(version: str) -> str:
    """递增 patch 版本号 (1.6.4 → 1.6.5)"""
    parts = version.split('.')
    if len(parts) >= 3:
        parts[2] = str(int(parts[2]) + 1)
    return '.'.join(parts)

def update_version(clock_py_path: str, new_version: str):
    """更新 clock.py 中的版本号"""
    with open(clock_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新 __version__
    content = re.sub(
        r'__version__ = "[\d.]+"',
        f'__version__ = "{new_version}"',
        content
    )
    
    # 更新 __version_info__
    parts = new_version.split('.')
    version_info = f"({parts[0]}, {parts[1]}, {parts[2]})"
    content = re.sub(
        r'__version_info__ = \([\d, ]+\)',
        f'__version_info__ = {version_info}',
        content
    )
    
    with open(clock_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 版本号已更新：{new_version}")

def main():
    script_dir = Path(__file__).parent
    clock_py_path = script_dir / "clock.py"
    
    if not clock_py_path.exists():
        print(f"❌ 错误：找不到 {clock_py_path}")
        sys.exit(1)
    
    # 获取新版本号
    if len(sys.argv) >= 2:
        new_version = sys.argv[1]
    else:
        # 自动递增 patch 版本
        current_version = get_current_version(str(clock_py_path))
        new_version = increment_patch(current_version)
        print(f"当前版本：{current_version}")
        print(f"新版本：{new_version}")
    
    # 更新版本号
    update_version(str(clock_py_path), new_version)
    
    # 创建 git tag
    import subprocess
    try:
        subprocess.run(['git', 'tag', f'v{new_version}'], cwd=script_dir, check=True)
        print(f"✅ Git tag 已创建：v{new_version}")
    except Exception as e:
        print(f"⚠️  创建 git tag 失败：{e}")

if __name__ == "__main__":
    main()
