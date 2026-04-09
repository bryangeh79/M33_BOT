# M33 Lotto Bot 数据模型设计

## 1. Users

### 字段建议：
- id
- telegram_id
- username
- display_name
- role
- status
- created_at
- updated_at

### 说明：
用于存储 Telegram 用户资料与权限。

## 2. Admin Roles

### 字段建议：
- id
- user_id
- role_name
- granted_by
- granted_at

### 说明：
用于记录管理员角色分配。

## 3. Bets

### 字段建议：
- id
- user_id
- input_date
- bet_date
- region
- bet_type
- bet_number
- amount
- raw_input
- status
- created_at
- updated_at

### 说明：
用于记录投注输入内容。

## 4. Draw Results

### 字段建议：
- id
- draw_date
- region
- result_data
- source
- fetched_at
- status

### 说明：
用于记录开奖数据。

## 5. Settlements

### 字段建议：
- id
- user_id
- bet_id
- draw_result_id
- settlement_date
- win_loss_amount
- payout_amount
- settlement_status
- created_at

### 说明：
用于记录结算结果。

## 6. Transactions History

### 字段建议：
- id
- user_id
- action_type
- reference_id
- description
- created_at

### 说明：
用于记录用户操作历史与查询记录。

## 7. System Config

### 字段建议：
- id
- config_key
- config_value
- config_group
- updated_at

### 说明：
用于存储系统参数，例如限额、佣金、开奖源设置等。

## A. 实体关系说明

- **Users 与 Bets 的关系**：
  - 一对多关系，用户可以有多个投注记录。

- **Bets 与 Settlements 的关系**：
  - 一对一关系，投注对应一个结算。

- **Draw Results 与 Settlements 的关系**：
  - 一对多关系，开奖结果可以与多个结算相关。

- **Users 与 Admin Roles 的关系**：
  - 一对多关系，用户可以有多个管理员角色。

## B. MVP Phase 1 需要的最小数据模型

第一阶段先需要以下实体：
- Users
- Bets
- Draw Results
- System Config

## C. 后期扩展数据模型

未来可能增加的实体：
- Bonus Payout Records
- Agent Commission Records
- Over Limit Records
- Audit Logs
