# -*- coding: utf-8 -*-
"""
链式调用对话系统
支持多步骤顺序执行
"""

import os
import json
import http.client

class ChainedCallManager:
    """链式调用管理器"""
    
    def __init__(self):
        self.steps = []
        self.results = {}
    
    def add_step(self, name, action, dependencies=None):
        """添加步骤"""
        self.steps.append({
            "name": name,
            "action": action,
            "dependencies": dependencies or []
        })
    
    def execute(self, context):
        """执行链式调用"""
        print("=== 开始链式执行 ===")
        
        for step in self.steps:
            # 检查依赖
            deps_ok = all(dep in self.results for dep in step['dependencies'])
            if not deps_ok:
                print(f"[跳过] {step['name']} - 依赖未满足")
                continue
            
            print(f"\n[步骤] {step['name']}")
            
            try:
                result = step['action'](context, self.results)
                self.results[step['name']] = result
                print(f"[结果] {result[:50]}..." if len(str(result)) > 50 else f"[结果] {result}")
            except Exception as e:
                print(f"[错误] {step['name']}: {str(e)}")
                self.results[step['name']] = None
        
        return self.results

def load_config():
    """加载配置"""
    config = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    return config

def call_llm(prompt, stream=True):
    """调用LLM服务"""
    config = load_config()
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

def search_action(context, results):
    """搜索动作"""
    query = context.get('query', '')
    return f"搜索结果: 关于'{query}'的信息"

def analyze_action(context, results):
    """分析动作"""
    search_result = results.get('search')
    return f"分析完成: 基于搜索结果进行了深度分析"

def summarize_action(context, results):
    """总结动作"""
    search_result = results.get('search')
    analyze_result = results.get('analyze')
    return f"总结报告: 综合搜索和分析结果生成报告"

def save_to_file(filename, content):
    """保存到文件"""
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def process_with_chain(user_input):
    """使用链式调用处理请求"""
    print(f"用户请求: {user_input}")
    
    # 创建链式调用管理器
    manager = ChainedCallManager()
    
    # 定义步骤
    manager.add_step("search", search_action)
    manager.add_step("analyze", analyze_action, dependencies=["search"])
    manager.add_step("summarize", summarize_action, dependencies=["search", "analyze"])
    
    # 执行链式调用
    context = {"query": user_input}
    results = manager.execute(context)
    
    # 生成最终回答
    final_result = results.get('summarize', "处理完成")
    
    print("\n=== 最终回答 ===")
    call_llm(f"根据以下结果，用自然语言回答用户问题：\n用户问题：{user_input}\n处理结果：{final_result}", stream=True)
    
    # 保存结果到文件
    save_to_file('title.txt', final_result)
    print(f"\n[状态] 结果已保存到 output/title.txt")

if __name__ == '__main__':
    print("=== 链式调用对话系统 ===")
    print("支持多步骤顺序执行")
    print("输入 'exit' 退出")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n你: ")
            if user_input.lower() == 'exit':
                print("再见！")
                break
            
            process_with_chain(user_input)
            
        except KeyboardInterrupt:
            print("\n再见！")
            break