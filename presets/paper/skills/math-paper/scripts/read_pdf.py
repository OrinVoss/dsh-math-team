#!/usr/bin/env python3
"""PDF 双通道读取：文本提取 + 每页渲染成 PNG。

用法:
    uv run --with pypdf --with pymupdf python read_pdf.py <input.pdf> <outdir> [dpi]

输出:
    <outdir>/<pdf名>.txt        # 文本通道（pypdf 提取，便于检索/复制/逐字核对）
    <outdir>/page_01.png ...    # 图像通道（pymupdf 渲染，默认 150 DPI）

为什么要双通道:
    - 文本通道：可检索、可复制、便于逐字核对数字与措辞；
    - 图像通道：保留公式、表格结构、上下标、图片与版式的原貌——这些正是
      文本提取最容易丢失或错乱的部分；
    - 两者应交叉对齐：发现不一致或明显缺漏时，以图像通道（原貌）为准，
      并在题目分析报告里记录差异。

依赖由 uv 临时安装，不污染系统环境。
"""

import os
import sys


def extract_text(src: str, dst: str) -> int:
    """文本通道：提取每页文字，写入 txt。"""
    from pypdf import PdfReader

    reader = PdfReader(src)
    parts = []
    for i, page in enumerate(reader.pages, 1):
        parts.append(f"===== 第 {i} 页 =====")
        parts.append(page.extract_text() or "(无可提取文本)")
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))
    return len(reader.pages)


def render_pages(src: str, outdir: str, dpi: int) -> int:
    """图像通道：把每页渲染成 PNG。"""
    try:
        import pymupdf
    except ImportError:  # 兼容旧包名
        import fitz as pymupdf

    doc = pymupdf.open(src)
    total = len(doc)
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(dpi=dpi)
        pix.save(os.path.join(outdir, f"page_{i:02d}.png"))
    return total


def main() -> None:
    argv = [a for a in sys.argv[1:] if a.strip()]
    if len(argv) < 2:
        print(__doc__)
        sys.exit(2)

    src, outdir = argv[0], argv[1]
    dpi = int(argv[2]) if len(argv) > 2 else 150
    if not os.path.isfile(src):
        print(f"[错误] 找不到 PDF：{src}")
        sys.exit(1)

    os.makedirs(outdir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(src))[0]
    txt_path = os.path.join(outdir, f"{stem}.txt")

    n_text = extract_text(src, txt_path)
    print(f"[文本通道] {n_text} 页 -> {txt_path}")

    n_img = render_pages(src, outdir, dpi)
    print(f"[图像通道] {n_img} 页 -> {outdir}{os.sep}page_01.png ... (dpi={dpi})")

    print("提示：两个通道请交叉对齐核对；冲突或明显缺漏时以图像通道为准。")


if __name__ == "__main__":
    main()
