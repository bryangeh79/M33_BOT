# 代码结构说明

## Python 项目目录用途

### src/bot
- 存放 Telegram 相关的逻辑，包括主菜单、消息处理等。

### src/modules/bet
- 存放与投注模块相关的实现，包含处理投注逻辑的各类文件。

### src/config
- 存放配置文件，包括环境变量和其他静态配置。

### src/data
- 存放与数据相关的实现，包括数据库连接及初始数据表的定义。

### src/core
- 存放核心逻辑代码，可能涉及对外部接口的处理或高级的业务逻辑。

### src/modules
- 存放其他功能模块，比如 result, info, admin 等。

## Bet 模块中的细分

### handlers
- 处理与用户交互的逻辑，接收并处理用户输入。

### services
- 提供业务逻辑层,处理各种计算与流程。

### parsers
- 解析用户输入与消息格式。

### validators
- 校验用户输入的有效性。

### calculators
- 计算相关的金额等数据。

### repositories
- 提供数据存取接口，负责与数据库的交互。

### models
- 定义数据模型和结构。

### formatters
- 格式化输出，包括成功或错误消息的展示。

### constants
- 存放常量值。

### types
- 定义各种类型与数据结构，使用 dataclass 或 pydantic model.