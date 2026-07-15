#!/usr/bin/env python3
"""
color_match.py — 1枚の基準画像の「見た目」に合わせて、
1〜複数枚の画像の 明度 / 彩度 / 色調（ホワイトバランス）を揃える。
 
中核の考え方（CIELAB 統計転送 / Reinhard et al. 2001）:
  入力画像と基準画像を CIELAB に変換し、チャンネルごとに、入力の平均・標準偏差が
  基準と一致するよう再スケールする。L は明度とコントラスト、a/b の平均は
  ホワイトバランス/色被り（色調）、a/b の広がり（彩度=chroma）は彩度を担う。
  3つを一括で合わせる方式は堅牢で、構造保存的（ピクセルの空間情報は変えず、
  色統計だけを動かす）。
 
手法は2つ:
  - lab-moments（既定）: L, a, b の平均+標準偏差を一括マッチ。万能・基本。
  - axes: 軸別に独立制御 — 明度(L) / ホワイトバランス(a,b平均, 色相回転なし) /
    彩度(chroma)。各軸を個別にON/OFFできる。
 
グローバルな --strength（0..1）で、補正結果を元画像側へブレンドできる。
「7割だけ基準に寄せる」といった調整が可能（全補正＝1.0）。
 
これは「統計マッチ」であって「意味を理解したグレーディング」ではない。入力が基準と
内容的に近いほどうまくいく（例: コーポレートの人物基準なら人物/内装の写真）。
内容が大きく異なる素材（白背景の製品・スクショ・屋外風景など）は破綻し得るので、
その場合は --strength を下げる、axes の彩度OFF、あるいは別の基準画像を使う。
"""
 
import argparse
import json
import sys
from pathlib import Path
 
import numpy as np
from PIL import Image, ImageOps
 
try:
    from skimage.color import rgb2lab, lab2rgb
except Exception as exc:  # pragma: no cover
    sys.stderr.write(
        "scikit-image が必要です。次でインストールしてください:\n"
        "  pip install scikit-image --break-system-packages\n"
        f"(import エラー: {exc})\n"
    )
    sys.exit(2)
 
try:
    import cv2  # クラリティ/シャープのガウシアンに使用（任意）
    _HAS_CV2 = True
except Exception:
    _HAS_CV2 = False
 
AB_GAIN_CAP = (0.75, 1.35)  # a/b・彩度の倍率の下限/上限（顔色保護）
 
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
EPS = 1e-6
 
 
def _blur_L(L, sigma):
    """L(0..100)のガウシアンぼかし。cv2が無ければ簡易ボックス近似。"""
    if _HAS_CV2:
        return cv2.GaussianBlur(L.astype(np.float32), (0, 0), sigmaX=float(sigma),
                                borderType=cv2.BORDER_REFLECT).astype(np.float64)
    # フォールバック: 分離ボックスフィルタ3回でガウシアン近似
    import scipy.ndimage as ndi  # noqa
    return ndi.gaussian_filter(L, sigma=sigma, mode="reflect")
 
 
def _recover_highlights_L(L, amount, lo, hi):
    """ハイライト復元。明るい階調だけを引き下げて白飛び/眠さ(washed)を抑える。
 
    しきい値(正規化0.55)より上だけを圧縮し、中間調・黒点は不動。Lightroomの
    「ハイライト −」相当。amount=0 で無変化、1で上端を強く圧縮。
    """
    if amount <= 0 or hi - lo < 1.0:
        return L
    n = np.clip((L - lo) / (hi - lo), 0.0, 1.0)
    t = 0.72
    over = np.clip(n - t, 0.0, None)
    n2 = np.where(n > t, t + over * (1.0 - amount), n)
    return np.clip(n2 * (hi - lo) + lo, 0.0, 100.0)
 
 
def _fill_shadows_L(L, amount, lo, hi):
    """シャドウリフト(fill)。黒点(lo)とハイライトは保ち、暗部〜中間下部だけ持ち上げる。
 
    逆光・明るい背景で被写体(暗いスーツ等)が沈む構図向け。Lightroomの
    「シャドウ」スライダー相当。amount=0 で無変化。
    """
    if amount <= 0 or hi - lo < 1.0:
        return L
    n = np.clip((L - lo) / (hi - lo), 0.0, 1.0)
    bright = np.sqrt(n)                                   # 暗部を強く持ち上げる曲線
    w = np.clip(1.0 - n / 0.6, 0.0, 1.0) * np.clip(n / 0.05, 0.0, 1.0)  # 暗部~中下のみ・真黒は保護
    w = w * amount
    n2 = n * (1.0 - w) + bright * w
    return np.clip(n2 * (hi - lo) + lo, 0.0, 100.0)
 
 
