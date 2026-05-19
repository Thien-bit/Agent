# -*- coding: utf-8 -*-
"""
链式调用测试脚本
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chat_with_chained_calls import ChainedCallManager, search_action, analyze_action, summarize_action, save_to_file

def test_chain_execution():
    """测试链式执行"""
    print("=== 测试链式执行 ===")
    
    manager = ChainedCallManager()
    
    manager.add_step("step1", lambda ctx, res: "结果1")
    manager.add_step("step2", lambda ctx, res: "结果2", dependencies=["step1"])
    manager.add_step("step3", lambda ctx, res: "结果3", dependencies=["step2"])
    
    results = manager.execute({})
    
    assert "step1" in results, "步骤1未执行"
    assert "step2" in results, "步骤2未执行"
    assert "step3" in results, "步骤3未执行"
    
    print(f"执行结果: {results}")
    print("✓ 链式执行测试通过")

def test_dependency_handling():
    """测试依赖处理"""
    print("\n=== 测试依赖处理 ===")
    
    manager = ChainedCallManager()
    
    manager.add_step("required", lambda ctx, res: "必需结果")
    manager.add_step("dependent", lambda ctx, res: "依赖结果", dependencies=["required"])
    manager.add_step("missing_dep", lambda ctx, res: "缺失依赖", dependencies=["nonexistent"])
    
    results = manager.execute({})
    
    assert "required" in results, "必需步骤未执行"
    assert "dependent" in results, "依赖步骤未执行"
    assert "missing_dep" not in results, "缺失依赖的步骤不应该执行"
    
    print(f"执行结果: {results}")
    print("✓ 依赖处理测试通过")

def test_action_functions():
    """测试动作函数"""
    print("\n=== 测试动作函数 ===")
    
    context = {"query": "人工智能"}
    results = {}
    
    search_result = search_action(context, results)
    print(f"搜索结果: {search_result}")
    assert "搜索结果" in search_result, "搜索动作失败"
    
    results["search"] = search_result
    analyze_result = analyze_action(context, results)
    print(f"分析结果: {analyze_result}")
    assert "分析完成" in analyze_result, "分析动作失败"
    
    results["analyze"] = analyze_result
    summarize_result = summarize_action(context, results)
    print(f"总结结果: {summarize_result}")
    assert "总结报告" in summarize_result, "总结动作失败"
    
    print("✓ 动作函数测试通过")

def test_file_save():
    """测试文件保存"""
    print("\n=== 测试文件保存 ===")
    
    content = "测试内容"
    filepath = save_to_file("test_output.txt", content)
    
    assert os.path.exists(filepath), "文件未保存"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        saved_content = f.read()
    
    assert saved_content == content, "文件内容不匹配"
    
    print(f"文件保存路径: {filepath}")
    print("✓ 文件保存测试通过")

def test_full_workflow():
    """测试完整工作流"""
    print("\n=== 测试完整工作流 ===")
    
    manager = ChainedCallManager()
    
    manager.add_step("search", search_action)
    manager.add_step("analyze", analyze_action, dependencies=["search"])
    manager.add_step("summarize", summarize_action, dependencies=["search", "analyze"])
    
    context = {"query": "Python编程"}
    results = manager.execute(context)
    
    assert "search" in results, "搜索步骤缺失"
    assert "analyze" in results, "分析步骤缺失"
    assert "summarize" in results, "总结步骤缺失"
    
    print(f"完整工作流结果: {results}")
    print("✓ 完整工作流测试通过")

if __name__ == '__main__':
    print("=== 链式调用测试 ===")
    print("=" * 50)
    
    test_chain_execution()
    test_dependency_handling()
    test_action_functions()
    test_file_save()
    test_full_workflow()
    
    print("\n=== 所有测试通过 ===")