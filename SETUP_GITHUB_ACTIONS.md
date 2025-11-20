# GitHub Actions 自动更新排行榜配置指南

## 📋 概述

通过 GitHub Actions，你的排行榜数据将自动从 OSS 更新到 GitHub Pages，无需手动操作。

## 🚀 配置步骤

### 1. 设置 GitHub Secrets

在你的 GitHub 仓库中设置以下 Secrets：

1. 访问你的仓库页面
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下 secrets：

| Secret Name | Value | 说明 |
|------------|-------|------|
| `OSS_ACCESS_KEY_ID` | 你的 OSS Access Key ID | 阿里云 OSS 访问密钥 |
| `OSS_ACCESS_KEY_SECRET` | 你的 OSS Access Key Secret | 阿里云 OSS 访问密钥 |
| `OSS_REGION` | `http://oss-cn-shanghai.aliyuncs.com` | OSS 区域端点 (可选) |
| `OSS_BUCKET_NAME` | `opencompass` | OSS 存储桶名称 (可选) |

**重要**: 不要将这些敏感信息提交到代码仓库！

### 2. 修改 GitHub Actions 配置

编辑 `.github/workflows/update-leaderboard.yml` 文件：

```yaml
# 找到这一行，修改为你的 ATLAS_leaderboard 仓库地址
git clone https://github.com/your-username/ATLAS_leaderboard.git
```

将 `your-username` 替换为你的 GitHub 用户名。

### 3. 修改 generate_leaderboard.py

如果你的 ATLAS_leaderboard 仓库是公开的，保持原样即可。

如果是私有仓库，需要：

1. 在 GitHub Settings → Developer settings → Personal access tokens 创建一个 token
2. 在仓库 Secrets 中添加 `GH_PAT` secret
3. 修改 workflow 文件中的 clone 步骤：

```yaml
- name: Clone ATLAS_leaderboard repository
  run: |
    cd ..
    git clone https://${{ secrets.GH_PAT }}@github.com/your-username/ATLAS_leaderboard.git
```

### 4. 提交并推送到 GitHub

```bash
cd /mnt/shared-storage-user/liushudong/SSS

# 添加新文件
git add .github/workflows/update-leaderboard.yml
git add docs/generate_leaderboard.py
git add docs/leaderboard_data.json
git add SETUP_GITHUB_ACTIONS.md

# 提交
git commit -m "Add GitHub Actions for automatic leaderboard updates"

# 推送
git push origin main
```

## ⚙️ 工作流程

### 自动触发

GitHub Actions 会在以下情况下自动运行：

1. **定时触发**: 每小时的第 5 分钟自动运行（例如：1:05, 2:05, 3:05...）
2. **脚本修改**: 当 `generate_leaderboard.py` 被修改并 push 时
3. **手动触发**: 在 GitHub Actions 页面手动运行

### 执行流程

```
1. GitHub Actions 启动
   ↓
2. 安装 Python 和依赖
   ↓
3. 克隆 ATLAS_leaderboard 仓库
   ↓
4. 运行 generate_leaderboard.py
   ↓
5. 检查 leaderboard_data.json 是否有变化
   ↓
6. 如有变化，自动 commit 并 push
   ↓
7. GitHub Pages 自动部署更新
```

## 📊 查看运行状态

1. 访问你的仓库页面
2. 点击 **Actions** 标签
3. 查看 "Update ATLAS Leaderboard" 工作流的运行历史

## 🔧 手动触发更新

如果需要立即更新排行榜：

1. 访问仓库的 **Actions** 页面
2. 选择 "Update ATLAS Leaderboard" 工作流
3. 点击右上角的 **Run workflow** 按钮
4. 选择分支（通常是 main）
5. 点击绿色的 **Run workflow** 按钮

## 📝 修改更新频率

编辑 `.github/workflows/update-leaderboard.yml` 中的 `cron` 表达式：

```yaml
schedule:
  - cron: '5 * * * *'  # 每小时运行一次
```

常用的 cron 表达式：

- `*/15 * * * *` - 每 15 分钟
- `0 * * * *` - 每小时整点
- `0 */2 * * *` - 每 2 小时
- `0 0 * * *` - 每天午夜
- `0 0 * * 0` - 每周日午夜

## ⚠️ 注意事项

1. **Secrets 安全**: 永远不要在代码中硬编码 OSS 凭证
2. **频率限制**: GitHub Actions 对公开仓库免费，但有使用限制
3. **提交信息**: commit 信息中的 `[skip ci]` 可以防止无限循环
4. **权限问题**: 确保 GitHub Actions 有写入仓库的权限

## 🐛 故障排查

### 问题: Actions 运行失败

**检查**:
1. 查看 Actions 日志中的错误信息
2. 确认 Secrets 已正确设置
3. 确认 OSS 凭证有效且有读取权限

### 问题: 数据没有更新

**检查**:
1. OSS 中的数据是否确实有变化
2. Actions 是否成功运行
3. 查看 Actions 日志中的 "Check for changes" 步骤

### 问题: GitHub Pages 没有更新

**检查**:
1. GitHub Pages 设置是否正确（Settings → Pages）
2. 部署分支是否正确
3. 等待 1-2 分钟让 GitHub Pages 重新部署

## 📚 相关文档

- [GitHub Actions 文档](https://docs.github.com/actions)
- [GitHub Pages 文档](https://docs.github.com/pages)
- [GitHub Secrets 文档](https://docs.github.com/actions/security-guides/encrypted-secrets)

## 💡 优化建议

1. **缓存依赖**: 添加 Python 依赖缓存以加快构建速度
2. **通知**: 配置失败时的邮件或 Slack 通知
3. **日志**: 添加更详细的日志输出以便调试
4. **回滚**: 在更新失败时自动回滚到上一个版本

## 🎯 完成检查清单

- [ ] 在 GitHub 仓库中设置了所有必需的 Secrets
- [ ] 修改了 workflow 文件中的仓库地址
- [ ] 提交并推送了所有文件到 GitHub
- [ ] 在 Actions 页面手动运行了一次测试
- [ ] 确认 leaderboard_data.json 已成功更新
- [ ] 访问 https://liushz.github.io/SSS/ 确认页面显示正确




