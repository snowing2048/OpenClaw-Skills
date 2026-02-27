#!/usr/bin/env python3
"""
Screenshot - Capture screen with auto-save to specified directory
Usage: py scripts/screenshot.py [--output-dir PATH] [--filename NAME]
"""
import base64
import io
import sys
import os
from datetime import datetime
from pathlib import Path

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

def get_output_dir(args):
    """从参数获取输出目录"""
    for i, arg in enumerate(args):
        if arg in ['--output-dir', '-o'] and i + 1 < len(args):
            return args[i + 1]
    default_dir = Path(__file__).parent.parent / "tmp" / "_artifacts" / "screenshots"
    default_dir.mkdir(parents=True, exist_ok=True)
    return str(default_dir)

def get_filename(args):
    """从参数获取文件名"""
    for i, arg in enumerate(args):
        if arg in ['--filename', '-f'] and i + 1 < len(args):
            return args[i + 1]
    return None

def capture_screen():
    """截图，尝试多种方法"""
    if pyautogui:
        try:
            screenshot = pyautogui.screenshot()
            return screenshot
        except Exception as e:
            print(f"pyautogui failed: {e}", file=sys.stderr)
    
    if ImageGrab:
        try:
            screenshot = ImageGrab.grab()
            return screenshot
        except Exception as e:
            print(f"PIL failed: {e}", file=sys.stderr)
    
    raise Exception("All screenshot methods failed")

def main():
    output_dir = get_output_dir(sys.argv)
    filename = get_filename(sys.argv)
    
    # 确保目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    filepath = os.path.join(output_dir, filename)
    
    try:
        # 截图
        screenshot = capture_screen()
        
        # 保存为文件
        screenshot.save(filepath)
        
        # 同时输出 base64（兼容旧用法）
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        base64_data = base64.b64encode(buffered.getvalue()).decode()
        
        # 输出到 stdout（base64，兼容管道）
        print(base64_data)
        
        # 输出信息到 stderr（不干扰管道）
        print(f"Screenshot saved: {filepath}", file=sys.stderr)
        print(f"Size: {os.path.getsize(filepath)} bytes", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nSolutions:", file=sys.stderr)
        print("- Run OpenClaw as Administrator", file=sys.stderr)
        print("- Enable 'Screen capture' in Windows Settings → Privacy", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
