import os
import json
import http.client

def load_config():
    """读取配置文件中的环境变量"""
    config = {}
    config_path = os.path.join(os.path.dirname(__file__), '.env')
    print(f"[调试] 配置文件路径: {config_path}")
    
    try:
        print(f"[调试] 文件存在检查: {os.path.exists(config_path)}")
        with open(config_path, 'r', encoding='utf-8') as f:
            print("[调试] 配置文件读取成功")
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    separator = line.find('=')
                    if separator != -1:
                        key = line[:separator].strip()
                        value = line[separator+1:].strip()
                        config[key] = value
                        print(f"[调试] 已加载配置项: {key} = {value}")
    except FileNotFoundError:
        print(f"[错误] 未找到配置文件: {config_path}")
        return None
    except Exception as err:
        print(f"[错误] 加载配置失败: {str(err)}")
        return None
    
    print(f"[调试] 已加载的配置: {config}")
    return config

def invoke_ai(prompt_text, token_limit=100):
    """通过HTTP协议调用AI模型"""
    config = load_config()
    if not config:
        return "系统错误：无法加载配置信息"
    
    endpoint = config.get('BASE_URL')
    model_name = config.get('MODEL')
    secret_key = config.get('API_KEY')
    
    if not all([endpoint, model_name, secret_key]):
        return "系统错误：缺少必要的配置参数"
    
    # 解析服务地址
    protocol = 'http'
    if endpoint.startswith('http://'):
        endpoint = endpoint[7:]
    elif endpoint.startswith('https://'):
        endpoint = endpoint[8:]
        protocol = 'https'
    
    # 分离主机和路径
    if '/' in endpoint:
        host_addr, api_path = endpoint.split('/', 1)
        api_path = '/' + api_path
    else:
        host_addr = endpoint
        api_path = '/'
    
    # 构造请求体
    request_body = {
        "model": model_name,
        "prompt": prompt_text,
        "max_tokens": token_limit
    }
    
    # 创建连接
    try:
        if protocol == 'https':
            connection = http.client.HTTPSConnection(host_addr)
        else:
            connection = http.client.HTTPConnection(host_addr)
    except Exception as err:
        return f"连接错误：{str(err)}"
    
    # 设置请求头
    request_headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {secret_key}'
    }
    
    try:
        # 发送请求
        connection.request('POST', f'{api_path}/completions', 
                          body=json.dumps(request_body), headers=request_headers)
        
        # 获取响应
        response = connection.getresponse()
        
        # 读取响应内容
        response_data = response.read().decode('utf-8')
        
        # 解析响应
        result = json.loads(response_data)
        
        # 提取生成内容
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['text']
        else:
            return f"响应异常：{response_data}"
    except Exception as err:
        return f"请求错误：{str(err)}"
    finally:
        connection.close()

if __name__ == '__main__':
    # 测试功能
    test_prompt = "Hello, how are you?"
    print(f"测试输入: {test_prompt}")
    ai_response = invoke_ai(test_prompt)
    print(f"AI回复: {ai_response}")