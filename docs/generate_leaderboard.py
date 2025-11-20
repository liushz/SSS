#!/usr/bin/env python3
"""
从 OSS 读取排行榜数据并生成 JSON 文件供前端使用

环境要求:
- pip install oss2 loguru
- 设置环境变量: OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET

使用场景:
1. 本地测试: 直接运行此脚本
2. GitHub Actions: 自动定时运行
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 检查必需的环境变量
required_env_vars = ['OSS_ACCESS_KEY_ID', 'OSS_ACCESS_KEY_SECRET']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these variables before running the script.")
    sys.exit(1)

# 导入 OSS 工具
try:
    from oss_utils.oss_leaderboard_manager import OSSLeaderboardManager
except ImportError as e:
    print(f"❌ Failed to import OSSLeaderboardManager: {e}")
    print("Please ensure 'oss2' and 'loguru' are installed:")
    print("  pip install oss2 loguru")
    sys.exit(1)


def generate_leaderboard_json():
    """从 OSS 读取排行榜数据并生成 JSON 文件"""
    try:
        print("📥 Loading leaderboard data from OSS...")
        
        # 创建 OSS 排行榜管理器
        manager = OSSLeaderboardManager()
        
        # 从 OSS 加载排行榜数据
        leaderboard_data = manager.load_leaderboard_from_oss()
        
        if not leaderboard_data:
            print("⚠️ No leaderboard data found in OSS")
            # 创建一个空的 JSON 文件
            output_data = {
                "last_updated": "",
                "total_entries": 0,
                "leaderboard": []
            }
        else:
            print(f"✅ Loaded {len(leaderboard_data)} entries")
            
            # 按准确率排序
            leaderboard_data.sort(key=lambda x: x.get("accuracy", 0), reverse=True)
            
            # 格式化数据为前端需要的格式
            formatted_data = []
            for idx, entry in enumerate(leaderboard_data, 1):
                formatted_entry = {
                    "rank": idx,
                    "model": entry.get("model_name", "Unknown"),
                    "organization": entry.get("organization", "Unknown"),
                    "access": entry.get("access_type", "API"),  # 从数据中读取访问类型
                    "accuracy": round(entry.get("accuracy", 0), 1),
                    "mg_pass_2": round(entry.get("mg_pass_2", 0), 1),
                    "mg_pass_4": round(entry.get("mg_pass_4", 0), 1),
                    "tokens": entry.get("tokens", "32k"),
                    "submitted_time": entry.get("submitted_time", "")
                }
                formatted_data.append(formatted_entry)
            
            # 获取最新更新时间
            last_updated = ""
            if leaderboard_data:
                # 尝试从第一条记录获取评估时间戳
                last_updated = leaderboard_data[0].get("evaluation_timestamp", "")
                if not last_updated:
                    # 如果没有，使用当前时间
                    last_updated = datetime.utcnow().isoformat() + "Z"
            
            output_data = {
                "last_updated": last_updated,
                "total_entries": len(formatted_data),
                "leaderboard": formatted_data
            }
        
        # 保存为 JSON 文件
        output_file = Path(__file__).parent / "leaderboard_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Leaderboard data saved to: {output_file}")
        print(f"📊 Total entries: {output_data['total_entries']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating leaderboard JSON: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = generate_leaderboard_json()
    sys.exit(0 if success else 1)
