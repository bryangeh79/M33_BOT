# Step 1A - 清理 VPS 旧 M33 部署

## 目标
- 删除 VPS 上所有旧的 M33 代码、旧配置、旧日志、旧进程托管残留
- 为新的标准化目录布局腾出干净环境

## 适用人群
- 第一次使用 Termius / VPS / Ubuntu
- 需要按步骤执行，不跳步

## 执行原则
- 先检查，再停止，再删除
- 每一步执行后都核对结果
- 不直接上来 `rm -rf /`
- 不删除不确定用途的系统目录

## 本步骤分 4 段

### A. 先连接 VPS
- 在 Termius 里点击你的 `M33`
- 登录用户先用 `root`

### B. 先做只读检查
执行：

```bash
pwd
find /root /home /opt /srv -maxdepth 4 \( -iname "*m33*" -o -iname "*lotto*" -o -iname "*bot*" -o -name "*.db" -o -name ".env" \) 2>/dev/null
ps -ef | grep -E "python|pm2|supervisord|supervisor|node" | grep -v grep
systemctl list-units --type=service | grep -Ei "m33|bot|pm2|supervisor"
```

如果装过 PM2，再执行：

```bash
pm2 list
```

如果装过 Supervisor，再执行：

```bash
supervisorctl status
```

### C. 停掉旧服务

#### 1. 如果是 systemd
先找服务名，再停：

```bash
systemctl stop 服务名
systemctl disable 服务名
```

#### 2. 如果是 PM2

```bash
pm2 stop all
pm2 delete all
pm2 save
```

#### 3. 如果是 Supervisor

```bash
supervisorctl stop all
```

### D. 删除旧 M33 文件

只删除确认属于 M33 的目录，例如：

```bash
rm -rf /root/M33*
rm -rf /root/*m33*
rm -rf /opt/M33*
rm -rf /opt/*m33*
rm -rf /srv/apps/m33-bot
rm -rf /srv/configs/m33-bot
rm -rf /srv/data/m33-bot
rm -rf /srv/logs/m33-bot
rm -rf /srv/backups/m33-bot
```

如果旧 bot 数据库散落在别处，再按检查结果单独删除，不要盲删整个目录。

## 新手实际执行顺序

### 第 1 步：先查旧目录
```bash
find /root /home /opt /srv -maxdepth 4 \( -iname "*m33*" -o -iname "*lotto*" -o -iname "*bot*" -o -name "*.db" -o -name ".env" \) 2>/dev/null
```

### 第 2 步：查旧进程
```bash
ps -ef | grep -E "python|pm2|supervisord|supervisor|node" | grep -v grep
```

### 第 3 步：查旧 systemd
```bash
systemctl list-units --type=service | grep -Ei "m33|bot|pm2|supervisor"
```

### 第 4 步：按实际情况停服务

### 第 5 步：删旧目录

### 第 6 步：复查是否删干净
```bash
find /root /home /opt /srv -maxdepth 4 \( -iname "*m33*" -o -iname "*lotto*" -o -iname "*bot*" -o -name "*.db" -o -name ".env" \) 2>/dev/null
ps -ef | grep -E "python|pm2|supervisord|supervisor|node" | grep -v grep
systemctl list-units --type=service | grep -Ei "m33|bot|pm2|supervisor"
```

## 完成标准
- 找不到旧 M33 目录
- 找不到旧 M33 bot 进程
- 找不到旧 M33 systemd/PM2/Supervisor 托管残留

## 下一步
- 进入 `Step 1` 正式基础层重建

