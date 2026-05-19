# 技能增强对话系统

基于技能调用的智能对话框架，支持动态加载和调用各种技能。

## 功能特性

- **技能注册**：支持动态注册各类技能
- **智能调度**：自动识别用户意图并调用相应技能
- **流程管理**：支持技能链式调用
- **结果整合**：自动整合技能执行结果

## 技能列表

| 技能名称 | 功能描述 |
|---------|---------|
| search_web | 网络搜索 |
| calculator | 数学计算 |
| weather | 获取天气 |
| summary | 文本摘要 |

## 使用方法

```bash
# 启动主程序
python chat_with_skills.py

# 运行测试
python test_chat.py
python test_skills.py
```

## 配置文件

在项目目录创建 `.env` 文件：

```env
BASE_URL=http://localhost:8000/v1
MODEL=your-model
API_KEY=your-api-key
```

## 扩展技能

在 `chat_with_skills.py` 中添加新技能：

```python
def new_skill(params):
    """新技能实现"""
    return "技能执行结果"

skills.register("new_skill", new_skill)
```