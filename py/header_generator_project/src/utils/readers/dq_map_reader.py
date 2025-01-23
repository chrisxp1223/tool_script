import pandas as pd
from typing import Tuple, List
import os
from ..utils.validators import DQMapValidator

class DQMapReader:
    """DQ Map Excel 檔案讀取器"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.validator = DQMapValidator()
        self.data = None

    def read_and_validate(self) -> Tuple[bool, List[str]]:
        """讀取並驗證 Excel 檔案"""
        try:
            if not self._validate_file_exists():
                return False, ["檔案不存在"]
                
            self.data = pd.read_excel(self.file_path)
            return self._validate_data()
            
        except Exception as e:
            return False, [f"錯誤：{str(e)}"]

    def _validate_file_exists(self) -> bool:
        """驗證檔案是否存在"""
        return os.path.exists(self.file_path)

    def _validate_data(self) -> Tuple[bool, List[str]]:
        """驗證數據格式和內容"""
        errors = []
        
        # 檢查必要欄位
        required_columns = self.validator.get_required_columns()
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        if missing_columns:
            errors.append(f"缺少必要欄位：{', '.join(missing_columns)}")

        # 檢查數據值
        for col in self.data.columns:
            for idx, value in enumerate(self.data[col]):
                if pd.isna(value):
                    errors.append(f"第 {idx+1} 行的 {col} 包含空值")
                elif not self.validator.validate_pin_name(str(value)):
                    errors.append(f"第 {idx+1} 行的 {col} 格式錯誤：{value}")
                elif not self.validator.validate_pin_number(str(value)):
                    errors.append(f"第 {idx+1} 行的 {col} PIN 編號超出範圍：{value}")

        return (len(errors) == 0, errors)

    def get_data(self) -> pd.DataFrame:
        """獲取驗證後的數據"""
        return self.data