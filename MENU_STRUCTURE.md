# M33 Lotto Bot 主菜单结构

## Main Menu

1. **Bet**  
   **用途**：用于输入投注
   - 点击后出现地区选择：
     - MN
     - MT
     - MB  
   **说明**：用户选择地区后，进入对应地区的投注输入流程。

2. **Report**  
   **用途**：查看报表与历史记录
   - **Today Settlement**  
     **用途**：检查今天的结算
   - **Transactions History**  
     **用途**：查询历史输入单
     - 提供最近 7 天按钮
     - 用户点击某一天后，可查看当天所有输入的单
   - **Summary Report**  
     **用途**：查询当天总结报表与个别号码汇总
     - 提供最近 7 天按钮
     - 用户点击某一天后，可查看当天输入总结及号码汇总

3. **Result**  
   **用途**：检查开彩成绩
   - **要求**：显示开奖结果
   - 后续允许扩展历史查询 / 地区筛选

4. **Other Day Input**  
   **用途**：补录非当天投注
   - **流程**：用户先选择日期，系统再显示地区选择：
     - MN
     - MT
     - MB  
   - 用户选择地区后，进入对应日期与地区的投注输入流程

5. **Admin**  
   **用途**：管理员功能入口
   - 包含以下子菜单：
     - **Set Admin Roles**  
       **用途**：设置群里管理人权限
     - **Bonus Payout**  
       **用途**：奖金派发管理
     - **Bet Limit**  
       **用途**：投注限额设置
     - **Agent Comm**  
       **用途**：代理佣金设置
     - **Over Limit Statement**  
       **用途**：超限报表 / 超限说明
     - **要求**：只有管理员可访问
       - 非管理员点击时需要提示无权限

6. **Info**  
   **用途**：介绍公司
   - **要求**：展示公司介绍内容
   - 后续可扩展规则说明、联系方式、公告等

## 菜单树结构
```
Main Menu
├── Bet
├── Report
│   ├── Today Settlement
│   ├── Transactions History
│   └── Summary Report
├── Result
├── Other Day Input
├── Admin
│   ├── Set Admin Roles
│   ├── Bonus Payout
│   ├── Bet Limit
│   ├── Agent Comm
│   └── Over Limit Statement
└── Info
```

## 模块对应关系
- Bet → 投注输入模块
- Report → 报表模块
- Result → 开奖结果模块
- Admin → 管理员模块
- Info → 信息展示模块

## MVP 开发建议
**Phase 1 MVP 优先开发**：
- 主菜单显示
- Bet 地区选择
- Result 开奖结果查看
- Info 公司介绍