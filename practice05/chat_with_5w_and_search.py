# -*- coding: utf-8 -*-
"""
基于5W1H方法论的智能搜索对话系统
支持深入分析和全面解答用户问题
"""

import os
import json
import http.client

class FiveWAnalyzer:
    """5W1H分析器"""
    
    def __init__(self):
        self.questions = {
            'what': '发生了什么？',
            'why': '为什么会发生？',
            'when': '什么时候发生的？',
            'where': '在哪里发生的？',
            'who': '谁参与了？',
            'how': '是如何发生的？'
        }
    
    def analyze(self, user_input):
        """分析用户问题，生成5W1H追问"""
        analysis_result = {}
        
        for key, question in self.questions.items():
            if key in user_input.lower() or self._detect_intent(user_input, key):
                analysis_result[key] = True
        
        return analysis_result
    
    def _detect_intent(self, text, intent):
        """检测用户意图"""
        intent_keywords = {
            'what': ['什么', '是什么', '发生', '内容', '情况'],
            'why': ['为什么', '原因', '理由', '为何', '起因'],
            'when': ['什么时候', '时间', '何时', '日期', '开始'],
            'where': ['哪里', '地点', '位置', '在', '于'],
            'who': ['谁', '谁的', '哪个人', '哪个', '何人'],
            'how': ['如何', '怎样', '怎么', '方式', '方法']
        }
        
        return any(keyword in text for keyword in intent_keywords.get(intent, []))

def load_env():
    """加载环境变量"""
    env = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
    return env

def execute_search(query):
    """执行搜索"""
    env = load_env()
    search_url = env.get('SEARCH_API_URL', 'http://localhost:8080/search')
    
    use_ssl = search_url.startswith('https://')
    url = search_url.replace('https://', '').replace('http://', '')
    host = url.split('/')[0]
    path = '/' + '/'.join(url.split('/')[1:]) if '/' in url else '/'
    
    try:
        conn = http.client.HTTPSConnection(host) if use_ssl else http.client.HTTPConnection(host)
        conn.request('GET', f'{path}?q={query}')
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        conn.close()
        
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"results": [{"title": "搜索结果", "content": data}]}
    except Exception as e:
        return {"results": [{"title": "搜索失败", "content": str(e)}]}

def call_ai_service(prompt, stream=True):
    """调用AI服务"""
    env = load_env()
    base_url = env.get('BASE_URL', 'http://localhost:8000/v1')
    model = env.get('MODEL', 'default')
    api_key = env.get('API_KEY', '')
    
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
            data = response.read().decode('utf-8')
            result = json.loads(data)
            return result['choices'][0]['text'] if 'choices' in result else data
    except Exception as e:
        return f"调用失败: {e}"
    finally:
        conn.close()

def process_with_5w(user_input):
    """使用5W1H方法处理用户问题"""
    print(f"用户问题: {user_input}")
    
    # 分析问题类型
    analyzer = FiveWAnalyzer()
    analysis = analyzer.analyze(user_input)
    print(f"问题分析: {analysis}")
    
    # 判断是否需要搜索
    needs_search = any([
        '最新' in user_input, '现在' in user_input, '今天' in user_input,
        '新闻' in user_input, '发生' in user_input
    ])
    
    search_results = ""
    if needs_search:
        print("[状态] 正在搜索相关信息...")
        results = execute_search(user_input)
        if results.get('results'):
            search_results = "\n【搜索参考】\n"
            for i, result in enumerate(results['results'][:3], 1):
                search_results += f"{i}. {result.get('title', '')}\n   {result.get('content', '')[:80]}...\n"
    
    # 构建prompt
    prompt = f"""
请使用5W1H方法分析并回答以下问题：

用户问题：{user_input}

{search_results}

请按照以下结构回答：
- 什么(What)：
- 为什么(Why)：
- 何时(When)：
- 何地(Where)：
- 何人(Who)：
- 如何(How)：

如果某些方面不适用，请注明"不适用"或"未知"。
"""
    
    print("助手: ", end='', flush=True)
    return call_ai_service(prompt, stream=True)

if __name__ == '__main__':
    print("=== 5W1H智能分析系统 ===")
    print("支持问题分析和智能搜索")
    print("输入 'exit' 退出")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n你: ")
            if user_input.lower() == 'exit':
                print("再见！")
                break
            
            process_with_5w(user_input)
            
        except KeyboardInterrupt:
            print("\n再见！")
            break