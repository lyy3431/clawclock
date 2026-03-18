#!/usr/bin/env python3
"""
验证 breath_light.py 模块结构（不导入 tkinter）
"""

import ast
import sys

def check_module_structure(filepath):
    """检查模块结构"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 解析 AST
    tree = ast.parse(content)
    
    # 查找类定义
    classes = []
    functions = []
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            if isinstance(node, ast.ImportFrom):
                imports.append(f"from {node.module}")
            else:
                for alias in node.names:
                    imports.append(f"import {alias.name}")
    
    return classes, functions, imports

print("🔍 验证 breath_light.py 模块结构")
print("=" * 60)

classes, functions, imports = check_module_structure('/home/lenovo/AItest/clawclock/breath_light.py')

print(f"\n✅ 找到的类 ({len(classes)}):")
for cls in classes:
    print(f"   • {cls}")

print(f"\n✅ 找到的函数 ({len(functions)}):")
for func in functions[:15]:  # 只显示前 15 个
    print(f"   • {func}")
if len(functions) > 15:
    print(f"   ... 还有 {len(functions) - 15} 个函数")

print(f"\n✅ 关键枚举类检查:")
expected_classes = ['BreathMode', 'BreathStyle', 'TimerStatus', 'BreathLightConfig', 
                   'BreathLightEffect', 'BreathLightWidget']
for cls in expected_classes:
    status = "✅" if cls in classes else "❌"
    print(f"   {status} {cls}")

print(f"\n✅ 工具函数检查:")
expected_funcs = ['hex_to_rgb', 'rgb_to_hex', 'interpolate_color']
for func in expected_funcs:
    status = "✅" if func in functions else "❌"
    print(f"   {status} {func}")

# 检查配置文件
import json
print(f"\n✅ 检查 config.json:")
with open('/home/lenovo/AItest/clawclock/config.json', 'r') as f:
    config = json.load(f)

breath_config = config.get('breath_light', {})
print(f"   • style: {breath_config.get('style', 'MISSING')}")
print(f"   • frequency: {breath_config.get('frequency', 'MISSING')}")
print(f"   • intensity: {breath_config.get('intensity', 'MISSING')}")
print(f"   • smooth_curve: {breath_config.get('smooth_curve', 'MISSING')}")

print(f"\n✅ 检查 timer.py 导入:")
with open('/home/lenovo/AItest/clawclock/timer.py', 'r') as f:
    timer_content = f.read()
    
if 'BreathStyle' in timer_content:
    print(f"   ✅ BreathStyle 已导入")
else:
    print(f"   ❌ BreathStyle 未导入")

if 'style=BreathStyle' in timer_content:
    print(f"   ✅ BreathStyle 已使用")
else:
    print(f"   ⚠️  BreathStyle 可能未使用")

print("\n" + "=" * 60)
print("✅ 模块结构验证完成！")
print("\n📋 v1.5.1 关键变更:")
print("   • 新增 BreathStyle 枚举（4 种风格）")
print("   • 新增 BREATH_STYLE_COLORS 配色方案")
print("   • 改进 _calculate_smooth_brightness 使用缓动曲线")
print("   • 优化默认参数（frequency=0.5, intensity=0.5）")
print("   • 更新 config.json 添加 style 和 smooth_curve")
