# M33 Lotto Bot - 阶段记录 v1.1

## 项目路径：
C:\AI_WORKSPACE\m33-lotto-bot

## 当前阶段：v1.1（Admin Settings 已接入）

---------------------------------

## 系统当前已完成模块

1️⃣ **Bet Module**（稳定）  
- 支持 LO / DD / XC / DA / DX  
- parser / validator / calculator 完整  
- ticket 系统稳定  
- delete_ticket 已支持

2️⃣ **Result Module**（稳定）  
- 数据源：xosodaiphat  
- MN / MT / MB 支持  
- HTML parsing + DB 存储  
- Refresh 正常

3️⃣ **Settlement Module**（稳定）  
- settlement_engine 已完成  
- payout_calculator 已统一入口  
- Agent Commission 已接入（从 admin setting 读取）

4️⃣ **Report Module**（完成 v1.1）  
包含：

✔ Transaction Report  
✔ Number Detail Report  
✔ Settlement Report（已接 agent comm）  
✔ Over Limit Report（已接后台 limit）  
✔ HTML Export（全部支持）

---------------------------------

## 新增系统（本阶段重点）

5️⃣ **Admin System**（已完成 v1.1）

包含：

✔ Admin 权限系统（user / admin）  
✔ Set Admin（可动态添加 / 删除）  
✔ Agent Commission Setting  
 - View / Edit  
 - 已接 Settlement Report

✔ Bonus Payout Setting  
 - View / Bulk Edit（整页输入）  
 - 已存 DB（尚未 fully 接入 payout_calculator）

✔ Over Limit Setting  
 - View / Bulk Edit  
 - 已接 Over Limit Report

✔ Over Limit Action  
 - ACCEPT / REJECT  
 - 已存 DB（下一阶段接入 Bet）

---------------------------------

## 当前数据结构（关键）

1. **Bonus Payout（分区）**

MN/MT：  
- 2C: LO / DD / DA / DX  
- 3C: LO / XC  
- 4C: LO / XC

MB：  
- 2C: LO / DD / DA  
- 3C: LO / XC  
- 4C: LO / XC

⚠️ MB 不支持 DX

---------------------------------

2. **Over Limit（结构一致）**

- 与 Bonus Payout 同结构  
- 默认值已初始化  
- 已接 Report

---------------------------------

## 当前未完成（下一阶段）

🚧 1. Bonus Payout → 接入 payout_calculator  
（当前只 fallback）

🚧 2. Over Limit → 接入 Bet（拒单 / 继续）

🚧 3. Admin UI 优化（美观 / 排版）

🚧 4. Report UI 优化（结构更清晰）

---------------------------------

## 当前系统状态

✅ 可运行  
✅ 可下注  
✅ 可结算  
✅ 可报表  
✅ 可风控查看  
✅ Admin 可控核心参数

---------------------------------

## 注意事项

1. 不允许删除现有模块结构  
2. 所有新功能必须接入 Admin Settings  
3. payout / limit 不再写死，统一走 DB

---------------------------------

## 记录时间：
2026-03-18

## 状态：
READY FOR UI OPTIMIZATION + FINAL INTEGRATION