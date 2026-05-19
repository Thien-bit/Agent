# -*- coding: utf-8 -*-
"""
带搜索功能的对话系统
支持在回答前进行网络搜索，获取最新信息
"""

import os
import json
import http.client
import urllib.parse

def load_env_config():
    """加载环境配置"""
    config = {}
    env_path = os.path.join(os.getcwd(), '.env')
    
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config

def perform_web_search(query):
    """执行网络搜索"""
    config = load_env_config()
    search_api_url = config.get('SEARCH_API_URL', 'http://localhost:8080/search')
    
    # 解析搜索API地址
    use_ssl = False
    if search_api_url.startswith('http://'):
        url_part = search_api_url[7:]
    elif search_api_url.startswith('https://'):
        url_part = search_api_url[8:]
        use_ssl = True
    else:
        url_part = search_api_url
    
    host = url_part.split('/')[0]
    path = '/' + '/'.join(url_part.split('/')[1:]) if '/' in url_part else '/'
    
    encoded_query = urllib.parse.quote(query)
    
    try:
        if use_ssl:
            conn = http.client.HTTPSConnection(host, timeout=10)
        else:
            conn = http.client.HTTPConnection(host, timeout=10)
        
        conn.request('GET', f'{path}?q={encoded_query}')
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        
        try:
            result = json.loads(data)
            return result.get('results', [])[:5]  # 返回前5条结果
        except json.JSONDecodeError:
            return [{"title": "搜索结果", "content": data}]
        
    except Exception as e:
        print(f"搜索失败: {e}")
        return []
    finally:
        conn.close()

def format_search_results(results):
    """格式化搜索结果"""
    if not results:
        return "未找到相关搜索结果"
    
    formatted = "【搜索结果参考】\n"
    for i, result in enumerate(results, 1):
        title = result.get('title', '')
        content = result.get('content', '')
        url = result.get('url', '')
        
        formatted += f"{i}. {title}\n"
        if content:
            formatted += f"   {content[:100]}...\n"
        if url:
            formatted += f"   来源: {url}\n"
        formatted += "\n"
    
    return formatted

def send_to_llm(prompt, stream=True):
    """发送请求到LLM"""
    config = load_env_config()
    base_url = config.get('BASE_URL', 'http://localhost:8000/v1')
    model = config.get('MODEL', 'default')
    api_key = config.get('API_KEY', '')
    
    # 解析URL
    use_ssl = False
    if base_url.startswith('http://'):
        url_part = base_url[7:]
    elif base_url.startswith('https://'):
        url_part = base_url[8:]
        use_ssl = True
    else:
        url_part = base_url
    
    host = url_part.split('/')[0]
    path = '/' + '/'.join(url_part.split('/')[1:]) if '/' in url_part else '/'
    
    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 800,
        "stream": stream
    }
    
    try:
        if use_ssl:
            conn = http.client.HTTPSConnection(host, timeout=30)
        else:
            conn = http.client.HTTPConnection(host, timeout=30)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        conn.request('POST', f'{path}/completions', 
                    body=json.dumps(data), headers=headers)
        
        response = conn.getresponse()
        
        if stream:
            full_text = ""
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    chunk = line[6:]
                    if chunk != '[DONE]':
                        try:
                            parsed = json.loads(chunk)
                            if 'choices' in parsed:
                                text = parsed['choices'][0].get('text', '')
                                print(text, end='', flush=True)
                                full_text += text
                        except json.JSONDecodeError:
                            pass
            print()
            return full_text
        else:
            response_data = response.read().decode('utf-8')
            result = json.loads(response_data)
            return result['choices'][0]['text'] if 'choices' in result else response_data
    
    except Exception as e:
        return f"LLM调用失败: {e}"
    finally:
        conn.close()

def should_search(user_input):
    """判断是否需要进行搜索"""
    search_triggers = [
        '最新', '现在', '今天', '最近', '最新消息', '最新动态',
        '新闻', '天气', '股价', '比赛结果', '比分',
        '谁是', '什么是', '有哪些', '如何', '怎样'
    ]
    
    return any(trigger in user_input for trigger in search_triggers)

def chat_with_search(user_input):
    """带搜索功能的对话"""
    print(f"用户问题: {user_input}")
    
    # 判断是否需要搜索
    if should_search(user_input):
        print("[状态] 需要进行网络搜索...")
        search_results = perform_web_search(user_input)
        
        if search_results:
            search_text = format_search_results(search_results)
            print(search_text)
            
            # 构建包含搜索结果的prompt
            prompt = f"""
根据以下搜索结果，回答用户的问题。搜索结果仅作为参考，你可以结合自己的知识进行回答。

{search_text}

用户问题：{user_input}
"""
        else:
            prompt = f"""回答用户问题：{user_input}"""
    else:
        prompt = f"""回答用户问题：{user_input}"""
    
    print("[状态] 正在生成回答...")
    return send_to_llm(prompt, stream=True)

if __name__ == '__main__':
    print("=== 智能搜索对话系统 ===")
    print("支持自动搜索的AI对话助手")
    print("输入 'exit' 退出")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n你: ")
            if user_input.lower() == 'exit':
                print("再见！")
                break
            
            chat_with_search(user_input)
            
        except KeyboardInterrupt:
            print("\n再见！")
            break