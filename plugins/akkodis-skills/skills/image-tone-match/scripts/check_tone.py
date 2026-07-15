#!/usr/bin/env python3
"""
check_tone.py — 画像の L(明度)中央値とハイライトクリッピング率を算出する
スタンドアロンのチェッカー。

color_match.py の補正ロジックには一切手を触れない独立ツール。撮影・書き出し
後の素材が「明るすぎ/暗すぎ」「白飛びしていないか」を素早く一覧で確認するために使う。

算出する指標（定義は color_match.py --check と同じ）:
  - L中央値      : CIELAB の L チャンネルの中央値(パーセンタイル50, 0..100)。
                   露出の目安。値が大きいほど明るい。
  - ハイライト   : L がしきい値(既定97)を超える画素の割合[%]。
    クリッピング率  白飛び(ハイライトの階調が失われている領域)の量の目安。

入力: 画像ファイルパス（複数可）またはフォルダ。
出力: 各画像の L中央値 / ハイライトクリッピング率(%) を標準出力の表、
      または --csv でCSVとして出力。
"""

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

try:
    from skimage.color import rgb2lab
except Exception as exc:  # pragma: no cover
    sys.stderr.write(
        "scikit-image が必要です。次でインストールしてください:\n"
        "  pip install scikit-image --break-system-packages\n"
        f"(import エラー: {exc})\n"
    )
    sys.exit(2)

# color_match.py と同じ対応拡張子。
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

# 白飛び判定の既定しきい値。color_match.py の --check(blown_pct) と一致。
DEFAULT_HIGHLIGHT_THRESHOLD = 97.0


def load_L(path):
    """画像を読み込み CIELAB の L チャンネル(0..100)を返す。

    color_match.py の load_rgb と同じく EXIF の回転を反映してから統計を取る。
    アルファ付き画像は RGB に落として評価する（明度指標に透明度は使わない）。
    """
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)  # 統計を取る前にカメラの回転を反映
    im = im.convert("RGB")
    rgb = np.asarray(im, dtype=np.float64) / 255.0
    lab = rgb2lab(rgb)
    return lab[..., 0]


def tone_metrics(L, highlight_threshold):
    """L中央値とハイライトクリッピング率(%)を返す。"""
    l_median = float(np.percentile(L, 50))
    highlight_pct = float(np.mean(L > highlight_threshold) * 100.0)
    return l_median, highlight_pct


def collect_inputs(paths):
    """ファイル/フォルダの混在を、対象画像ファイルの一覧に展開する。"""
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files += sorted(q for q in p.iterdir() if q.suffix.lower() in IMG_EXTS)
        elif p.is_file():
            files.append(p)
        else:
            sys.stderr.write(f"警告: 見つからないためスキップ: {p}\n")
    return files


def build_parser():
    ap = argparse.ArgumentParser(
        description="画像の L(明度)中央値とハイライトクリッピング率(%)を算出する。"
    )
    ap.add_argument("inputs", nargs="+",
                    help="評価対象の画像ファイルまたはフォルダ（複数可）。")
    ap.add_argument("--highlight-threshold", type=float,
                    default=DEFAULT_HIGHLIGHT_THRESHOLD,
                    help=f"白飛び判定のLしきい値(0..100)。これを超える画素をクリッピングとみなす。"
                         f"既定 {DEFAULT_HIGHLIGHT_THRESHOLD:.0f}（color_match.py --check と同じ）。")
    ap.add_argument("--csv", action="store_true",
                    help="結果をCSV形式で出力する（既定は読みやすい表）。")
    ap.add_argument("--csv-out", metavar="FILE", default=None,
                    help="結果をCSVファイルへ書き出す（--csv 相当のヘッダ付き）。")
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    files = collect_inputs(args.inputs)
    if not files:
        sys.stderr.write("入力画像が指定されていません。\n")
        return 1

    header = ["file", "L_median", "highlight_clip_pct"]
    rows = []
    errors = 0
    for f in files:
        try:
            L = load_L(f)
            l_median, highlight_pct = tone_metrics(L, args.highlight_threshold)
            rows.append([str(f), f"{l_median:.2f}", f"{highlight_pct:.2f}"])
        except Exception as exc:
            sys.stderr.write(f"エラー {Path(f).name}: {exc}\n")
            errors += 1

    # CSVファイルへの書き出し（指定時）。
    if args.csv_out:
        with open(args.csv_out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
        sys.stderr.write(f"CSVを書き出しました: {args.csv_out}\n")

    # 標準出力: --csv ならCSV、そうでなければ整形した表。
    if args.csv:
        w = csv.writer(sys.stdout)
        w.writerow(header)
        w.writerows(rows)
    else:
        print(f"{'file':<40} {'L中央値':>10} {'ハイライト白飛び%':>16}")
        print("-" * 68)
        for path_str, l_median, highlight_pct in rows:
            name = Path(path_str).name
            name = name if len(name) <= 40 else name[:37] + "..."
            print(f"{name:<40} {l_median:>10} {highlight_pct:>16}")
        print(f"\nしきい値: L > {args.highlight_threshold:.0f} をハイライトクリッピングとみなす。")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
