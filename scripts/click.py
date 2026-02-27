#!/usr/bin/env python3
"""
Click - Click at coordinates with auto-screenshot
Usage: py scripts/click.py 500 300 left 1 --output-dir "C:/path/to/output"
"""
import pyautogui
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 禁用 FAILSAFE
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

def auto_screenshot(output_dir, prefix, suffix=""):
    """自动截图并保存"""
    try:
        # 确保目录存在
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

def main():
    if len(sys.argv) < 2:
        print("Usage: py click.py X Y [button] [clicks] [--output-dir PATH]")
        print("  X, Y: 屏幕坐标")
        print("  button: left/right/middle (默认：left)")
        print("  clicks: 点击次数 (默认：1)")
        print("  --output-dir, -o: 截图输出目录 (默认：tmp/_artifacts/screenshots)")
        sys.exit(1)
    
    # 解析参数
    positional, output_dir = parse_args(sys.argv[1:])
    
    if len(positional) < 2:
        print("Error: X and Y coordinates are required")
        print("Usage: py click.py X Y [button] [clicks] [--output-dir PATH]")
        sys.exit(1)
    
    # 使用默认输出目录
    if not output_dir:
        output_dir = get_default_output_dir()
    
    x = int(positional[0])
    y = int(positional[1])
    button = positional[2] if len(positional) > 2 else "left"
    clicks = int(positional[3]) if len(positional) > 3 else 1
    
    params = {
        "x": x,
        "y": y,
        "button": button,
        "clicks": clicks
    }
    
    # 操作前截图
    before_shot = auto_screenshot(output_dir, "click_before_")
    
    # 执行点击
    try:
        pyautogui.click(x, y, clicks=clicks, button=button)
        result = {
            "success": True,
            "message": f"Clicked {button} button at ({x}, {y}) {clicks} time(s)"
        }
    except Exception as e:
        result = {
            "success": False,
            "message": f"Error: {e}"
        }
    
    # 操作后截图
    after_shot = auto_screenshot(output_dir, "click_after_")
    
    # 保存元数据
    meta_file = save_metadata(output_dir, "click", params, before_shot, after_shot)
    
    # 输出结果
    print(result["message"])
    print(f"Before: {before_shot.get('path', 'N/A')}")
    print(f"After: {after_shot.get('path', 'N/A')}")
    if meta_file:
        print(f"Metadata: {meta_file}")
    
    # 返回状态码
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()
