# -*- coding: utf-8 -*-
"""
带总结功能的对话系统
支持对话历史的自动总结
"""

import os
import json
import http.client

class ConversationManager:
    """对话管理器"""
    
    def __init__(self):
        self.history = []
        self.summary = ""
        self.max_history_length = 10
        self.summary_threshold = 5
    
    def add_message(self, user_msg, assistant_msg):
        """添加对话记录"""
        self.history.append({
            "user": user_msg,
            "assistant": assistant_msg
        })
        
        # 保持历史长度限制
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length:]
        
        # 判断是否需要总结
        if len(self.history) >= self.summary_threshold and len(self.history) % self.summary_threshold == 0:
            self.generate_summary()
    
    def generate_summary(self):
        """生成对话总结"""
        print("[状态] 正在生成对话总结...")
        
        history_text = "\n".join([f"用户: {h['user']}\n助手: {h['assistant']}" for h in self.history])
        
        prompt = f"""
请总结以下对话内容，提取关键信息和讨论要点：

{history_text}

总结要求：
1. 简洁明了，不超过100字
2. 包含主要问题和解决方案
3. 使用中文
"""
        
        summary = self.call_llm(prompt, stream=False)
        self.summary = summary
        print(f"【对话总结】{summary}")
    
    def get_context(self):
        """获取对话上下文"""
        context = ""
        if self.summary:
            context = f"【之前对话总结】{self.summary}\n\n"
        
        # 添加最近的对话历史
        recent_history = self.history[-3:] if len(self.history) > 3 else self.history
        for h in recent_history:
            context += f"用户: {h['user']}\n助手: {h['assistant']}\n"
        
        return context
    
    def call_llm(self, prompt, stream=True):
        """调用LLM"""
        config = self.load_config()
        base_url = config.get('BASE_URL', 'http://localhost:8000/v1')
        model = config.get('MODEL', 'default')
        api_key = config.get('API_KEY', '')
        
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
            "max_tokens": 500,
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
            return f"调用失败: {e}"
        finally:
            conn.close()
    
    def load_config(self):
        """加载配置"""
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

def main():
    """主函数"""
    print("=== 智能对话总结系统 ===")
    print("支持对话历史自动总结")
    print("输入 'exit' 退出")
    print("=" * 50)
    
    conv_manager = ConversationManager()
    
    while True:
        try:
            user_input = input("\n你: ")
            if user_input.lower() == 'exit':
                print("再见！")
                break
            
            # 获取上下文
            context = conv_manager.get_context()
            
            # 构建prompt
            prompt = f"""
{context}
用户: {user_input}
助手:
"""
            
            print("助手: ", end='', flush=True)
            response = conv_manager.call_llm(prompt, stream=True)
            
            # 添加到历史
            conv_manager.add_message(user_input, response)
            
        except KeyboardInterrupt:
            print("\n再见！")
            break

if __name__ == '__main__':
    main()