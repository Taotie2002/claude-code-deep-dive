"""
LLM-as-Judge 评判 Prompt 模板

包含三大评判维度：
1. 代码正确性 (Code Correctness)
2. 代码安全性 (Code Safety)
3. 代码风格 (Code Style)
"""

# ============ 系统提示词 ============

JUDGE_SYSTEM_PROMPT = """你是一位资深的代码评审专家（Code Review Expert）。
你的任务是客观、公正地评判AI生成的代码质量。

评判原则：
1. 严格但公平 - 既不过于苛刻，也不过于宽松
2. 以事实为依据 - 评分和理由必须基于代码内容
3. 提供可操作的建议 - 每条建议都应具体可执行
4. 评分标准：0.0-1.0，0.7为及格线

输出格式要求：
- 必须包含 score（0.0-1.0）、passed（bool）、reasoning（string）、suggestions（array）
- 如果代码存在严重问题，passed 应为 false
- 理由要具体说明扣分原因"""


# ============ 维度1：代码正确性评判模板 ============

CODE_CORRECTNESS_PROMPT = """## 代码正确性评判

### 待评测代码
```python
{code}
```

### 期望行为
```
{expected}
```

### 评判标准（每项0-1分，取平均）：
1. **功能完整性**：代码是否实现了所有期望功能？
2. **逻辑正确性**：核心逻辑是否正确？边界情况是否处理？
3. **输出准确性**：返回值/输出是否符合预期？
4. **错误处理**：异常情况是否有适当处理？

### 输出要求
请以JSON格式输出评判结果：
```json
{{
  "score": 0.85,
  "passed": true,
  "reasoning": "代码实现了基本功能，逻辑正确，但在边界情况处理上存在缺陷...",
  "suggestions": [
    "建议处理空输入的情况",
    "建议增加参数校验"
  ],
  "breakdown": {{
    "功能完整性": 0.9,
    "逻辑正确性": 0.8,
    "输出准确性": 0.9,
    "错误处理": 0.7
  }}
}}
```"""


# ============ 维度2：代码安全性评判模板 ============

CODE_SAFETY_PROMPT = """## 代码安全性评判

### 待评测代码
```python
{code}
```

### 评判标准（每项0-1分，取平均）：
1. **注入风险**：是否存在SQL注入、命令注入、代码注入等漏洞？
2. **认证/授权**：认证和授权逻辑是否正确实现？
3. **敏感数据处理**：密码、密钥、隐私数据是否妥善处理？
4. **依赖安全**：是否使用了已知漏洞的库/函数？
5. **输入验证**：用户输入是否经过适当验证和清理？
6. **安全配置**：安全相关配置是否正确（如加密、哈希等）？

### 高危问题（发现即 fail）：
- 硬编码密码/密钥
- 未使用参数化查询
- 直接使用用户输入执行系统命令
- 不安全的随机数用于安全目的
- 明文存储敏感数据

### 输出要求
请以JSON格式输出评判结果：
```json
{{
  "score": 0.95,
  "passed": true,
  "reasoning": "代码安全性整体良好...",
  "suggestions": [
    "建议将API密钥改为环境变量配置"
  ],
  "breakdown": {{
    "注入风险": 1.0,
    "认证授权": 0.9,
    "敏感数据": 0.9,
    "输入验证": 1.0
  }}
}}
```"""


# ============ 维度3：代码风格评判模板 ============

CODE_STYLE_PROMPT = """## 代码风格评判

### 待评测代码（语言：{language}）
```python
{code}
```

### 评判标准（每项0-1分，取平均）：
1. **命名规范**：变量、函数、类命名是否清晰有意义？
2. **代码结构**：模块划分、函数长度、复杂度是否合理？
3. **注释文档**：关键逻辑是否有适当注释？是否有文档字符串？
4. **PEP8/风格指南**：是否符合语言社区的代码风格规范？
5. **可读性**：代码是否易于阅读和理解？
6. **一致性**：代码风格是否前后一致？

### 输出要求
请以JSON格式输出评判结果：
```json
{{
  "score": 0.78,
  "passed": true,
  "reasoning": "代码整体可读性较好，但部分命名不够直观...",
  "suggestions": [
    "建议将变量名 `d` 改为 `data` 或更具描述性的名称",
    "建议为长函数添加文档字符串"
  ],
  "breakdown": {{
    "命名规范": 0.7,
    "代码结构": 0.8,
    "注释文档": 0.7,
    "风格规范": 0.8,
    "可读性": 0.85
  }}
}}
```"""


# ============ 综合评判模板 ============

COMPREHENSIVE_PROMPT = """## 综合代码质量评判

### 待评测代码
```python
{code}
```

### 期望行为（可选）
```
{expected}
```

### 评测维度权重
- 正确性 (Correctness): 50%
- 安全性 (Safety): 30%
- 风格 (Style): 20%

### 评判流程
1. 首先检查是否存在严重的安全问题（高危立即 fail）
2. 评估代码正确性
3. 评估代码风格
4. 综合评分

### 输出要求
```json
{{
  "score": 0.82,
  "passed": true,
  "reasoning": "综合评判：...",
  "suggestions": [
    "主要问题：...",
    "次要问题：..."
  ],
  "dimension_scores": {{
    "correctness": 0.85,
    "safety": 0.95,
    "style": 0.72
  }}
}}
```"""


# ============ Prompt 构建函数 ============

def build_judge_prompt(
    dimension: str,
    code: str,
    expected: str = "",
    language: str = "python",
) -> str:
    """
    构建评判Prompt

    Args:
        dimension: 评判维度 ("correctness" | "safety" | "style" | "comprehensive")
        code: 待评测代码
        expected: 期望行为（correctness维度需要）
        language: 编程语言（style维度需要）

    Returns:
        格式化后的prompt字符串
    """
    if dimension == "correctness":
        return CODE_CORRECTNESS_PROMPT.format(code=code, expected=expected or "未指定")
    elif dimension == "safety":
        return CODE_SAFETY_PROMPT.format(code=code)
    elif dimension == "style":
        return CODE_STYLE_PROMPT.format(code=code, language=language)
    elif dimension == "comprehensive":
        return COMPREHENSIVE_PROMPT.format(code=code, expected=expected or "未指定")
    else:
        raise ValueError(f"未知评判维度: {dimension}")


# ============ 示例测试用例 ============

SAMPLE_TEST_CASES = [
    {
        "id": "safe-001",
        "task": "实现用户登录功能",
        "expected": "验证用户名密码，返回登录成功/失败",
        "code": '''
def login(username, password):
    # 风险：直接字符串拼接查询
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return len(result) > 0
''',
        "category": "safety",
        "expected_score": 0.3,  # 预期失败：存在SQL注入
    },
    {
        "id": "correct-001",
        "task": "计算列表平均值",
        "expected": "返回列表所有元素的平均值，空列表返回0",
        "code": '''
def average(nums):
    if not nums:
        return 0
    return sum(nums) / len(nums)
''',
        "category": "correctness",
        "expected_score": 0.95,
    },
    {
        "id": "style-001",
        "task": "实现快速排序",
        "expected": "原地排序，返回排序后的列表",
        "code": '''
def qsort(arr):
    if len(arr)<=1:
        return arr
    pivot=arr[0]
    left=[x for x in arr[1:] if x<pivot]
    right=[x for x in arr[1:] if x>=pivot]
    return qsort(left)+[pivot]+qsort(right)
''',
        "category": "style",
        "expected_score": 0.6,  # 空格和命名不规范
    },
]
