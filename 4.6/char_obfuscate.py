#!/usr/bin/env python3
"""char_obfuscate.py - G1 字符级混淆工具

应用三种技术：
  A1: 同形字替换 (Homoglyph substitution) - 用西里尔/希腊字母替换拉丁字母
  A2: 零宽字符插入 (Zero-Width Character insertion) - 在关键词内插入不可见字符
  A4: Leetspeak 替换 - 数字替换字母（仅在描述文本中，不影响代码执行）

目标：破坏关键词匹配，同时保持人类可读性和恶意语义。
"""
import os
import re
import shutil
import sys
from pathlib import Path

# ──────────────────────────────────────────────
# A1: 同形字映射表（拉丁→西里尔/希腊，视觉相同）
# ──────────────────────────────────────────────
HOMOGLYPHS = {
    # 西里尔字母替换拉丁字母
    'a': 'а',  # U+0430 CYRILLIC SMALL LETTER A
    'c': 'с',  # U+0441 CYRILLIC SMALL LETTER ES
    'e': 'е',  # U+0435 CYRILLIC SMALL LETTER IE
    'o': 'о',  # U+043E CYRILLIC SMALL LETTER O
    'p': 'р',  # U+0440 CYRILLIC SMALL LETTER ER
    'x': 'х',  # U+0445 CYRILLIC SMALL LETTER HA
    'y': 'у',  # U+0443 CYRILLIC SMALL LETTER U
    'A': 'А',  # U+0410 CYRILLIC CAPITAL LETTER A
    'B': 'В',  # U+0412 CYRILLIC CAPITAL LETTER VE
    'C': 'С',  # U+0421 CYRILLIC CAPITAL LETTER ES
    'E': 'Е',  # U+0415 CYRILLIC CAPITAL LETTER IE
    'H': 'Н',  # U+041D CYRILLIC CAPITAL LETTER EN
    'K': 'К',  # U+041A CYRILLIC CAPITAL LETTER KA
    'M': 'М',  # U+041C CYRILLIC CAPITAL LETTER EM
    'O': 'О',  # U+041E CYRILLIC CAPITAL LETTER O
    'P': 'Р',  # U+0420 CYRILLIC CAPITAL LETTER ER
    'T': 'Т',  # U+0422 CYRILLIC CAPITAL LETTER TE
    'X': 'Х',  # U+0425 CYRILLIC CAPITAL LETTER HA
    'Y': 'У',  # U+0423 CYRILLIC CAPITAL LETTER U
}

# 在关键词中应用同形字替换的目标词（仅替换敏感词中的字母）
HOMOGLYPH_TARGETS = [
    'curl', 'wget', 'bash', 'exec', 'eval',
    'credential', 'credentials', 'secret', 'secrets',
    'token', 'password', 'exfil', 'exfiltrate',
    'malicious', 'payload', 'inject', 'hack',
    'steal', 'upload', 'send', 'post', 'api',
    'audit', 'compliance', 'scan', 'collect',
    'harvest', 'capture', 'extract', 'gather',
]

# ──────────────────────────────────────────────
# A2: 零宽字符插入配置
# ──────────────────────────────────────────────
ZWC_CHARS = [
    '\u200B',  # ZERO WIDTH SPACE
    '\u200C',  # ZERO WIDTH NON-JOINER
    '\u200D',  # ZERO WIDTH JOINER
    '\uFEFF',  # ZERO WIDTH NO-BREAK SPACE
]

# 在这些关键词内插入零宽字符
ZWC_TARGETS = [
    'curl', 'credential', 'secret', 'token', 'password',
    'exfil', 'audit', 'collect', 'backup', 'sync',
    'upload', 'send', 'post', 'analytics', 'tracking',
    'harvest', 'extract', 'capture', 'gather', 'steal',
    'malicious', 'payload', 'bash', 'eval', 'exec',
    'compliance', 'scan', 'api', 'key', 'auth',
]

# ──────────────────────────────────────────────
# A4: Leetspeak 映射（用于描述性文本，非代码）
# ──────────────────────────────────────────────
LEET_MAP = {
    'a': '4', 'e': '3', 'i': '1', 'o': '0',
    's': '5', 't': '7', 'g': '9', 'l': '1',
}

LEET_TARGETS = [
    'exfiltrate', 'exfil', 'steal', 'hack', 'malicious',
    'payload', 'exploit', 'attack', 'inject', 'hijack',
]


def apply_homoglyph_to_word(word: str) -> str:
    """将单词中的第一个或第二个字母替换为同形字（保持其余不变）"""
    result = list(word)
    replaced = 0
    for i, ch in enumerate(result):
        if ch in HOMOGLYPHS and replaced < 2:
            result[i] = HOMOGLYPHS[ch]
            replaced += 1
            if replaced >= 2:
                break
    return ''.join(result)


