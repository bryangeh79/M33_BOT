# PROJECT_STRUCTURE.md

## 项目目录结构
C:\AI_WORKSPACE\m33-lotto-bot

```plaintext
tree C:\AI_WORKSPACE\m33-lotto-bot
```

## 目录和文件作用

- **src/**: 源代码目录  
  - **app/**: 应用程序入口和核心逻辑  
    - **main.py**: 主入口文件  
  - **modules/**: 功能模块  
    - **bet/**: 下注相关逻辑  
    - **result/**: 结果处理逻辑  
    - **settlement/**: 结算逻辑  
    - **report/**: 报表生成逻辑  
    - **admin/**: 管理功能模块  
- **data/**: 数据存储  
  - **m33_lotto.db**: SQLite 数据库文件