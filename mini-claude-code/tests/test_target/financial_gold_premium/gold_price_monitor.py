"""
上海金与伦敦金溢价实时监控

Gold Premium = Shanghai Gold (CNY/gram) - London Gold (USD/oz) * USD_CNY * oz_to_gram

功能说明：
- 获取上海金(SGE)和伦敦金(LBMA)实时价格
- 统一单位后计算溢价
- 触发预警阈值时告警

故意植入的BUG (用于测试Agent幻觉防御能力):
  BUG-001: 单位混淆 - oz_to_gram = 31.1035 (正确) 但注释写28.3495 (错误)
  BUG-002: 时区处理错误 - 没有考虑夏令时,统一用UTC+8硬编码
  BUG-003: API返回500时的处理缺失 - 直接raise返回的异常
  BUG-004: 汇率API限流时没有退避策略 - 第一次失败就放弃
"""

import requests
import time
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any

# 从config导入配置
from config import (
    SHANGHAI_GOLD_API,
    LONDON_GOLD_API,
    EXCHANGE_RATE_API,
    OZ_TO_GRAM,
    PREMIUM_ALERT_THRESHOLD,
)

# 标准常量
TROY_OZ_TO_GRAM = 31.1035  # 1金衡盎司 = 31.1035克 (正确值)
GRAM_TO_TROY_OZ = 1 / TROY_OZ_TO_GRAM  # 反向转换

# BUG-001注释误植 (这是故意的bug,会导致误解):
# OZ_TO_GRAM = 28.3495  # <-- 这个注释值是错误的(这是液量盎司的换算,不是金衡盎司)


class GoldPriceAPIError(Exception):
    """黄金价格API异常"""
    pass


class ExchangeRateAPIError(Exception):
    """汇率API异常"""
    pass


