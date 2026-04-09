# M33 Lotto Bot 菜单行为规范

## 1. Bet

### 菜单名称：
Bet

### 用途：
用于输入投注

### 可访问角色：
User, Admin, Super Admin

### 点击后行为：
点击 Bet 后显示地区选择按钮：
- MN
- MT
- MB

### 输入要求：
用户选择地区后，进入对应地区的投注输入流程。

### 输出内容：
根据选择的地区，进入相应的投注页面。

### 异常情况提示：
如果用户未完成输入，应提示：
"请输入完整的投注信息。"

### 后续扩展点：
允许用户自定义投注站。

## 2. Report

### 子菜单：
- Today Settlement
- Transactions History
- Summary Report

### Today Settlement
- **点击后显示什么**：显示今天的结算情况。
- **是否按地区显示**：是，按地区分组。
- **输出格式建议**：表格形式，显示每个地区的结算结果。

### Transactions History
- **点击后先显示最近 7 天日期按钮**：是，用户选择日期后显示当天所有输入单。
- **输出格式建议**：日期 + 投注信息的列表。

### Summary Report
- **点击后先显示最近 7 天日期按钮**：是，用户选择日期后显示当天号码汇总。
- **输出格式建议**：按号码显示的表格。

### 可访问角色：
User, Admin, Super Admin

### 提示语：
如果当天没有数据，提示：
"今天没有任何投注记录。"

## 3. Result

### 点击后默认显示什么：
显示最新的开奖结果。

### 是否建议增加地区按钮：
是，允许用户选择 MN / MT / MB。

### 输出格式建议：
列表展示最近的开奖信息。

### 提示：
如果开奖结果尚未更新，提示：
"开奖结果正在加载，请稍后再试。"

## 4. Other Day Input

### 哪些角色可使用：
User, Admin, Super Admin

### 点击后流程：
先选日期，再选地区，进入补录投注流程。

### 提示：
如果用户选择了无效日期，提示：
"请选择有效的日期。"

## 5. Admin

### 子菜单：
- Set Admin Roles
- Bonus Payout
- Bet Limit
- Agent Comm
- Over Limit Statement

### 每个子菜单的用途：
- **Set Admin Roles**：设置群里管理人权限。
- **Bonus Payout**：奖金派发管理。
- **Bet Limit**：投注限额设置。
- **Agent Comm**：代理佣金设置。
- **Over Limit Statement**：超限报表 / 超限说明。

### 可访问角色：
Admin, Super Admin

### 提示语：
非管理员点击时提示：
"您没有权限访问此功能。"

### 占位功能：
- 当前所有功能暂时占位，后续进行开发。

## 6. Info

### 点击后展示的内容：
基础公司信息与介绍。

### 包含栏目建议：
- 公司介绍
- 规则说明
- 联系方式
- 公告

### 输出格式建议：
文本和链接结合的展示形式。

## A. 角色权限矩阵
| 角色        | 可访问菜单               |
|-------------|--------------------------|
| User        | Bet, Report, Result, Info |
| Admin       | Bet, Report, Result, Info, Admin |
| Super Admin | Bet, Report, Result, Info, Admin |

## B. Phase 1 开发范围建议

**当前 Phase 1 只先实现以下菜单行为**：
- 主菜单显示
- Bet → 地区选择
- Result → 基础结果显示
- Info → 公司介绍
- Admin → 权限拦截占位