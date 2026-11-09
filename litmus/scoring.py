"""综合分与效率系数计算模块（纯函数，不读写文件）。"""

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

# 难度权重配置
DIFFICULTY_WEIGHTS: Dict[str, int] = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
    "long": 6,
}

# 可以按隐藏测试通过比例拿部分分的难度：长任务边界情况多，
# 全对或全错会把"差一条用例"和"完全没做"算成一样，丢掉大部分区分度
PARTIAL_CREDIT_DIFFICULTIES = frozenset({"long"})

# 单题 token 预算配置
TOKEN_BUDGETS: Dict[str, int] = {
    "easy": 40000,
    "medium": 100000,
    "hard": 250000,
    "long": 800000,
}


def compute_time_score(r: Optional[float]) -> Optional[float]:
    """计算单题时间得分。

    r = 实际耗时秒 / (ref_minutes * 60)
    r <= 1 时得 1.0；否则得 max(0.6, 1.0 - 0.2 * log2(r))。
    r 为 None 或负数时返回 None。
    """
    if r is None or r < 0:
        return None
    if r <= 1.0:
        return 1.0
    return max(0.6, 1.0 - 0.2 * math.log2(r))


def compute_effective_tokens(
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
) -> float:
    """计算单题计费等价 token。

    计费等价 token = 未命中缓存的输入 + 缓存写入 + 输出（含思考） + 0.1 * 缓存读取
    """
    return (
        float(max(0, input_tokens))
        + float(max(0, cache_write_tokens))
        + float(max(0, output_tokens))
        + 0.1 * float(max(0, cache_read_tokens))
    )


def compute_token_score(
    effective_tokens: Optional[float], difficulty: str
) -> Optional[float]:
    """计算单题 token 得分。

    预算内得 1.0；超预算得 max(0.5, 1.0 - 0.25 * log2(用量 / 预算))。
    用量为 None 或未知难度预算时返回 None。
    """
    if effective_tokens is None or effective_tokens < 0:
        return None
    budget = TOKEN_BUDGETS.get(difficulty)
    if not budget or budget <= 0:
        return None
    if effective_tokens <= budget:
        return 1.0
    ratio = float(effective_tokens) / float(budget)
    return max(0.5, 1.0 - 0.25 * math.log2(ratio))


def _as_int(val: Any) -> Optional[int]:
    """把判分明细里的计数转成 int，类型不对返回 None（布尔值不算计数）。"""
    if isinstance(val, bool) or not isinstance(val, int):
        return None
    return val


def compute_task_credit(task: Dict[str, Any]) -> float:
    """计算单题得分比例（0～1）。

    通过的题得 1。长任务（tests 判分）没全过时，按 F2P 用例通过比例给部分分，
    但以下任一情况得 0：可合入性否决、没跑出测试结果（编译失败、整体超时、未提交、跳过）、
    任何 P2P 用例被改坏。其他难度不通过一律得 0。
    """
    if bool(task.get("passed", False)):
        return 1.0
    diff = str(task.get("difficulty") or "easy")
    if diff not in PARTIAL_CREDIT_DIFFICULTIES:
        return 0.0
    if str(task.get("grader") or "tests") != "tests":
        return 0.0
    if bool(task.get("merge_veto", False)):
        return 0.0
    if str(task.get("status") or "") in ("skipped", "incomplete"):
        return 0.0
    extra = task.get("extra")
    if not isinstance(extra, dict):
        return 0.0
    f2p_passed = _as_int(extra.get("f2p_passed"))
    f2p_total = _as_int(extra.get("f2p_total"))
    p2p_passed = _as_int(extra.get("p2p_passed"))
    p2p_total = _as_int(extra.get("p2p_total"))
    if None in (f2p_passed, f2p_total, p2p_passed, p2p_total):
        return 0.0
    if f2p_total <= 0 or p2p_passed != p2p_total:
        return 0.0
    return min(1.0, max(0.0, float(f2p_passed) / float(f2p_total)))


def _round_val(val: Optional[float], digits: int = 4) -> Optional[float]:
    """数值四舍五入辅助函数，规避浮点数二进制微小误差。"""
    if val is None:
        return None
    # 增加微小偏移使浮点数 .xxxx5 稳定符合数学四舍五入
    offset = 1e-9 if val >= 0 else -1e-9
    return round(val + offset, digits)


