# Phase 1.3 Checkpoint: Result Menu ReplyKeyboard Migration

## 任务理解
将 Result 菜单从 InlineKeyboard 迁移到 ReplyKeyboard，保留现有开奖结果查询功能不变。

## 改了什么
1. **新增状态**：
   - `UserState.RESULT_DATE`：选择结果日期
   - `UserState.RESULT_REGION`：选择结果地区

2. **新增 ReplyKeyboard 构建函数**：
   - `_build_result_date_kb()`：日期选择键盘
   - `_build_result_region_kb()`：地区选择键盘

3. **修改 main_menu_handler**：
   - 点击 "Result" 时切换到 `RESULT_DATE` 状态并显示 ReplyKeyboard

4. **新增 text_router 分支**：
   - `RESULT_DATE` 状态：处理日期选择（Today/具体日期/返回）
   - `RESULT_REGION` 状态：处理地区选择（MN/MT/MB/返回）

5. **保留旧 InlineKeyboard handlers** 作为 fallback

## 风险与影响
- **影响面**：Result 菜单交互逻辑
- **限制**：仅迁移交互层，不动业务逻辑
- **风险**：低风险，新增状态和键盘，保留旧 fallback

## 下一步
1. 测试 ReplyKeyboard 交互流程
2. 验证结果查询功能正常
3. 确认旧 InlineKeyboard fallback 有效
