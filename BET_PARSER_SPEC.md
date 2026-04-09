# Bet Parser 规范

## 处理总流程
1. 收到整条消息
2. 按行拆开
3. 逐行预检查
   - 只要有一行错 → 全部失败
4. 全部都对 → 逐行计算
5. 生成流水号
6. 保存 batch / items / details
7. 返回成功回执

## 模块分工
- **Context Resolver**
- **Line Splitter**
- **Bet Type Detector**
- **Structure Parser**
- **Validator**
- **Calculator**
- **Response Builder**

## 各玩法解析规则
- LO
- DD
- XC
- DA
- DX

## 错误检查顺序
1. 行是否为空
2. 最后 token 是否可识别 bet_type + amount
3. 按 bet_type 解析结构
4. 检查区域合法性
5. 检查号码合法性
6. 检查玩法限制
7. 检查上下文限制

通过后才计算 total
