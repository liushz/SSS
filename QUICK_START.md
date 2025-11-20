# 🚀 GitHub Actions 快速配置指南

## ⏱️ 5 分钟完成配置

### 步骤 1: 在 GitHub 上设置 Secrets (2 分钟)

1. 访问你的 SSS 仓库: `https://github.com/your-username/SSS`
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret** 添加以下内容:

```
名称: OSS_ACCESS_KEY_ID
值: [你的阿里云 OSS Access Key ID]
```

```
名称: OSS_ACCESS_KEY_SECRET  
值: [你的阿里云 OSS Access Key Secret]
```

### 步骤 2: 提交并推送 (2 分钟)

```bash
cd /mnt/shared-storage-user/liushudong/SSS

# 添加所有文件
git add .github/ docs/oss_utils/ docs/generate_leaderboard.py docs/index.html SETUP_GITHUB_ACTIONS.md QUICK_START.md

# 提交
git commit -m "🚀 Add GitHub Actions for auto-updating leaderboard"

# 推送到 GitHub
git push origin main
```

### 步骤 3: 验证设置 (立即)

1. 访问 `https://github.com/your-username/SSS/actions`
2. 点击 "Update ATLAS Leaderboard" workflow
3. 点击右上角 **Run workflow** → 选择 **main** → **Run workflow**
4. 等待 1-2 分钟查看运行结果

## ✅ 检查清单

- [ ] 已在 GitHub 添加 `OSS_ACCESS_KEY_ID` Secret
- [ ] 已在 GitHub 添加 `OSS_ACCESS_KEY_SECRET` Secret  
- [ ] 已提交并推送到 GitHub
- [ ] 已手动运行一次 workflow 测试
- [ ] 访问 https://liushz.github.io/SSS/ 确认显示正确

## 📊 预期结果

- GitHub Actions 每小时自动运行一次
- 自动从 OSS 读取最新排行榜数据
- 自动更新 `docs/leaderboard_data.json`
- GitHub Pages 自动部署更新的页面
- 访问 https://liushz.github.io/SSS/ 看到最新数据

## 🐛 遇到问题？

### Actions 运行失败

查看 Actions 日志:
1. 访问 `https://github.com/your-username/SSS/actions`
2. 点击失败的运行
3. 查看详细日志

常见错误:
- **Missing environment variables**: 检查 Secrets 是否正确设置
- **Permission denied**: 检查 OSS 凭证权限
- **Module not found**: 确保 oss_utils 目录已正确提交

### 数据没有更新

1. 确认 OSS 中确实有新数据
2. 查看 Actions 运行日志中的 "Check for changes" 步骤
3. 手动触发 workflow 测试

## 📚 更多文档

- 详细配置: 查看 `SETUP_GITHUB_ACTIONS.md`
- 排行榜说明: 查看 `docs/README_LEADERBOARD.md`

## 💡 提示

- 首次运行可能需要 2-3 分钟
- 后续运行如果数据无变化会跳过提交
- commit 信息中的 `[skip ci]` 防止触发无限循环

