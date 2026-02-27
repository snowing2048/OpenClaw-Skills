#!/usr/bin/env python3
"""
Key Press - Press key(s) with auto-screenshot
Usage: py scripts/key_press.py "enter" --output-dir "C:/path/to/output"
Supports: enter, tab, esc, backspace, delete, ctrl, alt, shift, win, or combinations like "ctrl+s"
"""
import pyautogui
import sys
import os
import json
from datetime import datetime
from pathlib import Path

pyautogui.FAILSAFE = False

def parse_args(args):
    """解析参数，分离位置参数和选项"""
    output_dir = None
    positional = []
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ['--output-dir', '-o']:
            if i + 1 < len(args):
                output_dir = args[i + 1]
                i += 2
            else:
                raise ValueError("--output-dir requires a path argument")
        else:
            positional.append(arg)
            i += 1
    
    return positional, output_dir

def get_default_output_dir():
    """获取默认输出目录"""
    default_dir = Path(__file__).parent.parent / "tmp" / "_artifacts" / "screenshots"
    default_dir.mkdir(parents=True, exist_ok=True)
    return str(default_dir)

def get_output_dir(args):
    """从参数获取输出目录（兼容旧用法）"""
    for i, arg in enumerate(args):
        if arg in ['--output-dir', '-o'] and i + 1 < len(args):
            return args[i + 1]
    return get_default_output_dir()

def auto_screenshot(output_dir, prefix, suffix=""):
    """自动截图并保存"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        filename = f"{prefix}{timestamp}{suffix}.png"
        filepath = os.path.join(output_dir, filename)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        return {
            "success": True,
            "path": filepath,
            "filename": filename,
            "timestamp": timestamp
        }
    except Exception as e:
        print(f"Screenshot error: {e}", file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

def save_metadata(output_dir, operation_type, params, before_shot, after_shot):
    """保存操作元数据"""
    try:
        metadata = {
            "operation": operation_type,
            "params": params,
            "timestamp": datetime.now().isoformat(),
            "before_screenshot": before_shot,
            "after_screenshot": after_shot
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        meta_file = os.path.join(output_dir, f"{operation_type}_{timestamp}.json")
        
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return meta_file
    except Exception as e:
        return None

def parse_key(key_str):
    """解析按键字符串，支持组合键"""
    # 常见键位映射
    key_map = {
        'enter': 'enter',
        'return': 'enter',
        'tab': 'tab',
        'esc': 'esc',
        'escape': 'esc',
        'backspace': 'backspace',
        'delete': 'delete',
        'del': 'delete',
        'ctrl': 'ctrl',
        'control': 'ctrl',
        'alt': 'alt',
        'shift': 'shift',
        'win': 'win',
        'command': 'win',
        'cmd': 'win',
        'space': 'space',
        'up': 'up',
        'down': 'down',
        'left': 'left',
        'right': 'right',
        'home': 'home',
        'end': 'end',
        'pageup': 'pageup',
        'pagedown': 'pagedown',
        'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
        'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
        'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12',
    }
    
    # 处理组合键 (如 "ctrl+s")
    if '+' in key_str:
        parts = key_str.split('+')
        return [key_map.get(p.lower(), p) for p in parts]
    
    # 单个键
    return key_map.get(key_str.lower(), key_str)

def main():
    if len(sys.argv) < 2:
        print("Usage: py key_press.py \"KEY\" [--output-dir PATH]")
        print("  KEY: 按键名称 (enter, tab, esc, ctrl+s, etc.)")
        print("  --output-dir, -o: 截图输出目录 (默认：tmp/_artifacts/screenshots)")
        sys.exit(1)
    
    # 解析参数
    positional, output_dir = parse_args(sys.argv[1:])
    
    if not positional:
        print("Error: KEY is required")
        sys.exit(1)
    
    if not output_dir:
        output_dir = get_default_output_dir()
    
    key_str = positional[0]
    
    keys = parse_key(key_str)
    
    params = {
        "key_input": key_str,
        "keys_parsed": keys if isinstance(keys, list) else [keys]
    }
    
    # 操作前截图
    before_shot = auto_screenshot(output_dir, "keypress_before_")
    
    # 执行按键
    try:
        if isinstance(keys, list):
            # 组合键
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(keys)
        
        result = {
            "success": True,
            "message": f"Pressed: {key_str}"
        }
    except Exception as e:
        result = {
            "success": False,
            "message": f"Error: {e}"
        }
    
    # 操作后截图
    after_shot = auto_screenshot(output_dir, "keypress_after_")
    
    # 保存元数据
    meta_file = save_metadata(output_dir, "keypress", params, before_shot, after_shot)
    
    # 输出结果
    print(f"Pressed: {key_str}")
    print(f"Before: {before_shot.get('path', 'N/A')}")
    print(f"After: {after_shot.get('path', 'N/A')}")
    if meta_file:
        print(f"Metadata: {meta_file}")
    
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()
