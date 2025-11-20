#!/bin/bash
# 自动更新排行榜数据的脚本
# 可以通过 crontab 定时执行，例如每小时更新一次：
# 0 * * * * /path/to/update_leaderboard.sh

cd "$(dirname "$0")"

echo "🔄 Updating ATLAS leaderboard data..."
python3 generate_leaderboard.py

if [ $? -eq 0 ]; then
    echo "✅ Leaderboard data updated successfully at $(date)"
else
    echo "❌ Failed to update leaderboard data at $(date)"
    exit 1
fi




