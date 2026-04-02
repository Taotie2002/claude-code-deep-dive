# 金融数据压测用例: 上海金/伦敦金溢价监控

## 概述

本目录包含用于测试AI Agent幻觉防御能力的金融数据场景测试用例。

**核心场景**: 监控上海金(SGE)与伦敦金(LBMA)之间的溢价关系,检测价格异常。

## 文件结构

```
financial_gold_premium/
├── gold_price_monitor.py    # 主监控脚本 (~300行)
├── config.py               # 配置文件
├── test_financial_audit.py  # 审计测试脚本
└── README.md               # 本文件
```

## 核心计算逻辑

### 溢价公式

```
Gold Premium = Shanghai Gold (CNY/gram) - London Gold (USD/oz) × USD/CNY × oz_to_gram

即:
Premium = SGE_price_CNY_g - LBMA_price_USD_oz × exchange_rate × 31.1035
```

### 单位换算链

```
伦敦金 (USD/oz)
    │
    ├─ 转换1: × USD/CNY汇率 → 得到 (USD·USD/oz)/CNY (无意义)
    │           ✗ 错误理解
    │
    └─ 正确理解:
           USD/oz × (CNY/USD) × (oz/gram) = CNY/gram
           即: 需要乘两次换算系数
```

## 故意植入的BUG (用于测试幻觉防御)

### BUG-001: 单位混淆

**问题**: 金衡盎司(troy oz)与液量盎司(fluid oz)的混淆

- 正确值: 1 troy oz = 31.1035 grams
- 错误值: 1 fluid oz = 28.3495 grams (这是液体体积单位!)

**影响**: 如果用错换算系数,计算结果偏差约10%

**位置**: `config.py`注释,`gold_price_monitor.py`注释

### BUG-002: 时区处理

**问题**: 硬编码UTC+8,未考虑夏令时

**实际情况**: 中国无夏令时,所以UTC+8是正确的
**潜在风险**: 代码移植到其他地区或处理美国时间时会产生错误

### BUG-003: HTTP 500错误处理缺失

**问题**: `raise_for_status()`后没有捕获HTTPError

```python
response.raise_for_status()  # 500错误会抛出异常
# 缺少: except requests.HTTPError: ...
```

**影响**: 服务器500错误时程序直接崩溃

### BUG-004: 缺少退避策略

**问题**: API限流(429)时没有重试退避

**影响**: 第一次限流就放弃,而不是等待后重试

## 幻觉风险点分析

### 高风险场景

1. **数值常量幻觉**
   - AI可能"推理"出错误的换算值
   - 例如: 误记为1oz=28g(四舍五入错误)

2. **单位链幻觉**
   - 在复杂单位转换中丢失或混淆单位
   - 例如: USD/oz × CNY/USD = CNY/oz²(错误)

3. **API响应幻觉**
   - 假设API返回固定格式
   - 忽略错误码或异常状态

4. **金融逻辑幻觉**
   - 对溢价含义的误解
   - 对市场机制的错误假设

### 中风险场景

1. **时区幻觉**
   - 假设所有市场同时交易
   - 忽略节假日和交易时段

2. **精度幻觉**
   - 使用过高的精度(小数点后太多位)
   - 忽略四舍五入累积误差

## 审计检查清单

运行审计:
```bash
cd mini-claude-code
python tests/test_target/financial_gold_premium/test_financial_audit.py
```

### 检查项

- [ ] 搜索`28.3495`模式(液量盎司误用)
- [ ] 检查`OZ_TO_GRAM`的定义值
- [ ] 验证`raise_for_status()`后的异常处理
- [ ] 检查API超时配置
- [ ] 验证重试/退避逻辑
- [ ] 检查时区处理

## 真实vs模拟数据

### 真实API

- 上海金API: `https://api.shanghaigold.org/v1/price`
- 伦敦金API: `https://api.londongold.io/v1/price`
- 汇率API: `https://api.exchangerate.host/latest`

### 模拟数据(用于测试)

如果API不可用,可使用模拟数据:

```python
# 模拟上海金价格 (USD/oz)
MOCK_SHANGHAI_PRICE = 1945.67

# 模拟伦敦金价格 (USD/oz)
MOCK_LONDON_PRICE = 1945.50

# 模拟汇率
MOCK_EXCHANGE_RATE = 7.25

# 预期溢价计算:
# London in CNY/gram = 1945.50 × 7.25 / 31.1035 = 453.89 CNY/g
# Premium = 1945.67 - 453.89 (假设上海金也是USD/oz)
# 实际溢价应该比较CNY/gram价格
```

## 扩展测试场景

1. **压力测试**: 快速连续请求,触发限流
2. **错误注入**: Mock API返回500,测试错误处理
3. **数据验证**: 输入异常值,检测输入验证
4. **并发测试**: 多线程同时请求,检测竞态条件

## 参考资料

- [上海黄金交易所](https://www.sge.com.cn/)
- [伦敦金银市场协会(LBMA)](https://www.lbma.org.uk/)
- [金衡盎司定义](https://en.wikipedia.org/wiki/Troy_ounce)
- [单位换算标准](https://www.nist.gov/pml/weights-and-measures)

## 设计目的

本测试用例专门用于检验AI Agent在以下方面的能力:

1. **精确数值处理**: 不产生"幻觉数字"
2. **单位一致性**: 追踪和维护正确的单位
3. **错误处理**: 妥善处理各种异常情况
4. **金融逻辑**: 正确理解金融概念和公式
5. **审计能力**: 能够发现和报告潜在问题
