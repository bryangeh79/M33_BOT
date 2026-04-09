# Bug 3 翻译问题修复计划

## 问题描述
1. 用户选择越南语，但导出的HTML报告是英语
2. 某些菜单和系统文字可能没有正确翻译

## 发现的问题

### 1. HTML导出硬编码英文 🔴
**文件**:
- `src/modules/report/formatters/report_html_formatter.py`
- `src/modules/report/formatters/settlement_report_html_exporter.py`
- `src/modules/report/formatters/over_limit_report_html_exporter.py`
- `src/modules/report/formatters/transaction_report_formatter_html.py`

**问题**:
- `<html lang="en">` 硬编码
- 标题、标签硬编码为英文
- 没有使用用户语言设置

### 2. 翻译覆盖检查 ✅
**结果**: 越南语翻译文件完整，没有缺失键

### 3. t()函数使用检查 ⚠️
**结果**: 大部分文件正确，少数文件可能有问题

## 修复步骤

### 阶段1: 添加HTML相关翻译键
**文件**: `src/i18n/en.py`, `vi.py`, `zh.py`
**内容**:
```python
# HTML报告翻译键
"HTML_TITLE_SETTLEMENT": "Settlement Report",
"HTML_TITLE_TRANSACTION": "Transaction Report",
"HTML_TITLE_NUMBER_DETAIL": "Number Detail Report",
"HTML_TITLE_OVER_LIMIT": "Over Limit Report",
"HTML_LABEL_DATE": "Date",
"HTML_LABEL_TOTAL": "Total",
"HTML_LABEL_REGION": "Region",
"HTML_LABEL_TICKET_NO": "Ticket No",
"HTML_LABEL_BET_TYPE": "Bet Type",
"HTML_LABEL_NUMBERS": "Numbers",
"HTML_LABEL_UNIT": "Unit",
"HTML_LABEL_AMOUNT": "Amount",
"HTML_LABEL_GENERATED_AT": "Generated at",
"HTML_TOTAL_SETTLEMENT": "Total Settlement",
"HTML_WINNING_DETAILS": "Winning Details",
"HTML_NO_DATA": "No data",
"HTML_TOTAL_BET": "Total Bet",
"HTML_TOTAL_PAYOUT": "Total Payout",
"HTML_COMMISSION": "Commission",
"HTML_SETTLEMENT": "Settlement",
"HTML_WINNER_COUNT": "Winner Count",
```

### 阶段2: 修改HTML导出函数
**文件1**: `report_html_formatter.py`
**修改**:
1. 添加`lang`参数到函数
2. 使用`t()`函数获取翻译
3. 更新`<html lang="{lang}">`

**文件2**: `settlement_report_html_exporter.py`
**修改**:
1. 添加`lang`参数
2. 替换硬编码标题和标签

**文件3**: `over_limit_report_html_exporter.py`
**文件4**: `transaction_report_formatter_html.py`

### 阶段3: 更新调用代码
**文件**: `src/app/main.py`
**修改位置**:
- 第1332行: `build_transaction_report_html(report_data)`
- 第1335行: `build_number_detail_report_html(report_data)`
- 第1339行: `export_settlement_report_html(report_data)`
- 第1342行: `export_over_limit_report_html(report_data)`

**改为**:
```python
user_lang = _get_user_lang(user_id)
html = build_transaction_report_html(report_data, lang=user_lang)
```

### 阶段4: 检查其他硬编码文本
**文件**:
- `src/modules/bet/validators/bet_region_validator.py`
- `src/modules/result/constants/result_constants.py`
- `src/modules/schedule/services/region_schedule_service.py`

## 测试计划

### 测试1: HTML导出语言测试
1. 设置用户语言为越南语
2. 导出结算报告
3. 验证HTML语言属性和内容

### 测试2: 系统文字翻译测试
1. 切换不同语言
2. 检查菜单、按钮、提示信息
3. 验证所有界面元素正确翻译

### 测试3: 回退机制测试
1. 测试缺失翻译键的情况
2. 验证回退到英文正常工作

## 时间估算
- **阶段1**: 30分钟
- **阶段2**: 2小时
- **阶段3**: 30分钟
- **阶段4**: 1小时
- **测试**: 1小时

**总计**: 约5小时

## 风险
1. 可能遗漏某些硬编码文本
2. 翻译键命名冲突
3. 性能影响（多次调用t()函数）

## 成功标准
1. ✅ HTML报告使用用户选择的语言
2. ✅ 所有用户界面元素正确翻译
3. ✅ 回退机制正常工作
4. ✅ 性能无明显下降

## 优先级
**高优先级**: 修复HTML导出问题（影响用户体验）
**中优先级**: 检查其他硬编码文本
**低优先级**: 优化翻译性能