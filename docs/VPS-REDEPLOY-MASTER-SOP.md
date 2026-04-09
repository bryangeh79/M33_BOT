# M33 Bot VPS 重建总蓝图

## 目标
- 重新部署一台干净的 Vultr VPS
- 使用 Termius 作为日常 SSH 管理工具
- 让 M33 Bot 成为 VPS 上的一个标准化项目，而不是唯一项目
- 为未来上线多个项目预留统一目录、权限、日志、备份和进程管理规范

## 部署原则
- 代码只从 GitHub 拉取，不再手工散落上传
- 配置、代码、数据、日志分离
- 一个长期服务一个 `systemd service`
- 每个项目独立目录、独立虚拟环境、独立运行用户
- 敏感信息不进 Git 仓库
- 所有部署动作都沉淀为 SOP，避免下次重复踩坑

## 当前推荐架构

### 目录结构
```text
/srv/
  apps/
    m33-bot/
    project-b/
  configs/
    m33-bot/
    project-b/
  data/
    m33-bot/
    project-b/
  logs/
    m33-bot/
    project-b/
  backups/
    m33-bot/
    project-b/
```

### 运行层
- 操作系统：Ubuntu 24.04 LTS
- SSH 工具：Termius
- 代码源：GitHub
- Python 运行：每项目独立 `venv`
- 进程托管：`systemd`
- Web 入口：`nginx`
- 定时任务：`cron`
- 日志轮转：`logrotate`

## 分阶段执行

### Step 1A: 清理旧 M33 部署
- 盘点旧目录、旧进程、旧服务
- 停掉旧 systemd / PM2 / Supervisor
- 删除旧 M33 代码、配置、日志、数据库残留
- 确认 VPS 回到可重新规划的干净状态

### Step 1: VPS 基础层重建
- 重建 VPS
- 建立统一目录规范
- 安装基础依赖
- 建立非 root 运维用户
- 准备 Python / git / nginx / systemd / 防火墙

### Step 2: GitHub 拉取与项目目录部署
- 从 GitHub clone `M33_BOT`
- 创建项目运行目录
- 分离配置目录与数据库目录
- 建立 `.env` 与 bot 配置文件

### Step 3: M33 多 Bot 服务化
- 为 bot1 / bot2 / bot3 建立独立 `systemd` 服务
- 验证开机自启
- 验证日志输出
- 验证 Telegram 实际收发

### Step 4: 运维保障
- 自动备份
- 日志轮转
- 资源监控
- 故障恢复 SOP

### Step 5: 多项目共存模板
- 新项目接入模板
- nginx 反向代理模板
- systemd 模板
- 统一上线流程模板

## 当前状态
- GitHub 代码仓已完成推送
- 下一步执行：`Step 1`
