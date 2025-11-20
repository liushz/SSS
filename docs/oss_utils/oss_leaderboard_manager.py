#!/usr/bin/env python3
"""
OSS排行榜管理器 - 从OSS读取和更新排行榜数据
"""

import os
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from oss_utils.oss_file_manager import OSSFileManager


class OSSLeaderboardManager:
    """OSS排行榜管理器 - 管理存储在OSS中的排行榜数据"""
    
    def __init__(self):
        """初始化OSS排行榜管理器"""
        self.oss_manager = OSSFileManager()
        
        # OSS路径配置
        self.leaderboard_path = "atlas_eval/leaderboard/"
        self.backup_path = "atlas_eval/leaderboard/backup/"
        self.leaderboard_file = "leaderboard.json"
        
        # 完整的OSS路径
        self.oss_leaderboard_file = f"{self.leaderboard_path}{self.leaderboard_file}"
        
        print(f"📊 OSS leaderboard path: oss://opencompass/{self.oss_leaderboard_file}")
        print(f"📦 OSS backup path: oss://opencompass/{self.backup_path}")
    
    def load_leaderboard_from_oss(self) -> List[Dict[str, Any]]:
        """
        从OSS加载排行榜数据
        
        Returns:
            排行榜数据列表
        """
        try:
            print(f"📥 Loading leaderboard data from OSS: {self.oss_leaderboard_file}")
            
            # 从OSS下载文件内容
            content = self.oss_manager.download_file_content(self.oss_leaderboard_file)
            
            if content:
                leaderboard_data = json.loads(content.decode('utf-8'))
                print(f"✅ Successfully loaded {len(leaderboard_data)} leaderboard entries")
                return leaderboard_data
            else:
                print("⚠️ No leaderboard file found in OSS, returning empty list")
                return []
                
        except Exception as e:
            print(f"❌ Failed to load leaderboard from OSS: {e}")
            return []
    
    def save_leaderboard_to_oss(self, leaderboard_data: List[Dict[str, Any]], 
                               create_backup: bool = True) -> bool:
        """
        保存排行榜数据到OSS
        
        Args:
            leaderboard_data: 排行榜数据
            create_backup: 是否创建备份
            
        Returns:
            是否保存成功
        """
        try:
            print(f"📤 Saving leaderboard data to OSS: {self.oss_leaderboard_file}")
            
            # 创建备份（如果需要且现有文件存在）
            if create_backup:
                self._create_backup()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(leaderboard_data, temp_file, indent=2, ensure_ascii=False)
                temp_file_path = temp_file.name
            
            try:
                # 上传到OSS
                success = self.oss_manager.upload_file(
                    local_file_path=temp_file_path,
                    oss_file_path=self.oss_leaderboard_file
                )
                
                if success:
                    print(f"✅ Successfully saved {len(leaderboard_data)} leaderboard entries to OSS")
                    return True
                else:
                    print("❌ Failed to upload leaderboard file to OSS")
                    return False
                    
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Failed to save leaderboard to OSS: {e}")
            return False
    
    def _create_backup(self) -> bool:
        """
        创建当前排行榜文件的备份
        
        Returns:
            是否备份成功
        """
        try:
            # 检查原文件是否存在
            if not self.oss_manager.file_exists(self.oss_leaderboard_file):
                print("📋 Original leaderboard file does not exist, skipping backup")
                return True
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"leaderboard.json.backup_{timestamp}"
            backup_path = f"{self.backup_path}{backup_filename}"
            
            # 复制文件到备份路径
            success = self.oss_manager.copy_file(
                source_path=self.oss_leaderboard_file,
                target_path=backup_path
            )
            
            if success:
                print(f"📦 Backup created successfully: {backup_path}")
                return True
            else:
                print(f"❌ Failed to create backup: {backup_path}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
    
    def add_evaluation_result(self, result_data: Dict[str, Any]) -> bool:
        """
        添加新的评测结果到排行榜
        
        Args:
            result_data: 评测结果数据
            
        Returns:
            是否添加成功
        """
        try:
            # 加载现有排行榜
            leaderboard_data = self.load_leaderboard_from_oss()
            
            # 检查是否已存在相同的提交（基于organization和submitted_time）
            existing_entry = None
            for i, entry in enumerate(leaderboard_data):
                if (entry.get("organization") == result_data.get("organization") and 
                    entry.get("submitted_time") == result_data.get("submitted_time")):
                    existing_entry = i
                    break
            
            if existing_entry is not None:
                print(f"🔄 Updating existing leaderboard entry: {result_data.get('organization')}")
                leaderboard_data[existing_entry] = result_data
            else:
                print(f"➕ Adding new leaderboard entry: {result_data.get('organization')}")
                leaderboard_data.append(result_data)
            
            # 按准确率排序
            leaderboard_data.sort(
                key=lambda x: x.get("accuracy", 0), 
                reverse=True
            )
            
            # 保存到OSS
            return self.save_leaderboard_to_oss(leaderboard_data)
            
        except Exception as e:
            print(f"❌ Failed to add evaluation result: {e}")
            return False
    
    def get_leaderboard_summary(self) -> Dict[str, Any]:
        """
        获取排行榜摘要信息
        
        Returns:
            排行榜摘要
        """
        try:
            leaderboard_data = self.load_leaderboard_from_oss()
            
            if not leaderboard_data:
                return {"total_entries": 0, "last_updated": None}
            
            # 统计信息
            total_entries = len(leaderboard_data)
            
            # 获取最新更新时间
            latest_time = None
            for entry in leaderboard_data:
                eval_time = entry.get("evaluation_timestamp")
                if eval_time and (latest_time is None or eval_time > latest_time):
                    latest_time = eval_time
            
            # 获取最高分
            top_scores = {}
            if leaderboard_data:
                top_entry = leaderboard_data[0]  # 已按准确率排序
                top_scores = {
                    "accuracy": top_entry.get("accuracy", 0),
                    "mg_pass_2": top_entry.get("mg_pass_2", 0),
                    "mg_pass_4": top_entry.get("mg_pass_4", 0)
                }
            
            return {
                "total_entries": total_entries,
                "last_updated": latest_time,
                "top_scores": top_scores,
                "oss_path": self.oss_leaderboard_file
            }
            
        except Exception as e:
            print(f"❌ Failed to get leaderboard summary: {e}")
            return {"error": str(e)}
    
    def migrate_local_to_oss(self, local_file_path: str) -> bool:
        """
        将本地排行榜文件迁移到OSS
        
        Args:
            local_file_path: 本地文件路径
            
        Returns:
            是否迁移成功
        """
        try:
            if not os.path.exists(local_file_path):
                print(f"❌ Local file does not exist: {local_file_path}")
                return False
            
            # 读取本地文件
            with open(local_file_path, 'r', encoding='utf-8') as f:
                leaderboard_data = json.load(f)
            
            print(f"📤 Migrating {len(leaderboard_data)} entries to OSS")
            
            # 保存到OSS
            return self.save_leaderboard_to_oss(leaderboard_data, create_backup=False)
            
        except Exception as e:
            print(f"❌ Failed to migrate file to OSS: {e}")
            return False


if __name__ == "__main__":
    # 测试OSS排行榜管理器
    manager = OSSLeaderboardManager()
    
    # 打印摘要信息
    summary = manager.get_leaderboard_summary()
    print(f"📊 Leaderboard summary: {summary}")
    
    # 测试加载排行榜
    leaderboard = manager.load_leaderboard_from_oss()
    print(f"📋 Number of leaderboard entries: {len(leaderboard)}")
