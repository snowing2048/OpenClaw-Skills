#!/usr/bin/env python3
"""
Auto Screenshot Module - 通用截图辅助模块
供 browser-agent 各脚本复用

Usage:
    from auto_screenshot import AutoScreenshotter
    
    shot = AutoScreenshotter(output_dir="C:/path/to/output")
    before = shot.capture("before")
    # ... 执行操作 ...
    after = shot.capture("after")
    shot.save_metadata("click", {"x": 100, "y": 200}, before, after)
"""
import os
import json
import base64
import io
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


class AutoScreenshotter:
    """自动截图器，支持操作前后截图和元数据保存"""
    
    def __init__(self, output_dir=None):
        """
        初始化截图器
        
        Args:
            output_dir: 输出目录，默认使用 tmp/_artifacts/screenshots
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path(__file__).parent.parent / "tmp" / "_artifacts" / "screenshots"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def capture(self, prefix="screenshot_", suffix=""):
        """
        截图并保存
        
        Args:
            prefix: 文件名前缀
            suffix: 文件名后缀
            
        Returns:
            dict: {success: bool, path: str, filename: str, timestamp: str}
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
            filename = f"{prefix}{timestamp}{suffix}.png"
            filepath = self.output_dir / filename
            
            screenshot = self._capture_screen()
            screenshot.save(filepath)
            
            return {
                "success": True,
                "path": str(filepath),
                "filename": filename,
                "timestamp": timestamp,
                "session_id": self.session_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _capture_screen(self):
        """内部截图方法"""
        if pyautogui:
            try:
                return pyautogui.screenshot()
            except Exception:
                pass
        
        if ImageGrab:
            try:
                return ImageGrab.grab()
            except Exception:
                pass
        
        raise Exception("All screenshot methods failed")
    
    def save_metadata(self, operation_type, params, before_shot=None, after_shot=None):
        """
        保存操作元数据
        
        Args:
            operation_type: 操作类型 (click, type, keypress, etc.)
            params: 操作参数 dict
            before_shot: 操作前截图信息 dict
            after_shot: 操作后截图信息 dict
            
        Returns:
            str: 元数据文件路径，失败返回 None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metadata = {
                "operation": operation_type,
                "params": params,
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "before_screenshot": before_shot,
                "after_screenshot": after_shot
            }
            
            meta_file = self.output_dir / f"{operation_type}_{timestamp}.json"
            
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return str(meta_file)
        except Exception as e:
            print(f"Failed to save metadata: {e}")
            return None
    
    def capture_sequence(self, operation_type, params, execute_fn):
        """
        执行操作并自动截图（前后）
        
        Args:
            operation_type: 操作类型
            params: 操作参数
            execute_fn: 执行操作的函数
            
        Returns:
            dict: {success: bool, result: any, before: dict, after: dict, metadata: str}
        """
        # 操作前截图
        before = self.capture(f"{operation_type}_before_")
        
        # 执行操作
        try:
            result = execute_fn()
            success = True
        except Exception as e:
            result = str(e)
            success = False
        
        # 操作后截图
        after = self.capture(f"{operation_type}_after_")
        
        # 保存元数据
        metadata_file = self.save_metadata(operation_type, params, before, after)
        
        return {
            "success": success,
            "result": result,
            "before": before,
            "after": after,
            "metadata": metadata_file
        }
    
    def get_session_dir(self):
        """获取当前会话目录"""
        session_dir = self.output_dir / self.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir


# 便捷函数
def quick_screenshot(output_dir=None, filename=None):
    """快速截图，返回 base64 和文件路径"""
    shot = AutoScreenshotter(output_dir)
    
    if not filename:
        filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    filepath = shot.output_dir / filename
    screenshot = shot._capture_screen()
    screenshot.save(filepath)
    
    buffered = io.BytesIO()
    screenshot.save(buffered, format="PNG")
    base64_data = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        "base64": base64_data,
        "path": str(filepath),
        "filename": filename
    }


if __name__ == "__main__":
    # 测试
    shot = AutoScreenshotter()
    result = shot.capture_sequence(
        "test",
        {"note": "test operation"},
        lambda: print("Test operation executed")
    )
    
    print(f"Success: {result['success']}")
    print(f"Before: {result['before'].get('path', 'N/A')}")
    print(f"After: {result['after'].get('path', 'N/A')}")
    print(f"Metadata: {result['metadata']}")
