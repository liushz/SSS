# ATLAS 排行榜数据更新说明

## 概述

私有集排行榜 (Private Leaderboard) 的数据从 OSS 存储中动态加载，而不是硬编码在 HTML 中。

## 工作原理

1. **数据源**: 排行榜数据存储在阿里云 OSS 的 `atlas_eval/leaderboard/leaderboard.json`
2. **数据生成**: `generate_leaderboard.py` 脚本从 OSS 读取数据并生成 `leaderboard_data.json`
3. **前端展示**: HTML 页面通过 JavaScript 的 `fetch` API 读取 `leaderboard_data.json` 并动态渲染

## 使用方法

### 手动更新

运行以下命令手动更新排行榜数据：

```bash
cd /mnt/shared-storage-user/liushudong/SSS/docs
python3 generate_leaderboard.py
```

或使用 shell 脚本：

```bash
./update_leaderboard.sh
```

### 自动更新 (推荐)

使用 crontab 设置定时任务，每小时自动更新一次：

```bash
# 编辑 crontab
crontab -e

# 添加以下行 (每小时的第 0 分钟执行)
0 * * * * /mnt/shared-storage-user/liushudong/SSS/docs/update_leaderboard.sh >> /mnt/shared-storage-user/liushudong/SSS/docs/update_leaderboard.log 2>&1
```

或者每 15 分钟更新一次：

```bash
*/15 * * * * /mnt/shared-storage-user/liushudong/SSS/docs/update_leaderboard.sh >> /mnt/shared-storage-user/liushudong/SSS/docs/update_leaderboard.log 2>&1
```

## 环境变量

确保设置了以下环境变量：

- `OSS_ACCESS_KEY_ID`: 阿里云 OSS 访问密钥 ID
- `OSS_ACCESS_KEY_SECRET`: 阿里云 OSS 访问密钥 Secret
- `OSS_REGION`: OSS 区域端点 (默认: http://oss-cn-shanghai.aliyuncs.com)
- `OSS_BUCKET_NAME`: OSS 存储桶名称 (默认: opencompass)

## 文件结构

```
docs/
├── index.html                  # 主页面，包含排行榜展示逻辑
├── leaderboard_data.json       # 排行榜数据文件 (由脚本生成)
├── generate_leaderboard.py     # 从 OSS 读取数据的 Python 脚本
├── update_leaderboard.sh       # 更新脚本
└── README_LEADERBOARD.md       # 本文档
```

## 数据格式

`leaderboard_data.json` 的格式：

```json
{
  "last_updated": "2025-01-19T12:00:00Z",
  "total_entries": 10,
  "leaderboard": [
    {
      "rank": 1,
      "model": "GPT-4",
      "organization": "OpenAI",
      "access": "API",
      "accuracy": 42.5,
      "mg_pass_2": 32.1,
      "mg_pass_4": 30.5,
      "tokens": "32k",
      "submitted_time": "2025-01-15"
    }
  ]
}
```

## 故障排查

### 问题: 页面显示静态数据

**原因**: `leaderboard_data.json` 不存在或加载失败

**解决**: 
1. 检查 `leaderboard_data.json` 文件是否存在
2. 运行 `python3 generate_leaderboard.py` 生成数据
3. 检查浏览器控制台的错误信息

### 问题: Python 脚本报错

**原因**: OSS 环境变量未设置或网络连接问题

**解决**:
1. 确认环境变量已正确设置
2. 测试 OSS 连接：`python3 -c "from src.oss.oss_leaderboard_manager import OSSLeaderboardManager; m = OSSLeaderboardManager(); print(m.load_leaderboard_from_oss())"`

### 问题: CORS 错误

**原因**: 本地文件系统不允许跨域请求

**解决**: 使用本地 HTTP 服务器运行：
```bash
python3 -m http.server 8000
# 然后访问 http://localhost:8000/index.html
```

## 注意事项

1. 确保 Python 脚本有权限访问 ATLAS_leaderboard 的代码
2. 定时任务的路径必须是绝对路径
3. 建议将更新日志输出到文件以便排查问题
4. 如果更新失败，页面会继续显示旧数据或静态数据




