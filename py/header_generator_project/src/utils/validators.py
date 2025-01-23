import re
from typing import List, Union

class DQMapValidator:
    """DQ Map 資料驗證器"""
    
    def __init__(self):
        self.dram_groups = ['MA', 'MB', 'MC', 'MD']
        self.valid_pin_pattern = re.compile(r'^[M][A-D][0-1]_DQ_[0-9A-F]{2}$')

    def validate_pin_name(self, pin_name: str) -> bool:
        """驗證 PIN 名稱格式"""
        if not isinstance(pin_name, str):
            return False
        return bool(self.valid_pin_pattern.match(pin_name))

    def validate_pin_number(self, pin_name: str) -> bool:
        """驗證 PIN 編號範圍"""
        if not self.validate_pin_name(pin_name):
            return False
        pin_num = pin_name.split('_')[-1]
        return 0x00 <= int(pin_num, 16) <= 0x1F

    def get_required_columns(self) -> List[str]:
        """獲取必要的欄位名稱列表"""
        columns = []
        for side in ['A', 'B']:
            for i in range(16):
                columns.append(f"DQ_{i:02d}_{side}")
        return columns