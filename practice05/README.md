# 智能对话增强系统

提供多种增强功能的AI对话工具集合。

## 功能模块

### 1. 5W分析搜索器 (chat_with_5w_and_search.py)
基于5W1H方法论的智能搜索分析工具，帮助用户深入分析问题。

### 2. AnythingLLM集成 (chat_with_anythingllm.py)
与AnythingLLM本地知识库系统集成，支持私有知识库问答。

### 3. 对话总结 (chat_with_summary.py)
自动总结对话历史，支持长对话管理。

## 环境配置

在项目根目录创建 `.env` 文件：

```env
# LLM配置
BASE_URL=http://localhost:8000/v1
MODEL=your-model-name
API_KEY=your-api-key

# 搜索配置
SEARCH_API_URL=http://localhost:8080/search

# AnythingLLM配置
ANYTHINGLLM_URL=http://localhost:3001
```

## 使用方法

```bash
# 启动5W分析搜索
python chat_with_5w_and_search.py

# 启动AnythingLLM对话
python chat_with_anythingllm.py

# 启动对话总结
python chat_with_summary.py
```

## 技术特点

- 模块化设计，易于扩展
- 支持多种LLM服务
- 完整的错误处理机制
- 流式输出支持