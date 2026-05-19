# 链式调用对话系统

支持多轮链式调用的智能对话框架。

## 功能特性

- **链式处理**：支持多个技能的顺序调用
- **上下文传递**：自动传递中间结果
- **流程控制**：支持条件分支和循环
- **结果汇总**：自动汇总所有步骤结果

## 使用方法

```bash
# 启动主程序
python chat_with_chained_calls.py

# 运行测试
python test_chained_calls.py
```

## 配置文件

在项目目录创建 `.env` 文件：

```env
BASE_URL=http://localhost:8000/v1
MODEL=your-model
API_KEY=your-api-key
```

## 输出目录

- `output/` - 存储生成的输出文件