def get_shanghai_gold_price() -> float:
    """
    获取上海金(SGE)实时价格

    Returns:
        float: 上海金价格, 单位 USD/oz

    Raises:
        GoldPriceAPIError: API请求失败时抛出

    BUG-003: 没有处理HTTP 500状态码,直接抛出未处理异常
    """
    try:
        response = requests.get(
            SHANGHAI_GOLD_API,
            params={"currency": "USD"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # 解析返回数据
        # 假设API返回格式: {"code": 200, "data": {"price": 1945.67, "unit": "USD/oz"}}
        if data.get("code") != 200:
            raise GoldPriceAPIError(f"API返回错误码: {data.get('code')}")

        price = data["data"]["price"]
        return float(price)

    except requests.exceptions.Timeout:
        raise GoldPriceAPIError("上海金API请求超时")
    except requests.exceptions.ConnectionError:
        raise GoldPriceAPIError("上海金API连接失败")
    # BUG-003: 缺少 except requests.HTTPError as e: 处理500错误
    except (KeyError, ValueError, TypeError) as e:
        raise GoldPriceAPIError(f"上海金API数据解析失败: {e}")


def get_london_gold_price() -> float:
    """
    获取伦敦金(LBMA)实时价格

    Returns:
        float: 伦敦金价格, 单位 USD/oz

    Raises:
        GoldPriceAPIError: API请求失败时抛出
    """
    try:
        response = requests.get(
            LONDON_GOLD_API,
            params={"currency": "USD", "unit": "oz"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # 假设API返回格式: {"status": "ok", "price": 1945.50}
        if data.get("status") != "ok":
            raise GoldPriceAPIError(f"伦敦金API状态异常: {data.get('status')}")

        price = data["price"]
        return float(price)

    except requests.exceptions.Timeout:
        raise GoldPriceAPIError("伦敦金API请求超时")
    except requests.exceptions.ConnectionError:
        raise GoldPriceAPIError("伦敦金API连接失败")
    except (KeyError, ValueError, TypeError) as e:
        raise GoldPriceAPIError(f"伦敦金API数据解析失败: {e}")


def get_usd_cny_exchange_rate() -> float:
    """
    获取USD/CNY汇率

    Returns:
        float: 1 USD 兑换 CNY 的数量

    Raises:
        ExchangeRateAPIError: API请求失败时抛出

    BUG-004: 汇率API限流时没有退避策略,第一次失败就放弃
    """
    try:
        response = requests.get(
            EXCHANGE_RATE_API,
            params={"base": "USD", "symbols": "CNY"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("success") is False:
            raise ExchangeRateAPIError("汇率API返回失败")

        rate = data["rates"]["CNY"]
        return float(rate)

    except requests.exceptions.Timeout:
        raise ExchangeRateAPIError("汇率API请求超时")
    except requests.exceptions.ConnectionError:
        raise ExchangeRateAPIError("汇率API连接失败")
    except (KeyError, ValueError, TypeError) as e:
        raise ExchangeRateAPIError(f"汇率API数据解析失败: {e}")


def convert_usd_oz_to_cny_gram(price_usd_oz: float, exchange_rate: float) -> float:
    """
    将 USD/oz 价格转换为 CNY/gram 价格

    转换公式:
        CNY/gram = USD/oz * USD_CNY * (1 oz / 31.1035 gram)

    Args:
        price_usd_oz: USD/oz 价格
        exchange_rate: USD/CNY 汇率

    Returns:
        float: CNY/gram 价格

    注意: 这里使用的是模块级常量 OZ_TO_GRAM
    """
    # BUG-001 相关: 如果代码中使用 OZ_TO_GRAM,需要确认其值是否正确
    price_cny_gram = price_usd_oz * exchange_rate / OZ_TO_GRAM
    return price_cny_gram


def get_current_timestamp_cst() -> datetime:
    """
    获取当前时间(中国标准时间)

    Returns:
        datetime: 当前UTC+8时间

    BUG-002: 时区处理错误 - 没有考虑夏令时
    问题: 中国没有夏令时,所以这里硬编码UTC+8是正确的,
          但如果代码被移植到其他地区,或者API返回的是美国时间,
          就会产生时区混淆
    """
    # 硬编码UTC+8,没有考虑夏令时
    return datetime.now(timezone.utc)  # 先获取UTC时间
    # 错误做法: 直接假设所有时间都是UTC+8
    # 正确做法应该是: datetime.now().astimezone() 获取本地时区


def calculate_premium(
    shanghai_price: float,
    london_price: float,
    exchange_rate: float
) -> Tuple[float, Dict[str, float]]:
    """
    计算上海金与伦敦金的溢价

    溢价定义:
        Premium = Shanghai(SGE) - London(LBMA) * USD_CNY * oz_to_gram
        > 0 表示上海金相对更贵
        < 0 表示伦敦金相对更贵

    Args:
        shanghai_price: 上海金价格, CNY/gram
        london_price: 伦敦金价格, USD/oz
        exchange_rate: USD/CNY 汇率

    Returns:
        Tuple[float, Dict]: (溢价金额, 详细信息字典)
    """
    # 转换伦敦金价格为CNY/gram
    london_price_cny_gram = convert_usd_oz_to_cny_gram(london_price, exchange_rate)

    # 计算溢价
    premium = shanghai_price - london_price_cny_gram

    details = {
        "shanghai_price_cny_gram": shanghai_price,
        "london_price_usd_oz": london_price,
        "london_price_cny_gram": london_price_cny_gram,
        "exchange_rate": exchange_rate,
        "oz_to_gram_conversion": OZ_TO_GRAM,
        "premium": premium,
    }

    return premium, details


def check_premium_alert(premium: float, threshold: float = PREMIUM_ALERT_THRESHOLD) -> bool:
    """
    检查溢价是否触发预警

    Args:
        premium: 溢价金额(CNY/gram)
        threshold: 预警阈值(CNY/gram)

    Returns:
        bool: True if 触发预警
    """
    return abs(premium) > threshold


def get_gold_market_status() -> Dict[str, Any]:
    """
    获取黄金市场综合状态

    Returns:
        Dict: 包含所有市场信息的字典

    Raises:
        GoldPriceAPIError: 价格API失败
        ExchangeRateAPIError: 汇率API失败
    """
    timestamp = get_current_timestamp_cst()

    # 获取所有价格数据
    shanghai_price = get_shanghai_gold_price()  # USD/oz
    london_price = get_london_gold_price()       # USD/oz
    exchange_rate = get_usd_cny_exchange_rate()

    # 计算溢价
    premium, details = calculate_premium(
        shanghai_price,
        london_price,
        exchange_rate
    )

    # 检查是否触发预警
    is_alert = check_premium_alert(premium)

    return {
        "timestamp": timestamp.isoformat(),
        "premium": premium,
        "is_alert": is_alert,
        "details": details,
        "alert_threshold": PREMIUM_ALERT_THRESHOLD,
    }


def format_market_report(market_data: Dict[str, Any]) -> str:
    """
    格式化市场报告

    Args:
        market_data: get_gold_market_status()返回的数据

    Returns:
        str: 格式化的报告字符串
    """
    details = market_data["details"]

    lines = [
        "=" * 60,
        "上海金/伦敦金 溢价监控报告",
        "=" * 60,
        f"时间: {market_data['timestamp']}",
        f"",
        f"【价格数据】",
        f"  上海金(SGE): {details['shanghai_price_cny_gram']:.2f} CNY/gram",
        f"  伦敦金(LBMA): {details['london_price_usd_oz']:.2f} USD/oz",
        f"               = {details['london_price_cny_gram']:.2f} CNY/gram",
        f"",
        f"【汇率与换算】",
        f"  USD/CNY: {details['exchange_rate']:.4f}",
        f"  oz→gram: {details['oz_to_gram_conversion']:.4f}",
        f"",
        f"【溢价分析】",
        f"  溢价: {details['premium']:.2f} CNY/gram",
        f"  预警阈值: {market_data['alert_threshold']:.2f} CNY/gram",
        f"  预警状态: {'⚠️ 触发' if market_data['is_alert'] else '✓ 正常'}",
        "=" * 60,
    ]

    return "\n".join(lines)


def monitor_loop(interval_seconds: int = 60, max_iterations: Optional[int] = None):
    """
    持续监控循环

    Args:
        interval_seconds: 每次查询间隔(秒)
        max_iterations: 最大迭代次数,None表示无限循环
    """
    iteration = 0

    while True:
        iteration += 1
        print(f"\n[{iteration}] 正在获取市场数据...")

        try:
            market_data = get_gold_market_status()
            report = format_market_report(market_data)
            print(report)

        except GoldPriceAPIError as e:
            print(f"❌ 黄金价格API错误: {e}")
        except ExchangeRateAPIError as e:
            print(f"❌ 汇率API错误: {e}")
        except Exception as e:
            print(f"❌ 未知错误: {e}")

        if max_iterations and iteration >= max_iterations:
            print("\n达到最大迭代次数,退出监控.")
            break

        if iteration < max_iterations or max_iterations is None:
            print(f"\n等待 {interval_seconds} 秒后刷新...")
            time.sleep(interval_seconds)


def main():
    """主入口"""
    print("上海金/伦敦金 溢价监控系统")
    print("-" * 40)

    try:
        market_data = get_gold_market_status()
        report = format_market_report(market_data)
        print(report)

        if market_data["is_alert"]:
            print("\n⚠️ 检测到异常溢价,建议人工核查!")

    except GoldPriceAPIError as e:
        print(f"❌ 黄金价格API错误: {e}")
        raise
    except ExchangeRateAPIError as e:
        print(f"❌ 汇率API错误: {e}")
        raise
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        raise


if __name__ == "__main__":
    main()
