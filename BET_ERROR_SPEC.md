# Bet 错误规范

## 核心要求
- **总原则**：一行错，整批失败。
- **用户提示格式**：<原输入行> Invalid Input
- **上下文未进入大区时可提示**：Please select region group first

## 错误场景
- 空输入
- 无法识别 bet type / amount
- 金额格式错误
- 上下文缺失
- MN / MT 缺少区域
- MB 中误写其他区域
- 区域代码不合法
- 区域不属于当前大区
- 号码不是纯数字
- 号码长度不合法
- DD 非 2c
- XC 非 3c / 4c
- DA 非 2c 
- DA 数量不足
- DA 跨区域
- DX 在 MB 中使用
- DX 区域数量不足
- DX 号码数量不足
- DX 非 2c
- DX 结构混乱
- 多余 token / 无法解释 token

## 内部日志
- 对用户显示简洁
- 内部日志保留详细错误原因