def compute_scores(
    tasks: Sequence[Dict[str, Any]],
    token_collected: bool = True,
) -> Dict[str, Any]:
    """纯函数：依据评测任务明细与 token 采集标志计算全场得分指标。

    返回 dict：composite、correctness、time_score、token_score、efficiency、token_collected、by_task/tasks。
    """
    by_task: Dict[str, Dict[str, Any]] = {}

    total_weight = 0
    earned_weight = 0.0  # Σ(权重 × 得分比例)

    # 临时收集有得分题目的加权得分；平均时的权重 = 题目权重 × 得分比例
    passed_time_items: List[Tuple[float, float]] = []   # (score, weight)
    passed_token_items: List[Tuple[float, float]] = []  # (score, weight)

    for task in tasks:
        tid = str(task.get("id") or "")
        diff = str(task.get("difficulty") or "easy")
        weight = int(task.get("weight") or DIFFICULTY_WEIGHTS.get(diff, 1))
        credit = compute_task_credit(task)

        total_weight += weight
        earned_weight += weight * credit

        # 1. 计算比值 r 与单题时间得分
        elapsed_s = task.get("elapsed_s")
        ref_minutes = task.get("ref_minutes")
        r: Optional[float] = None
        if elapsed_s is not None and ref_minutes is not None and ref_minutes > 0:
            r = float(elapsed_s) / (float(ref_minutes) * 60.0)

        # 2. 计算计费等价 token
        effective_tokens: Optional[float] = None
        if "effective_tokens" in task and task["effective_tokens"] is not None:
            effective_tokens = float(task["effective_tokens"])
        elif "tokens" in task and task["tokens"] is not None:
            tok_obj = task["tokens"]
            if isinstance(tok_obj, dict):
                effective_tokens = compute_effective_tokens(
                    input_tokens=tok_obj.get("input_tokens", 0),
                    output_tokens=tok_obj.get("output_tokens", 0),
                    cache_read_tokens=tok_obj.get("cache_read_tokens", 0),
                    cache_write_tokens=tok_obj.get("cache_write_tokens", 0),
                )
            else:
                effective_tokens = compute_effective_tokens(
                    input_tokens=getattr(tok_obj, "input_tokens", 0),
                    output_tokens=getattr(tok_obj, "output_tokens", 0),
                    cache_read_tokens=getattr(tok_obj, "cache_read_tokens", 0),
                    cache_write_tokens=getattr(tok_obj, "cache_write_tokens", 0),
                )

        # 3. 单题得分：得分为 0 的题不计入时间分与 token 分；
        #    拿部分分的长任务按"权重 × 得分比例"参与平均，做对得越少，快慢的影响越小
        if credit > 0:
            time_score = compute_time_score(r)
            token_score = compute_token_score(effective_tokens, diff) if token_collected else None

            if time_score is not None:
                passed_time_items.append((time_score, weight * credit))
            if token_collected and token_score is not None:
                passed_token_items.append((token_score, weight * credit))
        else:
            time_score = None
            token_score = None

        detail = {
            "weight": weight,
            "credit": round(credit, 4),
            "r": round(r, 4) if r is not None else None,
            "time_score": round(time_score, 4) if time_score is not None else None,
            "effective_tokens": round(effective_tokens, 1) if effective_tokens is not None else None,
            "token_score": round(token_score, 4) if token_score is not None else None,
        }
        if tid:
            by_task[tid] = detail

    # 4. 正确性分 = 100 * Σ(权重 × 得分比例) / Σ全部题权重
    if total_weight == 0:
        correctness = 0.0
    else:
        correctness = 100.0 * earned_weight / float(total_weight)

    # 5. 零得分特殊处理：正确性分 0、综合分 0，时间分和 token 分为 None，效率系数为 None
    if earned_weight <= 0:
        return {
            "composite": 0.0,
            "correctness": 0.0,
            "time_score": None,
            "token_score": None,
            "efficiency": None,
            "token_collected": token_collected,
            "by_task": by_task,
            "tasks": by_task,
        }

    # 6. 时间分加权平均（只按通过且有耗时的题）
    time_score_avg: Optional[float] = None
    if passed_time_items:
        time_sum = sum(score * w for score, w in passed_time_items)
        time_w = sum(w for _, w in passed_time_items)
        time_score_avg = time_sum / float(time_w) if time_w > 0 else None

    # 7. token 分加权平均（只按通过且有 token 数据的题）
    token_score_avg: Optional[float] = None
    if token_collected and passed_token_items:
        tok_sum = sum(score * w for score, w in passed_token_items)
        tok_w = sum(w for _, w in passed_token_items)
        token_score_avg = tok_sum / float(tok_w) if tok_w > 0 else None

    # 8. 效率系数计算
    # 有 token 分时：0.75 + 0.15 * 时间分 + 0.10 * token 分
    # token 未采集时：0.75 + 0.25 * 时间分
    efficiency: Optional[float] = None
    if time_score_avg is not None:
        if token_collected and token_score_avg is not None:
            efficiency = 0.75 + 0.15 * time_score_avg + 0.10 * token_score_avg
        else:
            efficiency = 0.75 + 0.25 * time_score_avg
    elif token_collected and token_score_avg is not None:
        efficiency = 0.75 + 0.25 * token_score_avg
    else:
        # 有题做对但耗时和 token 都缺失：按效率系数下限计，不能因为缺数据把正确性清零
        efficiency = 0.75

    # 9. 综合分 = 正确性分 * 效率系数
    composite = correctness * efficiency

    return {
        "composite": _round_val(composite, 4),
        "correctness": _round_val(correctness, 4),
        "time_score": _round_val(time_score_avg, 4),
        "token_score": _round_val(token_score_avg, 4),
        "efficiency": _round_val(efficiency, 4),
        "token_collected": token_collected,
        "by_task": by_task,
        "tasks": by_task,
    }
