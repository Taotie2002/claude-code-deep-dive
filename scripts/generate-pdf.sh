#!/bin/bash
# PDF生成脚本 - Claude Code Deep Dive v2.2
# 依赖: Pandoc, WeasyPrint, Noto字体

set -e

WORKSPACE="/home/zyu/.openclaw/workspaces/Main/claude-code-教科书"
OUTPUT_DIR="$WORKSPACE/assets"
MAIN_DOC="$WORKSPACE/claude-code-deep-dive.md"
TEMPLATE="$WORKSPACE/scripts/pdf-template.html"
TEMP_DIR="/tmp/pdf-gen-claude"

# 创建临时目录
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "  Claude Code Deep Dive - PDF生成"
echo "=========================================="
echo "输入: $MAIN_DOC"
echo "输出: $OUTPUT_DIR/claude-code-deep-dive.pdf"
echo ""

# Step 1: Markdown → HTML
echo "[1/4] Markdown → HTML..."
/tmp/pandoc-3.1.13/bin/pandoc "$MAIN_DOC" \
    -o "$TEMP_DIR/content.html" \
    --standalone \
    --metadata title="Claude Code Deep Dive" \
    --toc --toc-depth=2 \
    -s 2>/dev/null

# Step 2: 预处理HTML
echo "[2/4] 预处理HTML（修复emoji等）..."
python3 - << 'PYTHON_END'
import re
import os

temp_dir = "/tmp/pdf-gen-claude"

with open(f"{temp_dir}/content.html", 'r', encoding='utf-8') as f:
    content = f.read()

# 替换emoji为文字描述
emoji_map = {
    '✅': '[OK]', '❌': '[X]', '⚠️': '[!]', '🔴': '[P0]',
    '🟡': '[P1]', '🟢': '[L1]', '🔵': '[L3]', '⚪': '[L4]',
    '💰': '[Finance]', '🐕': '[Audit]', '✍️': '[Writer]',
    '🐴': '[Coder]', '🧙': '[Planner]', '⭐': '*',
    '📊': '[Chart]', '🚀': '->', '🔗': '[Link]',
    '🏛️': '', '🔧': '', '🔮': '', '🔑': '',
}

for emoji, replacement in emoji_map.items():
    content = content.replace(emoji, replacement)

with open(f"{temp_dir}/content.html", 'w', encoding='utf-8') as f:
    f.write(content)

print("  Emoji和特殊字符已替换")
PYTHON_END

# Step 3: HTML → PDF
echo "[3/4] HTML → PDF (WeasyPrint)..."
python3 - << 'PYTHON_END'
import os

temp_dir = "/tmp/pdf-gen-claude"
workspace = "/home/zyu/.openclaw/workspaces/Main/claude-code-教科书"

try:
    from weasyprint import HTML, CSS
    
    # 加载CSS
    with open(f"{workspace}/scripts/pdf-template.html", 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # 加载HTML
    with open(f"{temp_dir}/content.html", 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 生成PDF
    output_path = f"{workspace}/assets/claude-code-deep-dive.pdf"
    
    HTML(string=html_content).write_pdf(
        output_path,
        stylesheets=[CSS(string=css_content)],
        presentational_hints=True
    )
    
    size = os.path.getsize(output_path) / 1024 / 1024
    print(f"  PDF生成成功! ({size:.1f} MB)")
    
except Exception as e:
    print(f"  错误: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_END

# Step 4: 清理
echo "[4/4] 清理临时文件..."
rm -rf "$TEMP_DIR"

echo ""
echo "=========================================="
echo "  ✅ PDF生成完成!"
echo "=========================================="
ls -lh "$OUTPUT_DIR/claude-code-deep-dive.pdf"
