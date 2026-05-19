# -*- coding: utf-8 -*-
"""
对话系统测试脚本
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_with_skills import process_with_skills, call_llm_service

def test_basic_conversation():
    """测试基础对话功能"""
    print("=== 测试基础对话 ===")
    
    test_cases = [
        "你好",
        "今天天气怎么样",
        "1+2+3等于多少"
    ]
    
    for test_input in test_cases:
        print(f"\n测试输入: {test_input}")
        process_with_skills(test_input)
        print("-" * 40)

def test_llm_direct_call():
    """测试直接调用LLM"""
    print("\n=== 测试LLM直接调用 ===")
    
    prompt = "请用一句话介绍人工智能"
    print(f"Prompt: {prompt}")
    response = call_llm_service(prompt, stream=True)
    print(f"响应: {response}")

def test_skill_invocations():
    """测试技能调用"""
    print("\n=== 测试技能调用 ===")
    
    test_cases = [
        "帮我搜索一下人工智能",
        "计算 25 * 4 + 18",
        "北京今天的天气",
        "请总结：Python是一种高级编程语言，简洁易读，应用广泛。"
    ]
    
    for test_input in test_cases:
        print(f"\n测试输入: {test_input}")
        process_with_skills(test_input)
        print("-" * 40)

if __name__ == '__main__':
    print("=== 对话系统测试 ===")
    print("=" * 50)
    
    test_basic_conversation()
    test_llm_direct_call()
    test_skill_invocations()
    
    print("\n=== 测试完成 ===")