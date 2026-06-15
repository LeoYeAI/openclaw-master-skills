#!/usr/bin/env python3
"""
本地 LLM 集成模块 - 使用 Qwen/CodeLlama 提升 AI 驱动能力

支持:
- Qwen (通义千问) - 阿里云
- CodeLlama - Meta
- ChatGLM - 智谱 AI
- 本地 Ollama 服务
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: str = "ollama"  # ollama, qwen, codellama, chatglm
    model: str = "qwen2.5-coder:7b"
    base_url: str = "http://localhost:11434"
    api_key: str = ""
    timeout: int = 60
    max_tokens: int = 2048
    temperature: float = 0.1  # 低温度更适合代码分析

class LocalLLM:
    """本地 LLM 封装"""
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        
        # 从环境变量读取配置
        if not self.config.api_key:
            self.config.api_key = os.environ.get('LLM_API_KEY', '')
        if not self.config.base_url:
            self.config.base_url = os.environ.get('LLM_BASE_URL', 'http://localhost:11434')
    
    def analyze_vulnerability(self, code: str, vuln_type: str, context: str = "") -> Dict[str, Any]:
        """
        使用 LLM 分析漏洞真实性
        
        Returns:
            {
                'is_vulnerable': bool,
                'confidence': float,
                'explanation': str,
                'fix_suggestion': str,
                'false_positive_reason': str (if applicable)
            }
        """
        prompt = self._build_vulnerability_analysis_prompt(code, vuln_type, context)
        response = self._call_llm(prompt)
        return self._parse_vulnerability_analysis(response)
    
    def generate_fix(self, code: str, vuln_type: str) -> str:
        """生成修复代码"""
        prompt = self._build_fix_generation_prompt(code, vuln_type)
        response = self._call_llm(prompt)
        return self._extract_code_block(response)
    
    def detect_false_positive(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测误报
        
        分析维度:
        1. 上下文是否有防护措施
        2. 代码是否为测试/示例
        3. 变量来源是否可信
        4. 是否有类型安全
        """
        prompt = self._build_false_positive_prompt(finding)
        response = self._call_llm(prompt)
        return self._parse_false_positive_analysis(response)
    
    def _build_vulnerability_analysis_prompt(self, code: str, vuln_type: str, context: str) -> str:
        """构建漏洞分析提示词"""
        return f"""你是一个专业的代码安全审计专家。请分析以下代码是否存在{vuln_type}漏洞。

## 代码片段
```python
{code}
```

## 上下文信息
{context if context else "无额外上下文"}

## 分析要求
1. 判断是否存在真实漏洞 (true positive) 还是误报 (false positive)
2. 如果存在漏洞，说明利用路径和风险等级
3. 如果是误报，说明原因 (如有防护措施、测试代码等)
4. 提供置信度评分 (0.0-1.0)

## 输出格式 (JSON)
{{
    "is_vulnerable": true/false,
    "confidence": 0.0-1.0,
    "risk_level": "CRITICAL/HIGH/MEDIUM/LOW",
    "explanation": "详细说明",
    "exploitation_path": "利用路径描述",
    "false_positive_reason": "如果是误报，说明原因"
}}

请只输出 JSON，不要有其他内容。"""
    
    def _build_fix_generation_prompt(self, code: str, vuln_type: str) -> str:
        """构建修复代码生成提示词"""
        return f"""你是一个专业的代码安全专家。请为以下存在{vuln_type}漏洞的代码生成修复方案。

## 原始代码 (有漏洞)
```python
{code}
```

## 要求
1. 提供 2-3 种修复方案 (如果适用)
2. 说明每种方案的优缺点
3. 推荐最佳方案
4. 确保修复后的代码功能等价

## 输出格式
### 方案 1: [方案名称]
```python
[修复后的代码]
```
**优点**: ...
**缺点**: ...

### 方案 2: [方案名称]
```python
[修复后的代码]
```
**优点**: ...
**缺点**: ...

### 推荐方案
[方案编号] - [理由]"""
    
    def _build_false_positive_prompt(self, finding: Dict[str, Any]) -> str:
        """构建误报检测提示词"""
        return f"""你是一个专业的代码安全审计专家。请分析以下安全警告是否为误报。

## 警告信息
- 类型：{finding.get('type', 'unknown')}
- 文件：{finding.get('location', {}).get('file', 'unknown')}
- 行号：{finding.get('location', {}).get('line', 0)}
- 证据：{finding.get('evidence', '')}

## 代码上下文
{finding.get('context', '无上下文')}

## 分析维度
1. 是否有防护措施 (escape, sanitize, validate, parameterize 等)
2. 是否为测试/示例代码
3. 变量来源是否可信 (配置文件、环境变量等)
4. 是否有类型注解保护
5. 是否有错误处理

## 输出格式 (JSON)
{{
    "is_false_positive": true/false,
    "confidence": 0.0-1.0,
    "reasons": ["原因 1", "原因 2", ...],
    "risk_assessment": "风险评估",
    "recommendation": "建议"
}}

请只输出 JSON，不要有其他内容。"""
    
    def _call_llm(self, prompt: str) -> str:
        """调用 LLM"""
        if self.config.provider == "ollama":
            return self._call_ollama(prompt)
        elif self.config.provider == "qwen":
            return self._call_qwen(prompt)
        elif self.config.provider == "chatglm":
            return self._call_chatglm(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")
    
    def _call_ollama(self, prompt: str) -> str:
        """调用本地 Ollama 服务"""
        url = f"{self.config.base_url}/api/generate"
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.config.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        except requests.exceptions.ConnectionError:
            # Ollama 服务不可用，降级到规则引擎
            return self._fallback_rule_based(prompt)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _call_qwen(self, prompt: str) -> str:
        """调用通义千问 API"""
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.config.model,
            "input": {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get('output', {}).get('text', '')
        except Exception as e:
            return self._fallback_rule_based(prompt)
    
    def _call_chatglm(self, prompt: str) -> str:
        """调用智谱 ChatGLM API"""
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get('choices', [{}])[0].get('message', {}).get('content', '')
        except Exception as e:
            return self._fallback_rule_based(prompt)
    
    def _fallback_rule_based(self, prompt: str) -> str:
        """LLM 不可用时的规则引擎降级"""
        # 简单的关键词匹配
        if "false positive" in prompt.lower():
            return json.dumps({
                "is_false_positive": False,
                "confidence": 0.5,
                "reasons": ["LLM unavailable, using rule-based analysis"],
                "risk_assessment": "Medium - requires manual review",
                "recommendation": "Please review manually"
            })
        else:
            return json.dumps({
                "is_vulnerable": True,
                "confidence": 0.5,
                "risk_level": "MEDIUM",
                "explanation": "LLM unavailable, using rule-based analysis",
                "recommendation": "Please review manually"
            })
    
    def _parse_vulnerability_analysis(self, response: str) -> Dict[str, Any]:
        """解析漏洞分析结果"""
        try:
            # 提取 JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"error": "Failed to parse JSON", "raw_response": response}
        except json.JSONDecodeError:
            return {"error": "JSON decode error", "raw_response": response}
    
    def _parse_false_positive_analysis(self, response: str) -> Dict[str, Any]:
        """解析误报分析结果"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"error": "Failed to parse JSON", "raw_response": response}
        except json.JSONDecodeError:
            return {"error": "JSON decode error", "raw_response": response}
    
    def _extract_code_block(self, response: str) -> str:
        """提取代码块"""
        import re
        pattern = r'```(?:python)?\s*(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        return matches[0].strip() if matches else response


# 便捷函数
def init_llm(provider: str = "ollama", model: str = None) -> LocalLLM:
    """初始化 LLM"""
    config = LLMConfig(provider=provider)
    if model:
        config.model = model
    return LocalLLM(config)


def analyze_with_llm(code: str, vuln_type: str, context: str = "") -> Dict[str, Any]:
    """便捷函数：使用 LLM 分析漏洞"""
    llm = init_llm()
    return llm.analyze_vulnerability(code, vuln_type, context)


if __name__ == "__main__":
    # 测试示例
    test_code = '''
def get_user(user_id):
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()
'''
    
    llm = init_llm()
    result = llm.analyze_vulnerability(test_code, "SQL Injection")
    print(json.dumps(result, indent=2, ensure_ascii=False))
