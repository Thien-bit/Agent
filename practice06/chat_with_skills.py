# -*- coding: utf-8 -*-
"""
技能增强对话系统
支持多种技能的动态调用
"""

import os
import json
import http.client

class SkillManager:
    """技能管理器"""
    
    def __init__(self):
        self.skills = {}
    
    def register(self, skill_name, handler):
        """注册技能"""
        self.skills[skill_name] = handler
        print(f"[技能] 已注册: {skill_name}")
    
    def get_skill(self, skill_name):
        """获取技能处理器"""
        return self.skills.get(skill_name)
    
    def list_skills(self):
        """列出所有技能"""
        return list(self.skills.keys())

# 全局技能管理器
skill_manager = SkillManager()

# 内置技能实现
def search_web_skill(params):
    """网络搜索技能"""
    return f"搜索结果: 关于'{params}'的相关信息"

def calculator_skill(params):
    """计算器技能"""
    allowed_chars = set('0123456789+-*/.() ')
    if all(c in allowed_chars for c in params):
        try:
            result = eval(params)
            return f"计算结果: {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"
    return "计算错误: 包含非法字符"

def weather_skill(params):
    """天气查询技能"""
    return f"天气信息: {params} 晴 26°C"

def summary_skill(params):
    """摘要生成技能"""
    return f"文本摘要: {params[:50]}..."

# 注册内置技能
skill_manager.register("search_web", search_web_skill)
skill_manager.register("calculator", calculator_skill)
skill_manager.register("weather", weather_skill)
skill_manager.register("summary", summary_skill)

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

def call_llm_service(prompt, stream=True):
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
        return f"调用失败: {e}"
    finally:
        conn.close()

def parse_skill_call(response_text):
    """解析技能调用指令"""
    import re
    pattern = r'\[技能调用\]\s*(\w+)\((.*?)\)'
    match = re.search(pattern, response_text)
    
    if match:
        return {
            "skill_name": match.group(1),
            "parameters": match.group(2).strip()
        }
    
    return None

def process_with_skills(user_input):
    """使用技能处理用户请求"""
    print(f"用户问题: {user_input}")
    
    # 构建技能调用提示
    available_skills = skill_manager.list_skills()
    skills_list = "\n".join([f"- {skill}" for skill in available_skills])
    
    prompt = f"""
你是一个智能助手，可以调用以下技能：
{skills_list}

请分析用户请求，如果需要调用技能，请使用格式：[技能调用]技能名(参数)
如果不需要调用技能，可以直接回答。

用户请求：{user_input}
"""
    
    print("[状态] 分析用户请求...")
    response = call_llm_service(prompt, stream=False)
    print(f"分析结果: {response}")
    
    # 检查技能调用
    skill_call = parse_skill_call(response)
    
    if skill_call:
        skill_name = skill_call['skill_name']
        params = skill_call['parameters']
        
        print(f"\n[技能调用] {skill_name}({params})")
        
        # 执行技能
        handler = skill_manager.get_skill(skill_name)
        if handler:
            skill_result = handler(params)
            print(f"技能返回: {skill_result}")
            
            # 总结回答
            summary_prompt = f"""
根据以下技能执行结果，用自然语言回答用户问题：

用户问题：{user_input}
技能执行结果：{skill_result}

请提供友好、清晰的回答。
"""
            
            print("\n助手: ", end='', flush=True)
            return call_llm_service(summary_prompt, stream=True)
        else:
            print(f"未知技能: {skill_name}")
            return "抱歉，该技能暂不可用"
    else:
        print("\n助手: ", end='', flush=True)
        return call_llm_service(f"回答用户问题：{user_input}", stream=True)

if __name__ == '__main__':
    print("=== 技能增强对话系统 ===")
    print(f"已加载技能: {skill_manager.list_skills()}")
    print("输入 'exit' 退出")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n你: ")
            if user_input.lower() == 'exit':
                print("再见！")
                break
            
            process_with_skills(user_input)
            
        except KeyboardInterrupt:
            print("\n再见！")
            break