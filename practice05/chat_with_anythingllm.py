# -*- coding: utf-8 -*-
"""
与AnythingLLM集成的对话系统
支持本地知识库问答
"""

import os
import json
import http.client

def get_config():
    """获取配置"""
    config = {}
    env_file = '.env'
    
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config

def query_anythingllm(message, collection_name=None):
    """查询AnythingLLM"""
    config = get_config()
    base_url = config.get('ANYTHINGLLM_URL', 'http://localhost:3001')
    
    use_ssl = base_url.startswith('https://')
    url = base_url.replace('https://', '').replace('http://', '')
    host = url.split('/')[0]
    path = '/' + '/'.join(url.split('/')[1:]) if '/' in url else '/'
    
    data = {
        "message": message,
        "collectionName": collection_name or "default",
        "stream": False
    }
    
    try:
        conn = http.client.HTTPSConnection(host, timeout=30) if use_ssl else http.client.HTTPConnection(host, timeout=30)
        headers = {'Content-Type': 'application/json'}
        
        api_path = f"{path}/api/v1/chat" if path else "/api/v1/chat"
        conn.request('POST', api_path, body=json.dumps(data), headers=headers)
        
        response = conn.getresponse()
        response_data = response.read().decode('utf-8')
        
        try:
            result = json.loads(response_data)
            return result.get('text', result.get('response', str(result)))
        except json.JSONDecodeError:
            return response_data
    except Exception as e:
        return f"AnythingLLM查询失败: {str(e)}"
    finally:
        conn.close()

def call_main_llm(prompt, stream=True):
    """调用主LLM服务"""
    config = get_config()
    base_url = config.get('BASE_URL', 'http://localhost:8000/v1')
    model = config.get('MODEL', 'default')
    api_key = config.get('API_KEY', '')
    
    use_ssl = base_url.startswith('https://')
    url = base_url.replace('https://', '').replace('http://', '')
    host = url.split('/')[0]
    path = '/' + '/'.join(url.split('/')[1:]) if '/' in url else '/'
    
    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 800,
        "stream": stream
    }
    
    try:
        conn = http.client.HTTPSConnection(host, timeout=30) if use_ssl else http.client.HTTPConnection(host, timeout=30)
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        conn.request('POST', f'{path}/completions', body=json.dumps(data), headers=headers)
        
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

def hybrid_query(user_input):
    """混合查询：先查知识库，再用LLM总结"""
    print(f"用户问题: {user_input}")
    
    # 第一步：查询知识库
    print("[状态] 正在查询本地知识库...")
    kb_result = query_anythingllm(user_input)
    print(f"知识库结果: {kb_result[:100]}..." if len(kb_result) > 100 else f"知识库结果: {kb_result}")
    
    # 第二步：用LLM总结回答
    prompt = f"""
请根据以下知识库内容回答用户问题：

知识库信息：
{kb_result}

用户问题：{user_input}

请用自然、友好的语言回答，如果知识库内容不足以回答问题，请结合你的知识进行回答。
"""
    
    print("\n助手: ", end='', flush=True)
    return call_main_llm(prompt, stream=True)

if __name__ == '__main__':
    print("=== AnythingLLM集成对话系统 ===")
    print("支持本地知识库查询")
    print("输入 'exit' 退出")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n你: ")
            if user_input.lower() == 'exit':
                print("再见！")
                break
            
            hybrid_query(user_input)
            
        except KeyboardInterrupt:
            print("\n再见！")
            break