def _clarity_L(L, amount, sigma):
    """ローカルコントラスト(クラリティ)。中間調中心に、黒白点と階調端は保護。
 
    detail = L - 大きめガウシアン。中間調マスクで端点付近の効果を弱め、
    黒浮き・ハイライトのハロを防ぐ。amount=0 で無変化。
    """
    if amount <= 0:
        return L
    detail = L - _blur_L(L, sigma)
    n = np.clip(L / 100.0, 0.0, 1.0)
    mask = 1.0 - (2.0 * n - 1.0) ** 2  # 中間調=1, 端=0
    return np.clip(L + amount * detail * mask, 0.0, 100.0)
 
 
def _s_curve_L(L, strength):
    """トーンカーブ(S字)。端点(0/100)固定でコントラストを付与。
 
    smoothstep へ寄せることで、暗部を締め・明部を伸ばしつつ端点で
    なだらかにロールオフ（フィルム的な肩/トウ）。strength=0 で無変化。
    """
    if strength <= 0:
        return L
    n = np.clip(L / 100.0, 0.0, 1.0)
    s = n * n * (3.0 - 2.0 * n)
    return np.clip((n + strength * (s - n)) * 100.0, 0.0, 100.0)
 
 
def _sharpen_L(L, amount, sigma=1.0):
    """出力用アンシャープ（Web表示の精細感）。amount=0 で無変化。"""
    if amount <= 0:
        return L
    return np.clip(L + amount * (L - _blur_L(L, sigma)), 0.0, 100.0)
 
 
def _vibrance_ab(a, b, amount):
    """肌色を保護したバイブランス。低彩度ほど強く持ち上げ、肌の色相は抑制。
 
    色相回転はしない（chroma の大きさだけを調整）。amount=0 で無変化。
    """
    if amount == 0:
        return a, b
    C = np.sqrt(a * a + b * b)
    h = np.arctan2(b, a)
    sat_n = np.clip(C / 40.0, 0.0, 1.0)            # おおよその正規化彩度
    boost = amount * (1.0 - sat_n)                  # 低彩度を優先して持ち上げ
    deg = (np.degrees(h)) % 360.0
    skin = np.exp(-(((deg - 30.0) / 25.0) ** 2))    # 肌(暖色~30°)付近を保護
    boost = boost * (1.0 - 0.7 * skin)
    C2 = np.clip(C * (1.0 + boost), 0.0, None)
    return C2 * np.cos(h), C2 * np.sin(h)
 
 
# --------------------------------------------------------------------------- #
# 入出力ヘルパー
# --------------------------------------------------------------------------- #
def load_rgb(path):
    """(rgb_float[H,W,3] 0..1, alpha[H,W] 0..1 または None) を返す。"""
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)  # 統計を取る前にカメラの回転を反映
    alpha = None
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        alpha = np.asarray(im.split()[-1], dtype=np.float64) / 255.0
        im = im.convert("RGB")
    else:
        im = im.convert("RGB")
    rgb = np.asarray(im, dtype=np.float64) / 255.0
    return rgb, alpha
 
 