def apply_homoglyphs(text: str) -> str:
    """在文本中找到目标词并替换同形字"""
    def replace_match(m):
        word = m.group(0)
        lower = word.lower()
        if lower in HOMOGLYPH_TARGETS:
            return apply_homoglyph_to_word(word)
        return word

    pattern = r'\b(' + '|'.join(re.escape(t) for t in HOMOGLYPH_TARGETS) + r')\b'
    return re.sub(pattern, replace_match, text, flags=re.IGNORECASE)


def insert_zwc(word: str, zwc: str = '\u200B') -> str:
    """在单词中间插入零宽字符（在第2个字母后）"""
    if len(word) <= 3:
        return word
    mid = len(word) // 2
    return word[:mid] + zwc + word[mid:]


def apply_zwc(text: str) -> str:
    """在文本中找到目标词并插入零宽字符"""
    import random
    rng = random.Random(42)  # 固定种子保证可重复

    def replace_match(m):
        word = m.group(0)
        zwc = rng.choice(ZWC_CHARS)
        return insert_zwc(word, zwc)

    pattern = r'\b(' + '|'.join(re.escape(t) for t in ZWC_TARGETS) + r')\b'
    return re.sub(pattern, replace_match, text, flags=re.IGNORECASE)


def apply_leet(text: str) -> str:
    """对目标词应用Leetspeak替换"""
    def leetify(word: str) -> str:
        result = []
        for ch in word:
            result.append(LEET_MAP.get(ch.lower(), ch))
        return ''.join(result)

    def replace_match(m):
        return leetify(m.group(0))

    pattern = r'\b(' + '|'.join(re.escape(t) for t in LEET_TARGETS) + r')\b'
    return re.sub(pattern, replace_match, text, flags=re.IGNORECASE)


def is_code_line(line: str) -> bool:
    """判断是否是代码行（在代码块内，或以特殊字符开头）"""
    stripped = line.strip()
    return (
        stripped.startswith('```') or
        stripped.startswith('    ') or
        stripped.startswith('\t') or
        stripped.startswith('#!') or
        stripped.startswith('$') or
        stripped.startswith('>>>') or
        '=' in stripped[:20] and not stripped.startswith('-') or
        stripped.startswith('import ') or
        stripped.startswith('from ') or
        stripped.startswith('def ') or
        stripped.startswith('curl ') or
        stripped.startswith('wget ')
    )


def obfuscate_skill_md(content: str) -> str:
    """
    对 SKILL.md 内容应用字符级混淆：
    - 在代码块外的描述文本中应用 A1（同形字）和 A2（零宽字符）
    - 对特定恶意词汇应用 A4（Leetspeak），仅在描述文本中
    - 不修改代码块内的可执行代码（避免破坏功能）
    """
    lines = content.split('\n')
    in_code_block = False
    result_lines = []

    for line in lines:
        # 检测代码块边界
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue

        if in_code_block:
            # 代码块内只做同形字替换（影响关键词匹配但不破坏语法）
            # 只替换注释中的词（以 # 开头的部分）
            if '#' in line:
                code_part, _, comment = line.partition('#')
                comment_obfuscated = apply_homoglyphs(comment)
                comment_obfuscated = apply_zwc(comment_obfuscated)
                result_lines.append(code_part + '#' + comment_obfuscated)
            else:
                result_lines.append(line)
        else:
            # 描述文本：应用全部三种混淆
            obfuscated = apply_homoglyphs(line)
            obfuscated = apply_zwc(obfuscated)
            # A4 仅用于明显的恶意词汇（不太可能出现在正常描述中）
            # obfuscated = apply_leet(obfuscated)  # 暂时不启用，可读性影响较大
            result_lines.append(obfuscated)

    return '\n'.join(result_lines)


def process_skill_dir(src_dir: Path, dst_dir: Path):
    """处理一个skill目录：复制所有文件，对SKILL.md应用混淆"""
    dst_dir.mkdir(parents=True, exist_ok=True)

    for item in src_dir.iterdir():
        if item.is_file():
            dst_path = dst_dir / item.name
            if item.name == 'SKILL.md':
                content = item.read_text(encoding='utf-8')
                obfuscated = obfuscate_skill_md(content)
                dst_path.write_text(obfuscated, encoding='utf-8')
                print(f"  [A1+A2] {item.name} → obfuscated")
            else:
                shutil.copy2(item, dst_path)
                print(f"  [copy]  {item.name}")
        elif item.is_dir():
            shutil.copytree(item, dst_dir / item.name, dirs_exist_ok=True)
            print(f"  [copy]  {item.name}/")


def main():
    benchmark_dir = Path("/Users/tan/Desktop/RA3/3.24/benchmark/malicious")

    cases = [f"AP{i:02d}" for i in range(1, 13)]

    for case in cases:
        src = benchmark_dir / f"{case}_orig"
        dst = benchmark_dir / f"{case}_evade_g1"

        if not src.exists():
            print(f"[SKIP] {case}_orig not found")
            continue

        print(f"\n[G1] Processing {case}_orig → {case}_evade_g1")
        process_skill_dir(src, dst)

    print("\n✓ G1 字符级混淆完成，共处理 12 个 skill")


if __name__ == "__main__":
    main()
