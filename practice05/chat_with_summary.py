# -*- coding: utf-8 -*-
"""
智能对话总结系统
自动管理和总结对话历史
"""

import os
import json
import http.client

class ChatSummaryManager:
    """对话总结管理器"""
    
    def __init__(self):
        self.dialog_history = []
        self.current_summary = ""
        self.max_history = 8
        self.summary_interval = 4
    
    def add_dialog(self, user_msg, bot_msg):
        """添加对话记录"""
        self.dialog_history.append({
            "user": user_msg,
            "bot": bot_msg
        })
        
        if len(self.dialog_history) > self.max_history:
            self.dialog_history = self.dialog_history[-self.max_history:]
        
        if len(self.dialog_history) % self.summary_interval == 0:
            self.create_summary()
    
    def create_summary(self):
        """创建对话总结"""
        print("[系统] 正在生成对话总结...")
        
        history_text = "\n".join([f"用户: {d['user']}\n助手: {d['bot']}" for d in self.dialog_history])
        
        prompt = f"""
请总结以下对话内容：

{history_text}

总结要求：
1. 简洁明了
2. 不超过80字
3. 中文输出
"""
        
        summary = self.invoke_llm(prompt, stream=False)
        self.current_summary = summary
        print(f"【对话摘要】{summary}")
    
    def get_dialog_context(self):
        """获取对话上下文"""
        context = ""
        if self.current_summary:
            context = f"【历史对话摘要】{self.current_summary}\n\n"
        
        recent_dialogs = self.dialog_history[-2:] if len(self.dialog_history) > 2 else self.dialog_history
        for d in recent_dialogs:
            context += f"用户: {d['user']}\n助手: {d['bot']}\n"
        
        return context
    
    def invoke_llm(self, prompt, stream=True):
        """调用LLM服务"""
        config = self.load_configuration()
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
            "max_tokens": 500,
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
            return f"服务调用失败: {e}"
        finally:
            conn.close()
    
    def load_configuration(self):
        """加载配置"""
        config = {}
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        return config

def start_chat():
    """启动对话"""
    print("=== 智能对话总结系统 ===")
    print("支持自动总结对话历史")
    print("输入 'exit' 退出")
    print("=" * 50)
    
    manager = ChatSummaryManager()
    
    while True:
        try:
            user_input = input("\n你: ")
            if user_input.lower() == 'exit':
                print("再见！")
                break
            
            context = manager.get_dialog_context()
            
            prompt = f"""
{context}
用户: {user_input}
助手:
"""
            
            print("助手: ", end='', flush=True)
            response = manager.invoke_llm(prompt, stream=True)
            
            manager.add_dialog(user_input, response)
            
        except KeyboardInterrupt:
            print("\n再见！")
            break

if __name__ == '__main__':
    start_chat()