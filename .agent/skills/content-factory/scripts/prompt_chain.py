#!/usr/bin/env python3
"""Three-stage prompt chain SOP with FuzzyVariables for Content Factory.

Stage 1: Data In (Anchor facts from BUSINESS-SOT.md + customer quotes)
Stage 2: HookGen (Batch generate 10 hooks: suspense, counter-intuitive, pain-point, etc.)
Stage 3: De-grease & Humanize (Strip buzzwords, inject random emotions and colloquial fillers)
"""

import argparse
import random
import re
import sys
from pathlib import Path

# Common buzzwords & AI grease to eliminate
DEFAULT_FORBIDDEN_WORDS = [
    "赋能", "一站式", "扬帆起航", "在充满挑战的时代", "助力全方位",
    "开启崭新篇章", "为您保驾护航", "领航者", "闭环赋能", "颠覆性",
    "引领行业", "毋庸置疑", "众所周知", "显而易见", "值得一提的是",
    "delve", "tapestry", "revolutionize", "beacon", "game-changer",
    "in today's fast-paced world", "testament", "seamlessly"
]

# Fuzzy variables: random emotions and conversational fillers to break AI monotony
EMOTION_TAGS = [
    "踩坑避雷后的恍然大悟",
    "实测验证后的理性克制",
    "面对同行内卷的无奈吐槽",
    "发现突破点后的兴奋分享",
    "作为一线从业者的真诚复盘"
]

COLLOQUIAL_FILLERS_ZH = [
    "说实话", "讲真", "踩过3次坑才发现", "谁懂啊",
    "内部实测了很久才敢发", "之前一直以为", "其实底层逻辑很简单"
]

COLLOQUIAL_FILLERS_EN = [
    "To be honest", "Here is what actually happened:", "After failing 3 times, we realized:",
    "Most advice online gets this backwards:", "A quick reality check:"
]


def inject_fuzzy_variables(lang: str = "zh") -> dict:
    """Pick randomized human emotional and tone variables to counter AI detection."""
    emotion = random.choice(EMOTION_TAGS)
    filler = random.choice(COLLOQUIAL_FILLERS_ZH if lang == "zh" else COLLOQUIAL_FILLERS_EN)
    return {
        "emotion": emotion,
        "filler": filler
    }


def scan_for_grease(text: str, custom_forbidden: list[str] = None) -> list[str]:
    """Scan draft for banned buzzwords and return violations."""
    banned = DEFAULT_FORBIDDEN_WORDS + (custom_forbidden or [])
    found = []
    for word in banned:
        if word.lower() in text.lower():
            found.append(word)
    return found


def format_stage1_prompt(topic: str, sot_excerpt: str, quotes: str = "") -> str:
    return f"""### 【节点 1：定词与事实锚定 (Data In)】
请基于以下【底层事实】与【用户原声】，梳理出本期内容的核心论据骨架。
严禁虚构任何未经核验的功能、参数或商业承诺！

【选题目标】：{topic}
【底层事实 (来自 BUSINESS-SOT.md)】：
{sot_excerpt}

【真实用户痛点/原声引用】：
{quotes or "（暂无额外引用，严格遵循底层事实）"}

请输出：
1. 核心论点（一句话结论）
2. 3个关键支撑论据（事实/对比/数据）
3. 对应的受众痛点场景
"""


def get_proven_hooks() -> str:
    """Read proven hooks from content/memory.md to provide few-shot inspiration."""
    try:
        repo_root = Path(__file__).resolve().parents[4]
        memory_path = repo_root / "content" / "memory.md"
        if not memory_path.exists():
            return ""
        text = memory_path.read_text(encoding="utf-8")
        if "## 1. Proven Winning Hooks" in text:
            section = text.split("## 1. Proven Winning Hooks")[1].split("## 2.")[0].strip()
            return section[:600]
    except Exception as e:
        pass
    return ""


def format_stage2_hook_prompt(stage1_summary: str, platform: str) -> str:
    few_shots = get_proven_hooks()
    few_shot_block = f"\n【参考历史实战跑赢的黄金钩子 (来自 memory.md Few-Shot)】：\n{few_shots}\n" if few_shots else ""
    return f"""### 【节点 2：批量造钩子 (HookGen)】
基于节点 1 的核心论点：
{stage1_summary}
{few_shot_block}
针对平台【{platform}】，请批量生成 10 个具有极强停留率与点击率的 Hook（标题/前两行）：
- 3 个【痛点反常识型】：打破常规认知，指出常见做法的缺陷。
- 3 个【强烈结果/反差型】：用具体可衡量的数据或前后对比吸引注意。
- 2 个【悬念/故事型】：从真实踩坑或意外经历切入。
- 2 个【干货清单型】：明确交付物价值，降低学习门槛。

要求：口语化、接地气、拒绝正确的废话！吸收历史黄金钩子的开口结构，但严禁抄袭内容！
"""


def format_stage3_degrease_prompt(draft: str, platform: str, lang: str = "zh") -> str:
    fuzzy = inject_fuzzy_variables(lang)
    forbidden_list = "、".join(DEFAULT_FORBIDDEN_WORDS[:12])
    return f"""### 【节点 3：去油自检与人类瑕疵感注入 (De-grease)】
针对平台【{platform}】，对初稿进行终审重写：

【模糊变量注入】：
- 语气基调：以【{fuzzy['emotion']}】的心态展开表达。
- 开头口语垫词：自然融入类似“【{fuzzy['filler']}】”的人声连接。

【强行去油与去爹味铁律】：
1. 严禁出现以下空洞商业词汇：{forbidden_list}。
2. 强制使用第一人称（“我”、“我们”、“咱”），严禁使用高高在上的指导式说教。
3. 增加短句节奏，加入真实的细节描述。

【待去油初稿】：
{draft}
"""


def main():
    parser = argparse.ArgumentParser(description="Prompt Chain & De-grease Helper")
    parser.add_argument("--check-text", help="Check given text for banned buzzwords")
    parser.add_argument("--fuzzy", action="store_true", help="Generate random fuzzy variables")
    args = parser.parse_args()

    if args.fuzzy:
        f_zh = inject_fuzzy_variables("zh")
        f_en = inject_fuzzy_variables("en")
        print(f"[ZH Fuzzy] Emotion: {f_zh['emotion']} | Filler: {f_zh['filler']}")
        print(f"[EN Fuzzy] Emotion: {f_en['emotion']} | Filler: {f_en['filler']}")

    if args.check_text:
        violations = scan_for_grease(args.check_text)
        if violations:
            print(f"[GREASE DETECTED] Found {len(violations)} banned phrases: {violations}")
            sys.exit(1)
        else:
            print("[CLEAN] No banned buzzwords detected.")


if __name__ == "__main__":
    main()
