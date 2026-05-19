# -*- coding: utf-8 -*-
"""
技能模块测试脚本
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_with_skills import skill_manager, search_web_skill, calculator_skill, weather_skill, summary_skill

def test_skill_registration():
    """测试技能注册"""
    print("=== 测试技能注册 ===")
    
    skills = skill_manager.list_skills()
    print(f"已注册技能: {skills}")
    
    assert 'search_web' in skills, "search_web技能未注册"
    assert 'calculator' in skills, "calculator技能未注册"
    assert 'weather' in skills, "weather技能未注册"
    assert 'summary' in skills, "summary技能未注册"
    
    print("✓ 技能注册测试通过")

def test_search_web():
    """测试搜索技能"""
    print("\n=== 测试搜索技能 ===")
    
    result = search_web_skill("人工智能")
    print(f"搜索结果: {result}")
    
    assert "搜索结果" in result, "搜索技能返回格式不正确"
    print("✓ 搜索技能测试通过")

def test_calculator():
    """测试计算器技能"""
    print("\n=== 测试计算器技能 ===")
    
    tests = [
        ("2 + 3", "计算结果: 5"),
        ("10 * 5", "计算结果: 50"),
        ("100 / 4", "计算结果: 25.0"),
        ("invalid", "计算错误")
    ]
    
    for expr, expected in tests:
        result = calculator_skill(expr)
        print(f"{expr} → {result}")
        
        if expected != "计算错误":
            assert expected in result, f"计算结果不正确: {result}"
        else:
            assert expected in result, f"错误处理不正确: {result}"
    
    print("✓ 计算器技能测试通过")

def test_weather():
    """测试天气技能"""
    print("\n=== 测试天气技能 ===")
    
    result = weather_skill("北京")
    print(f"天气结果: {result}")
    
    assert "天气信息" in result, "天气技能返回格式不正确"
    print("✓ 天气技能测试通过")

def test_summary():
    """测试摘要技能"""
    print("\n=== 测试摘要技能 ===")
    
    long_text = "Python是一种高级编程语言，由Guido van Rossum于1991年发布。它以简洁的语法和强大的功能著称，广泛应用于Web开发、数据科学、人工智能等领域。"
    result = summary_skill(long_text)
    print(f"摘要结果: {result}")
    
    assert "文本摘要" in result, "摘要技能返回格式不正确"
    print("✓ 摘要技能测试通过")

def test_dynamic_registration():
    """测试动态注册技能"""
    print("\n=== 测试动态注册 ===")
    
    def custom_skill(params):
        return f"自定义技能: {params}"
    
    skill_manager.register("custom", custom_skill)
    
    skills = skill_manager.list_skills()
    assert 'custom' in skills, "自定义技能注册失败"
    
    handler = skill_manager.get_skill("custom")
    result = handler("测试参数")
    assert "自定义技能" in result, "自定义技能执行失败"
    
    print(f"已注册技能: {skills}")
    print(f"自定义技能结果: {result}")
    print("✓ 动态注册测试通过")

if __name__ == '__main__':
    print("=== 技能模块测试 ===")
    print("=" * 50)
    
    test_skill_registration()
    test_search_web()
    test_calculator()
    test_weather()
    test_summary()
    test_dynamic_registration()
    
    print("\n=== 所有测试通过 ===")