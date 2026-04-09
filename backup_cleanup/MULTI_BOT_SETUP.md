# 多Bot配置管理指南

## 概述

本系统现在支持同时运行多个Telegram Bot，每个bot有独立的配置。你只需要在一个配置文件中管理所有bot的token和其他设置。

## 文件结构

```
.env.multi          # 主配置文件（所有bot配置都在这里）
configs/            # 自动生成的bot配置目录
  bot_1/            # Bot 1配置目录
    .env            # Bot 1的环境变量
    settings.json   # Bot 1的设置文件
  bot_2/            # Bot 2配置目录
    ...
setup_bots.py       # 配置设置脚本
start_all_bots_simple.py  # 批量启动脚本
```

## 快速开始

### 1. 编辑主配置文件

打开 `.env.multi` 文件，填写各个bot的配置：

```env
# ===========================================
# Bot 1 配置
# ===========================================
BOT_1_TOKEN=8713226156:AAGDHv1xd-lObWy7yAt_It7EBL3q225HMuw
BOT_1_DB_PATH=data\simple_test.db
BOT_1_CLIENT_NAME=simple_test
BOT_1_TIMEZONE=Asia/Ho_Chi_Minh

# ===========================================
# Bot 2 配置
# ===========================================
BOT_2_TOKEN=你的第二个bot_token
BOT_2_DB_PATH=data\bot2.db
BOT_2_CLIENT_NAME=客户2
BOT_2_TIMEZONE=Asia/Ho_Chi_Minh

# ===========================================
# 通用配置（所有bot共享）
# ===========================================
DEFAULT_ADMIN_USER_IDS=2063305617,6577170044
DEFAULT_LANGUAGE=vi
```

### 2. 生成配置目录

运行配置脚本：

```bash
python setup_bots.py
```

这会自动：
- 读取 `.env.multi` 文件
- 为每个配置了token的bot创建独立的配置目录
- 生成对应的 `.env` 文件

### 3. 查看已配置的bot

```bash
python setup_bots.py --list
```

### 4. 启动所有bot

```bash
python start_all_bots_simple.py
```

或者手动启动单个bot：

```bash
# 启动Bot 1
python src/app/main.py --config-dir configs/bot_1

# 启动Bot 2
python src/app/main.py --config-dir configs/bot_2
```

## 管理命令

### 清理所有配置目录

```bash
python setup_bots.py --clean
```

### 只设置特定bot

```bash
# 只设置Bot 1和Bot 3
python setup_bots.py --setup 1 3
```

## 添加新的Bot

1. 在 `.env.multi` 文件中添加新的配置段：

```env
# ===========================================
# Bot 6 配置
# ===========================================
BOT_6_TOKEN=新的bot_token
BOT_6_DB_PATH=data\bot6.db
BOT_6_CLIENT_NAME=新客户
BOT_6_TIMEZONE=Asia/Ho_Chi_Minh
```

2. 生成配置：

```bash
python setup_bots.py --setup 6
```

3. 启动新的bot：

```bash
python src/app/main.py --config-dir configs/bot_6
```

## 注意事项

1. **Token安全**：确保 `.env.multi` 文件不被泄露
2. **数据库路径**：每个bot使用独立的数据库文件，避免数据混淆
3. **时区设置**：所有bot默认使用越南时区，可根据需要修改
4. **日志文件**：每个bot的日志会输出到控制台，可通过修改配置指定日志文件

## 故障排除

### 问题：Bot启动失败，提示token无效
- 检查token是否正确
- 确保token已通过BotFather激活

### 问题：数据库错误
- 检查数据库文件路径是否存在
- 确保有写入权限

### 问题：配置未生效
- 运行 `python setup_bots.py --clean` 清理后重新生成
- 检查 `.env.multi` 文件格式是否正确

## 高级用法

### 自定义每个bot的设置

每个bot目录中的 `settings.json` 文件可以自定义：
- 功能开关（投注、报表、结算等）
- UI设置（货币符号、日期格式等）
- 限制设置（最大投注金额、每日投注次数等）
- 佣金设置

### 独立日志文件

在 `.env.multi` 中为每个bot指定不同的日志文件：

```env
BOT_1_LOG_PATH=logs/bot1.log
BOT_2_LOG_PATH=logs/bot2.log
```

## 支持

如有问题，请检查日志输出或联系开发人员。