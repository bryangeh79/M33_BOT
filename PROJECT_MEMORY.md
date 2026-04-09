# PROJECT_MEMORY.md

## 项目路径
C:\AI_WORKSPACE\m33-lotto-bot

## 当前阶段
Phase: Settlement System + Report System 已完成（v1.0）

## 系统架构
- 语言：Python
- 框架：python-telegram-bot
- 数据库：SQLite（data/m33_lotto.db）
- 入口：src/app/main.py

--------------------------------------------------

## 已完成模块

1️⃣ **Bet Module**（稳定运行）  
路径：src/modules/bet/  
功能：  
- 下注解析（parser）  
- 验证（validator）  
- 计算金额（calculator）  
- 成功 / 错误 formatter  
- ticket 系统  
- delete_ticket 已支持

--------------------------------------------------

2️⃣ **Result Module**（稳定运行）  
路径：src/modules/result/  
功能：  
- 抓取 xosodaiphat  
- MN / MT / MB 支持  
- HTML parsing  
- DB 存储  
- 查询缓存  
- Telegram 展示  
- Refresh 机制

--------------------------------------------------

3️⃣ **Settlement Module**（已完成）  
路径：src/modules/settlement/  
功能：  
- 按区域结算（MN / MT / MB）  
- 支持：  
 - LO  
 - XC  
 - DX  
- payout_calculator 已稳定  
- settlement_engine 已完成  
- settlement_results 已写入数据库  
- 防重复结算已实现

--------------------------------------------------

4️⃣ **Report Module**（已完成 v1.0）  
路径：src/modules/report/

已完成：  
✅ Transaction Report  
✅ Number Detail Report  
✅ Settlement Report（核心）

Settlement Report 包含：  
- MN / MT / MB 投注总数  
- MN / MT / MB 中奖金额  
- 总结算（gross_total）  
- 代理佣金（暂时固定 0）  
- 总中奖金额  
- 净结果（net_result）  
- 中奖明细（payout > 0）

--------------------------------------------------

5️⃣ **Report 输出能力**

✅ Telegram 文本输出  
路径：  
- settlement_report_formatter.py

✅ HTML 导出  
路径：  
- settlement_report_html_exporter.py

功能：  
- Export HTML 按钮  
- 自动生成 HTML 文件  
- 可直接下载

--------------------------------------------------

6️⃣ **Bot UI**（已接通）

Report 流程：  
Main Menu  
→ Report  
→ Settlement Report  
→ Select Date  
→ 输出报表  
→ Export HTML

相关文件：  
- src/app/main.py（已接入 callback）  
- InlineKeyboard UI 已完成

--------------------------------------------------

## 当前系统状态

系统已具备：

✔ 可下注  
✔ 可开奖  
✔ 可结算  
✔ 可出报表  
✔ 可导出 HTML

👉 属于「可运营版本 v1.0」

--------------------------------------------------

## 当前未完成

🚧 Over Limit Report（开发中）  
目标：  
- 按号码聚合下注金额  
- 判断是否超过 limit  
- 输出超限数据（风控核心）

🚧 Agent Commission（未接）  
- Admin 设置佣金 %  
- 自动进入 Settlement Report

--------------------------------------------------

## 下一阶段开发

Phase v1.1：

1. Over Limit Report（优先）  
2. Agent Commission System  
3. Report UI 优化（更专业）  
4. 风控系统（限额 + 报警）

--------------------------------------------------

## 重要要求

你必须记住：

- 所有开发在 C:\AI_WORKSPACE 下进行  
- 不允许再使用旧路径 C:\M33 Lotto Bot  
- 所有新模块必须符合现有架构（modules 分层）  
- 所有修改必须给“完整文件”，不能局部修改