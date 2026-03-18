# ClawClock 配置持久化模块
"""
负责应用数据的持久化存储（如闹钟、秒表状态等）
"""
import json
import os
from typing import Dict, Any, List, Optional
from config.constants import ALARMS_FILE

class PersistenceManager:
    """持久化管理器"""
    
    def __init__(self, data_dir: str = "."):
        """初始化持久化管理器"""
        self.data_dir = data_dir
        self.alarms_file = os.path.join(data_dir, ALARMS_FILE)
        self._alarms: List[Dict[str, Any]] = []
    
    def load_alarms(self) -> List[Dict[str, Any]]:
        """加载闹钟数据"""
        if os.path.exists(self.alarms_file):
            try:
                with open(self.alarms_file, 'r', encoding='utf-8') as f:
                    self._alarms = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  闹钟数据加载失败: {e}")
                self._alarms = []
        return self._alarms
    
    def save_alarms(self, alarms: List[Dict[str, Any]]) -> bool:
        """保存闹钟数据"""
        try:
            with open(self.alarms_file, 'w', encoding='utf-8') as f:
                json.dump(alarms, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"⚠️  闹钟数据保存失败: {e}")
            return False
    
    def add_alarm(self, time_str: str, label: str = "", enabled: bool = True, 
                  repeat_days: List[int] = None, sound: str = "default") -> bool:
        """添加闹钟"""
        alarms = self.load_alarms()
        
        alarm = {
            "time": time_str,
            "label": label,
            "enabled": enabled,
            "sound": sound,
            "repeat_days": repeat_days or []
        }
        alarms.append(alarm)
        
        return self.save_alarms(alarms)
    
    def remove_alarm(self, index: int) -> bool:
        """删除闹钟"""
        alarms = self.load_alarms()
        
        if 0 <= index < len(alarms):
            alarms.pop(index)
            return self.save_alarms(alarms)
        return False
    
    def toggle_alarm(self, index: int, enabled: bool = None) -> bool:
        """切换闹钟启停状态"""
        alarms = self.load_alarms()
        
        if 0 <= index < len(alarms):
            if enabled is not None:
                alarms[index]["enabled"] = enabled
            else:
                alarms[index]["enabled"] = not alarms[index]["enabled"]
            return self.save_alarms(alarms)
        return False
    
    def clear_alarms(self) -> bool:
        """清空所有闹钟"""
        return self.save_alarms([])
    
    def load_stopwatch_state(self) -> Optional[Dict[str, Any]]:
        """加载秒表状态"""
        return self._load_state("stopwatch")
    
    def save_stopwatch_state(self, state: Dict[str, Any]) -> bool:
        """保存秒表状态"""
        return self._save_state("stopwatch", state)
    
    def load_timer_state(self) -> Optional[Dict[str, Any]]:
        """加载倒计时状态"""
        return self._load_state("timer")
    
    def save_timer_state(self, state: Dict[str, Any]) -> bool:
        """保存倒计时状态"""
        return self._save_state("timer", state)
    
    def _load_state(self, name: str) -> Optional[Dict[str, Any]]:
        """加载通用状态"""
        state_file = os.path.join(self.data_dir, f"{name}_state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return None
    
    def _save_state(self, name: str, state: Dict[str, Any]) -> bool:
        """保存通用状态"""
        state_file = os.path.join(self.data_dir, f"{name}_state.json")
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            return True
        except IOError:
            return False


# 全局持久化管理器实例
_persistence_manager: Optional[PersistenceManager] = None


def get_persistence_manager() -> PersistenceManager:
    """获取全局持久化管理器实例"""
    global _persistence_manager
    if _persistence_manager is None:
        _persistence_manager = PersistenceManager()
    return _persistence_manager
