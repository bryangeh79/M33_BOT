# QUICK_START.md

## 如何启动项目

```bash
cd C:\AI_WORKSPACE\m33-lotto-bot
python -m src.app.main
```

## 项目核心入口

- **src/app/main.py**

## 主要模块说明

- **Bet Module**: 下注逻辑
- **Result Module**: 开奖抓取
- **Report Module**: 报表
- **Settlement Module**: 结算（核心）

## 数据库位置

- **data/m33_lotto.db**

## 最重要规则（必须强调）

❗不允许算错钱  
❗不允许漏单  
❗不允许重复结算

## 修改代码规则

- 不允许只改一部分 → 必须给完整文件
- 不破坏现有功能
- 所有改动可回滚