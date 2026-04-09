# Step 1 - VPS 基础层重建清单

## 目标
- 把 VPS 从“单项目临时机”重建为“多项目标准宿主机”

## 适用环境
- VPS 提供商：Vultr
- SSH 客户端：Termius
- 目标系统：Ubuntu 24.04 LTS

## Step 1 输出结果
- 一台干净的 Ubuntu VPS
- 可通过 Termius 正常登录
- 完成安全加固
- 完成基础软件安装
- 完成多项目目录标准化
- 完成项目运行用户规划

## 1. 重建 VPS 时的建议规格

### 最低建议
- 2 vCPU
- 4 GB RAM
- 80 GB SSD

### 如果未来项目会增加
- 4 vCPU
- 8 GB RAM
- 160 GB SSD

## 2. Vultr 创建时建议
- OS 选择 `Ubuntu 24.04 LTS`
- 开启自动备份
- 绑定 SSH Key
- 不建议长期依赖 root 密码登录

## 3. Termius 连接规范
- Host Label: `vultr-m33-prod`
- Username: `root`
- Authentication: SSH Key
- 首次连接后记录：
- 公网 IP
- 区域
- SSH 端口
- root 是否可直连

## 4. 首次登录后立即执行

```bash
apt update && apt upgrade -y
timedatectl set-timezone Asia/Kuala_Lumpur
apt install -y git curl wget unzip zip htop ufw nginx logrotate python3 python3-venv python3-pip
```

## 5. 创建标准目录

```bash
mkdir -p /srv/apps
mkdir -p /srv/configs
mkdir -p /srv/data
mkdir -p /srv/logs
mkdir -p /srv/backups
```

## 6. 创建运维用户

```bash
adduser bryan
usermod -aG sudo bryan
```

## 7. 创建项目运行用户

```bash
adduser --system --group --home /srv/apps/m33-bot m33
```

## 8. 建立 M33 专用目录

```bash
mkdir -p /srv/apps/m33-bot
mkdir -p /srv/configs/m33-bot
mkdir -p /srv/data/m33-bot
mkdir -p /srv/logs/m33-bot
mkdir -p /srv/backups/m33-bot
chown -R m33:m33 /srv/apps/m33-bot /srv/configs/m33-bot /srv/data/m33-bot /srv/logs/m33-bot /srv/backups/m33-bot
```

## 9. SSH 基础加固
- 优先使用 SSH Key
- 如果确认 key 正常，再考虑关闭密码登录
- 如果确认有非 root sudo 用户，再考虑限制 root 远程登录

暂不建议第一分钟就锁死 SSH，避免把自己关在门外。

## 10. 防火墙建议

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
ufw status
```

## 11. Step 1 验收标准
- Termius 可稳定连接 VPS
- `bryan` 用户可 sudo
- `/srv` 标准目录已创建
- `m33` 用户已创建
- Python / git / nginx / ufw 已安装
- 时区正确
- 防火墙已开启

## 12. Step 1 完成后不要立刻做的事
- 不要先手工上传一堆文件
- 不要把 `.env` 和数据库丢进 Git 仓库
- 不要继续让 bot 直接跑在 root 用户下
- 不要把多个 bot 混成一个后台脚本硬跑

## 13. Step 2 预告
- 从 GitHub 拉取 `M33_BOT`
- 创建 Python 虚拟环境
- 分离 bot 配置与数据目录
- 为 bot1 / bot2 / bot3 准备启动方式