def save_rgb(rgb, alpha, path, fmt, quality):
    arr = np.clip(rgb, 0.0, 1.0)
    arr8 = (arr * 255.0 + 0.5).astype(np.uint8)
    if alpha is not None:
        a8 = (np.clip(alpha, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
        out = Image.fromarray(np.dstack([arr8, a8]), mode="RGBA")
    else:
        out = Image.fromarray(arr8, mode="RGB")
 
    path = Path(path)
    fmt = (fmt or path.suffix.lstrip(".")).lower()
    if fmt in ("jpg", "jpeg"):
        if out.mode == "RGBA":
            out = out.convert("RGB")  # JPEG はアルファ非対応
        out.save(path, "JPEG", quality=quality, subsampling=0)
    elif fmt == "webp":
        out.save(path, "WEBP", quality=quality, method=6)
    elif fmt == "png":
        out.save(path, "PNG", optimize=True)
    else:
        out.save(path)
 
 
# --------------------------------------------------------------------------- #
# 統計量
# --------------------------------------------------------------------------- #
def lab_stats(lab):
    """各チャンネルの平均/標準偏差に加え、chroma平均/標準偏差とLパーセンタイル。"""
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.sqrt(a * a + b * b)
    p = np.percentile(L, [1, 50, 99])
    return {
        "L": {"mean": float(L.mean()), "std": float(L.std())},
        "a": {"mean": float(a.mean()), "std": float(a.std())},
        "b": {"mean": float(b.mean()), "std": float(b.std())},
        "chroma": {"mean": float(C.mean()), "std": float(C.std())},
        "L_pct": {"p1": float(p[0]), "p50": float(p[1]), "p99": float(p[2])},
    }
 
 
def describe_profile(s):
    """プロファイルを人間向けに短く説明する。"""
    warm = "暖色(黄)寄り" if s["b"]["mean"] > 2 else "寒色(青)寄り" if s["b"]["mean"] < -2 else "黄-青はニュートラル"
    tint = "マゼンタ寄り" if s["a"]["mean"] > 2 else "緑寄り" if s["a"]["mean"] < -2 else "緑-マゼンタはニュートラル"
    bright = "明るい" if s["L"]["mean"] > 70 else "暗い" if s["L"]["mean"] < 40 else "中明度"
    sat = "鮮やか" if s["chroma"]["mean"] > 30 else "くすみ(低彩度)" if s["chroma"]["mean"] < 12 else "中程度の彩度"
    return (
        f"L平均 {s['L']['mean']:.1f} ({bright})、"
        f"黒点L1≈{s['L_pct']['p1']:.1f}、"
        f"a平均 {s['a']['mean']:.1f} ({tint})、"
        f"b平均 {s['b']['mean']:.1f} ({warm})、"
        f"chroma平均 {s['chroma']['mean']:.1f} ({sat})。"
    )
 
 
def _moment(src, ref_mean, ref_std, clip_ratio, cap=None):
    """平均・広がりを基準へ合わせる。cap=(lo,hi) 指定時は倍率をその範囲に制限。
 
    a/b・彩度は cap を必ず使う: 白壁中心の低彩度シーンでは倍率が×2超になり
    肌の赤みが過増幅され（顔が赤く）、派手な背景では×0.6未満に圧縮され
    肌の血色が抜ける（顔色が悪くなる）ため。
    """
    s_mean, s_std = float(src.mean()), float(src.std())
    if s_std < EPS:
        return src - s_mean + ref_mean
    ratio = ref_std / s_std
    lo, hi = (1.0 / clip_ratio, clip_ratio) if cap is None else cap
    ratio = min(max(ratio, lo), hi)
    return (src - s_mean) * ratio + ref_mean
 
 
def _anchor_L(L, ref_lo, ref_hi, pts):
    """L の黒点/白点を基準に合わせる（レベル補正）。
 
    入力 L の下位/上位パーセンタイル(pts)を、基準の同じ点(ref_lo, ref_hi)へ
    線形写像する。平均マッチと違い「黒は黒・白は白」が保たれるので、
    暗部が浮く(milky/ヘイズ)現象を防ぐ。明るさを背景の白壁量に引きずられない
    ぶん、内容差にも頑健。
    """
    lo, hi = np.percentile(L, pts)
    span = hi - lo
    if span < 1.0:  # ほぼフラット: 中点合わせにフォールバック
        return L - (lo + hi) * 0.5 + (ref_lo + ref_hi) * 0.5
    gain = (ref_hi - ref_lo) / span
    return np.clip((L - lo) * gain + ref_lo, 0.0, 100.0)
 
 
def _converge_midtone(L, tgt_median, strength, lo, hi):
    """中間調(明るさ)を目標中央値へ寄せる。黒点(lo)と白点(hi)は固定点。
 
    [lo,hi] を 0..1 に正規化してガンマをかけるため、L=lo と L=hi は不動。
    つまり黒は浮かず白は飛ばさずに、中央値だけを tgt_median へ寄せられる。
    アンカーで端点を [lo,hi] に固定した「後」に適用すること。strength=0 で無変化。
    """
    if strength <= 0 or hi - lo < 1.0:
        return L
    n = np.clip((L - lo) / (hi - lo), 1e-4, 1.0)
    ms = (float(np.percentile(L, 50)) - lo) / (hi - lo)
    mt = (tgt_median - lo) / (hi - lo)
    if not (1e-3 < ms < 1 - 1e-3) or not (1e-3 < mt < 1 - 1e-3):
        return L
    g = np.log(mt) / np.log(ms)
    if mt <= ms:        # lift-only: 目標より明るい(良露出の)写真は暗くしない
        return L
    g = 1.0 + strength * (g - 1.0)
    return np.clip(np.power(n, g) * (hi - lo) + lo, 0.0, 100.0)
 
 
# --------------------------------------------------------------------------- #
# 手法（CIELAB の float 配列に対して動作）
# --------------------------------------------------------------------------- #
def method_lab_moments(src_lab, ref, clip_ratio, l_mode):
    out = src_lab.copy()
    if l_mode == "anchor":
        out[..., 0] = _anchor_L(src_lab[..., 0], ref["L_anchor"]["lo"],
                                ref["L_anchor"]["hi"], ref["L_anchor"]["pts"])
    else:
        out[..., 0] = _moment(src_lab[..., 0], ref["L"]["mean"], ref["L"]["std"], clip_ratio)
    for i, ch in ((1, "a"), (2, "b")):
        out[..., i] = _moment(src_lab[..., i], ref[ch]["mean"], ref[ch]["std"],
                              clip_ratio, cap=AB_GAIN_CAP)
    return out
 
 
def method_axes(src_lab, ref, clip_ratio, do_bright, do_wb, do_sat, sat_std, l_mode):
    out = src_lab.copy()
    L, a, b = out[..., 0], out[..., 1], out[..., 2]
 
    if do_bright:  # 明度 + コントラスト
        if l_mode == "anchor":
            L = _anchor_L(L, ref["L_anchor"]["lo"], ref["L_anchor"]["hi"], ref["L_anchor"]["pts"])
        else:
            L = _moment(L, ref["L"]["mean"], ref["L"]["std"], clip_ratio)
 
    if do_wb:  # 色調 / ホワイトバランス: ニュートラル点を移動、色相回転なし
        a = a - float(a.mean()) + ref["a"]["mean"]
        b = b - float(b.mean()) + ref["b"]["mean"]
 
    if do_sat:  # 彩度: 色相を保ったまま chroma を平均まわりでスケール
        C = np.sqrt(a * a + b * b)
        h = np.arctan2(b, a)
        if sat_std:
            C = _moment(C, ref["chroma"]["mean"], ref["chroma"]["std"], clip_ratio, cap=AB_GAIN_CAP)
        else:
            cm = float(C.mean())
            ratio = ref["chroma"]["mean"] / cm if cm > EPS else 1.0
            ratio = min(max(ratio, 1.0 / clip_ratio), clip_ratio)
            C = C * ratio
        C = np.clip(C, 0.0, None)
        a = C * np.cos(h)
        b = C * np.sin(h)
 
    out[..., 0], out[..., 1], out[..., 2] = L, a, b
    return out
 
 
# --------------------------------------------------------------------------- #
# 全体制御
# --------------------------------------------------------------------------- #
def process_one(src_path, out_path, ref_profile, args):
    rgb, alpha = load_rgb(src_path)
    src_lab = rgb2lab(rgb)
 
    if args.method == "lab-moments":
        matched = method_lab_moments(src_lab, ref_profile, args.clip_ratio, args.l_mode)
    elif args.method == "axes":
        matched = method_axes(
            src_lab, ref_profile, args.clip_ratio,
            do_bright=not args.no_brightness,
            do_wb=not args.no_white_balance,
            do_sat=not args.no_saturation,
            sat_std=args.saturation_std,
            l_mode=args.l_mode,
        )
    else:
        raise ValueError(args.method)
 
    # WB補正の強さ: マッチで適用された a/b の平均シフトを (1-w) だけ戻す
    if args.wb_strength < 1.0:
        w = max(0.0, args.wb_strength)
        matched[..., 1] += (1.0 - w) * (float(src_lab[..., 1].mean()) - ref_profile["a"]["mean"])
        matched[..., 2] += (1.0 - w) * (float(src_lab[..., 2].mean()) - ref_profile["b"]["mean"])
 
    # 中間調(明るさ)の収束: アンカーで固定した黒白点[lo,hi]を保ったまま中央値を目標へ。
    if getattr(args, "_midtone_strength", 0.0) > 0 and args._midtone_target is not None:
        la = ref_profile["L_anchor"]
        matched[..., 0] = _converge_midtone(matched[..., 0], args._midtone_target,
                                            args._midtone_strength, la["lo"], la["hi"])
 
    if args.strength < 1.0:
        matched = src_lab + args.strength * (matched - src_lab)
 
    # 彩度の寄せ具合: 合わせた色相/WBは保ったまま、chroma の大きさだけ
    # 元画像側へ戻す。L・コントラスト・WB（色相方向）には影響しない。
    if args.sat_strength < 1.0:
        src_C = np.sqrt(src_lab[..., 1] ** 2 + src_lab[..., 2] ** 2)
        m_a, m_b = matched[..., 1], matched[..., 2]
        m_C = np.sqrt(m_a ** 2 + m_b ** 2)
        m_h = np.arctan2(m_b, m_a)
        C_final = np.clip(m_C + (1.0 - args.sat_strength) * (src_C - m_C), 0.0, None)
        matched[..., 1] = C_final * np.cos(m_h)
        matched[..., 2] = C_final * np.sin(m_h)
 
    # 仕上げ（非破壊。画素を作り直さず、トーン/コントラスト/精細感だけを整える）
    la = ref_profile["L_anchor"]
    matched[..., 0] = _fill_shadows_L(matched[..., 0], args.fill, la["lo"], la["hi"])
    matched[..., 0] = _recover_highlights_L(matched[..., 0], args.highlights, la["lo"], la["hi"])
    sigma = max(8.0, (matched.shape[0] + matched.shape[1]) / 2.0 / 22.0)  # クラリティ半径は画像サイズ依存
    matched[..., 0] = _clarity_L(matched[..., 0], args.clarity, sigma)
    matched[..., 0] = _s_curve_L(matched[..., 0], args.contrast)
    if args.vibrance != 0:
        matched[..., 1], matched[..., 2] = _vibrance_ab(matched[..., 1], matched[..., 2], args.vibrance)
    matched[..., 0] = _sharpen_L(matched[..., 0], args.sharpen)
 
    out_rgb = lab2rgb(matched)
    save_rgb(out_rgb, alpha, out_path, args.format, args.quality)
 
    if args.print_stats:
        before = lab_stats(src_lab)
        after = lab_stats(rgb2lab(np.clip(out_rgb, 0, 1)))
        print(f"  {Path(src_path).name}")
        print(f"    補正前: {describe_profile(before)}")
        print(f"    補正後: {describe_profile(after)}")
    return out_path
 
 
def collect_inputs(paths):
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
        description="複数画像の 明度/彩度/色調 を基準画像に合わせて統一する。"
    )
    here = Path(__file__).resolve().parent.parent
    ap.add_argument("inputs", nargs="*", help="処理対象の画像ファイルまたはフォルダ。")
    ap.add_argument("--profile", default=str(here / "assets" / "neutral_profile.json"),
                    help="基準プロファイルJSON（既定=同梱の合成ニュートラル基準 neutral_profile.json）。"
                         "通常は変更不要。ハウス・トーンにしたい時だけ neutral_profile.json の数値を編集。")
    ap.add_argument("--check", action="store_true",
                    help="変換せず、撮影品質の検収だけ行う（WB色被り/黒/白飛び/露出/彩度を"
                         "assets/shooting_spec.json の閾値で PASS/WARN/FAIL 判定）。納品物の受入チェック用。")
    ap.add_argument("--wb-strength", type=float, default=0.7,
                    help="色被り(WB)補正の強さ 0..1。AKKODiS既定=0.7（背景の強い色被りで顔が青白くなる過補正を抑える）。"
                         "1.0で完全中立化。金色の壁・夕日など色被りが極端な外れ値だけ 0.5〜0.6 へさらに下げる。")
    ap.add_argument("--midtone-strength", type=float, default=None,
                    help="中間調(全体の明るさ)を目標へ寄せる強さ 0..1（lift-only=暗いカットだけ持ち上げ）。"
                         "既定 0.5。0 で明るさ非調整(色だけ基準に合わせる)。黒白点は固定なのでヘイズは出ない。")
    ap.add_argument("--midtone-target", type=float, default=None,
                    help="中間調の目標L値(0..100)。既定 62（バッチ非依存の固定値）。ハイキー画像の中央値に"
                         "明るさを合わせると washed になるため固定値を使う。もっと明るく/暗くは 66 / 56 等。")
    ap.add_argument("--out-dir", default="./toned", help="出力フォルダ。")
    ap.add_argument("--method", choices=["lab-moments", "axes"],
                    default="lab-moments",
                    help="マッチ手法。既定 lab-moments。")
    ap.add_argument("--strength", type=float, default=1.0,
                    help="0..1 で基準への寄せ具合をブレンド（既定 1.0=全補正）。全軸に効く。")
    ap.add_argument("--sat-strength", type=float, default=0.85,
                    help="0..1 で彩度だけの寄せ具合。既定0.85（基準の自然な彩度に寄せつつ元の質感を一部残す）。"
                         "色の濃い写真でくすむ時は下げる、もっと揃えたいなら 1.0。")
    # 仕上げ（非破壊。生成は使わない）
    ap.add_argument("--fill", type=float, default=0.15,
                    help="シャドウリフト。黒点は保ち暗部~中間下部だけ持ち上げる。既定0.15（軽め）。"
                         "逆光・明るい背景で被写体(黒スーツ等)が沈む写真は 0.3〜0.6、不要なら 0。")
    ap.add_argument("--highlights", type=float, default=0.0,
                    help="ハイライト復元。明るい階調だけ引き下げ、白飛び/眠さ(washed)を抑える。"
                         "0で無効(既定)。明るすぎ/眠いと感じたら 0.3〜0.6。")
    ap.add_argument("--clarity", type=float, default=0.12,
                    help="ローカルコントラスト(クラリティ)。中間調中心に立体感を付与。0で無効。既定0.12。"
                         "人物の肌のテカり/シワが強調されすぎる時は 0.05〜0.08 に下げる。")
    ap.add_argument("--contrast", type=float, default=0.10,
                    help="トーンカーブ(S字)の強さ。端点固定でメリハリ。0で無効。既定0.10。")
    ap.add_argument("--vibrance", type=float, default=0.0,
                    help="肌色保護つきの彩度持ち上げ。低彩度を優先。0で無効(既定)。くすみが気になる時 0.1〜0.2。")
    ap.add_argument("--sharpen", type=float, default=0.0,
                    help="出力アンシャープ(Web表示の精細感)。0で無効(既定)。掛けるなら 0.2〜0.4。")
    ap.add_argument("--clip-ratio", type=float, default=3.0,
                    help="チャンネルごとの最大スケール比。過補正を防ぐ（既定 3.0）。")
    # 明度(L)の合わせ方
    ap.add_argument("--l-mode", choices=["anchor", "moments"], default="anchor",
                    help="L の合わせ方。anchor=黒点/白点を基準に合わせる(既定・暗部の浮きを防ぐ)。"
                         "moments=平均+標準偏差マッチ(従来挙動)。")
    ap.add_argument("--anchor-lo", type=float, default=1.0,
                    help="[l-mode=anchor] 黒点に使う下位パーセンタイル（既定 1.0）。")
    ap.add_argument("--anchor-hi", type=float, default=99.0,
                    help="[l-mode=anchor] 白点に使う上位パーセンタイル（既定 99.0）。")
    # axes 手法のトグル
    ap.add_argument("--no-brightness", action="store_true", help="[axes] 明度/コントラストのマッチをしない。")
    ap.add_argument("--no-white-balance", action="store_true", help="[axes] ホワイトバランス/色被りのマッチをしない。")
    ap.add_argument("--no-saturation", action="store_true", help="[axes] 彩度のマッチをしない。")
    ap.add_argument("--saturation-std", action="store_true",
                    help="[axes] chroma の平均だけでなく標準偏差もマッチ（既定: 平均のみ）。")
    # 出力
    ap.add_argument("--format", default="webp", choices=["keep", "webp", "png", "jpg", "jpeg"],
                    help="出力形式。既定 webp に統一。png/jpg 等を指定すればそれに従う。keep で入力形式を維持。")
    ap.add_argument("--quality", type=int, default=92, help="JPEG/WebP の品質（既定 92）。")
    ap.add_argument("--suffix", default="_toned", help="ファイル名サフィックス（既定 _toned）。")
    ap.add_argument("--print-stats", action="store_true", help="画像ごとに補正前後の統計を表示。")
    return ap
 
 
def main(argv=None):
    args = build_parser().parse_args(argv)
 
    # 合わせる先は常に合成ニュートラル基準（同梱の固定プロファイルJSON）。画像基準は持たない。
    prof_path = args.profile or str(Path(__file__).resolve().parent.parent / "assets" / "neutral_profile.json")
    ref_profile = json.loads(Path(prof_path).read_text())
 
    files = collect_inputs(args.inputs)
 
    if args.check:
        spec_path = Path(__file__).resolve().parent.parent / "assets" / "shooting_spec.json"
        spec = json.loads(spec_path.read_text())
        def judge(v, rule):
            pa, wa = rule["pass"], rule["warn"]
            if isinstance(pa, list):
                if pa[0] <= v <= pa[1]: return "PASS"
                if wa[0] <= v <= wa[1]: return "WARN"
                return "FAIL"
            if v <= pa: return "PASS"
            if v <= wa: return "WARN"
            return "FAIL"
        order = ["wb_a_abs","wb_b_abs","black_p1","blown_pct","exposure_med","chroma_mean"]
        any_bad = False
        for f in files:
            rgb, _ = load_rgb(f)
            lab = rgb2lab(rgb); L,a,b = lab[...,0],lab[...,1],lab[...,2]
            C = np.sqrt(a*a+b*b)
            vals = {"wb_a_abs": abs(float(a.mean())), "wb_b_abs": abs(float(b.mean())),
                    "black_p1": float(np.percentile(L,1)), "blown_pct": float(np.mean(L>97)*100),
                    "exposure_med": float(np.percentile(L,50)), "chroma_mean": float(C.mean())}
            verdicts = {k: judge(vals[k], spec[k]) for k in order}
            worst = "FAIL" if "FAIL" in verdicts.values() else ("WARN" if "WARN" in verdicts.values() else "PASS")
            any_bad |= worst != "PASS"
            print(f"\n[{worst}] {Path(f).name}")
            for k in order:
                mark = {"PASS":"  ok ","WARN":" 注意","FAIL":" 不可"}[verdicts[k]]
                line = f"  {mark} {spec[k]['label']:<16} = {vals[k]:6.1f}"
                if verdicts[k] != "PASS":
                    line += f"   → {spec[k]['fix']}"
                print(line)
        print("\n判定基準: assets/shooting_spec.json（撮影要件指示書と同一の数値）")
        return 1 if any_bad else 0
 
    if not files:
        sys.stderr.write("入力画像が指定されていません。\n")
        return 1
 
    # 合わせる先は常に合成ニュートラル基準に1対1。バッチ非依存=決定論的。
    # 明るさだけは基準の中央値ではなく固定の目標(既定62)へ lift-only で寄せる
    # (暗いカットだけ持ち上げ・明るい良露出は不変)。
    match_profile = ref_profile
    DEFAULT_MIDTONE_TARGET = 62.0
    midtone_target = args.midtone_target if args.midtone_target is not None else DEFAULT_MIDTONE_TARGET
    args._midtone_strength = args.midtone_strength if args.midtone_strength is not None else 0.5
    args._midtone_target = float(midtone_target)
 
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"合わせる先: 合成ニュートラル基準(1対1)  ({describe_profile(match_profile)})")
    print(f"手法={args.method}  彩度={args.sat_strength}  "
          f"中間調 lift-only 強度={args._midtone_strength}(目標L中央値={args._midtone_target:.0f})  -> {out_dir}")
 
    ok = 0
    for f in files:
        ext = f.suffix if args.format == "keep" else f".{args.format.replace('jpeg','jpg')}"
        out_path = out_dir / f"{f.stem}{args.suffix}{ext}"
        try:
            process_one(f, out_path, match_profile, args)
            ok += 1
        except Exception as exc:
            sys.stderr.write(f"エラー {f.name}: {exc}\n")
    print(f"完了: {ok}/{len(files)} 枚")
    return 0 if ok == len(files) else 1
 
 
if __name__ == "__main__":
    raise SystemExit(main())
 