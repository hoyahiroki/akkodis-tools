#!/usr/bin/env python3
"""HCUX Audit / 改善ロードマップ の Markdown を ブルー基調A4横向きPDF に整形する。
使い方: python3 render.py <input.md> <output.pdf> [--title "任意のタイトル"]
 
このバージョンで追加した整形ルール（プレゼンテーション層で決定論的に適用。GPTが出力した
分析本文は一切変更せず、並び順・体裁のみ整える）:
  [A] 改善課題リスト（10列）: ID/根拠強度/影響度/優先度 を最小幅・折り返し禁止にし、
      問題内容/根拠/改善案/計測指標 を広く取る（列ごとの固定幅を付与）。
  [B] ロードマップ「含まれる課題」表: 列順を ID→優先度→影響度→根拠強度→場所・対象→一言要約
      に統一し、優先度/影響度/根拠強度 を折り返し禁止にする。
  [C] ロードマップ「依存関係・順序の判断」が“表”で来た場合、箇条書き（ID○○：…）に変換する。
  [D] 「最短で効果を出す着手順トップ5」が“箇条書き（ID○○：…）”で来た場合、
      順位/ID/理由 の表に変換する（既に表で来ていればそのまま）。
  [E] 「評価手法・指標の凡例（参考）」は、GPT出力の凡例ブロックを破棄し、
      v38.2の凡例と一致する完全版（8ブロック）に差し替える。GPTが確認レベル等を落としても常に完全版になる。
  [F] セクション3「推奨データ収集リスト」の各テーブル（GA4/ヒートマップ/追加検証。
      「関連ID」列を持つ表）を専用スタイルで整え、関連ID列は折り返さない。
"""
import sys, re, html, tempfile, os
 
CSS = """<style>
*{box-sizing:border-box;}
body{margin:0;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.report{padding:0 34px 26px;font-family:'Noto Sans CJK JP',sans-serif;color:#1a2b3c;}
.report h1{background:linear-gradient(100deg,#0c447c,#0a3766);color:#fff;font-size:25px;font-weight:900;margin:0 -34px 20px;padding:24px 34px;letter-spacing:.01em;}
.report h2{color:#0c447c;font-size:19px;font-weight:800;margin:22px 0 11px;padding-left:11px;border-left:5px solid #0c447c;page-break-after:avoid;}
.report h3{color:#22384c;font-size:14.5px;font-weight:800;margin:16px 0 7px;page-break-after:avoid;}
.report p{font-size:12.5px;line-height:1.7;margin:7px 0;}
.report ul{margin:7px 0 7px 2px;padding:0;list-style:none;}
.report li{font-size:12.5px;line-height:1.6;margin:4px 0;padding-left:17px;position:relative;}
.report li::before{content:"";position:absolute;left:2px;top:8px;width:6px;height:6px;border-radius:50%;background:#0c64b4;}
.report table{width:100%;border-collapse:collapse;margin:9px 0 6px;font-size:12px;page-break-inside:auto;}
.report thead{display:table-header-group;}
.report tr{page-break-inside:avoid;}
.report th{background:#0c447c;color:#fff;font-weight:700;font-size:11.5px;text-align:left;padding:9px 8px;border:1px solid #0a3d70;line-height:1.3;}
.report td{padding:9px 8px;border:1px solid #e2e8f0;vertical-align:top;line-height:1.5;}
.report tr:nth-child(even) td{background:#f6f9fc;}
.report table.wide{font-size:10.5px;table-layout:fixed;}
.report table.wide th,.report table.wide td{padding:7px 6px;word-break:break-word;line-height:1.45;}
.report table.issue{font-size:10.2px;table-layout:fixed;}
.report table.issue th,.report table.issue td{padding:6px 5px;word-break:break-word;line-height:1.4;}
.report table.rm{font-size:11.5px;table-layout:fixed;}
.report table.rm th,.report table.rm td{padding:7px 7px;word-break:break-word;line-height:1.45;}
.report table.top5{font-size:12px;table-layout:fixed;}
.report table.top5 th,.report table.top5 td{padding:7px 8px;word-break:break-word;line-height:1.55;}
.report th.nw,.report td.nw{white-space:nowrap;text-align:center;}
.bd{display:inline-block;color:#fff;font-weight:800;font-size:11px;padding:2px 7px;border-radius:5px;}
.p0{background:#d6453f;}.p1{background:#e8a13a;}.p2{background:#8a94a6;}
.ih{color:#d6453f;font-weight:800;}.im{color:#c98a20;font-weight:800;}.il{color:#7b8a9a;font-weight:700;}
.report a{color:#0c64b4;word-break:normal;overflow-wrap:anywhere;text-decoration:none;}
.report h4{color:#22384c;font-size:13px;font-weight:800;margin:13px 0 5px;page-break-after:avoid;}
.report p.lgnote{font-size:10.5px;color:#5b6b7b;margin:3px 0 8px;}
.report p.lg{font-size:11px;line-height:1.55;margin:5px 0;}
.report p.lg strong{color:#0c447c;}
.report table.dc{font-size:11.5px;}
.report table.dc th,.report table.dc td{padding:7px 8px;}
</style>"""
 
def esc(s): return html.escape(s, quote=False)
 
# ⑤ v38.2 の「評価手法・指標の凡例（参考）」を整形側で固定注入する。
# GPT出力が凡例ブロックを落としたり別構造で出しても、PDFは常にこの完全版に差し替える。
# 【重要・保守メモ】この文言は v38.2 の凡例と一致させてある(8ブロック・ラベル/順序/本文を機械照合で確認済み)。GPT側(v38.x)で凡例を改訂したら、ここも更新すること。
CANON_LEGEND_BLOCKS = [
    ("優先度", "P0：最優先（最初に着手すべき）／P1：次対応（P0の後に着手）／P2：改善候補（余力があれば対応）"),
    ("影響度", "高：CVや主要KPIへの直接的な影響が想定される／中：ユーザーの迷い・離脱を引き起こす可能性がある／低：体験の改善にはなるがCV・KPIへの影響は限定的"),
    ("根拠強度", "強：実測定量データまたは実データに基づく定性調査（ユーザーテスト等）と観察事実が一致（サンプル・推計・デモ・ダミーデータは原則除く）／中：観察事実＋公知のUX原則・Web慣習で裏付け、または仮再評価用データ（サンプル・推計・デモ）で裏付け（実測は要差し替え）／弱：観察範囲が限定的で追加確認が必要"),
    ("確認レベル", "（アクセシビリティ評価の課題で「根拠」欄末尾に付記）観察で確認可能：目視で判断できる／DOM確認が必要：HTML構造の確認を要する／操作検証が必要：実機での操作確認を要する／未確認：今回の評価範囲では確認できていない"),
    ("実測根拠未添付時のP0について", "実測定量データまたは実データに基づく定性調査がない場合、根拠強度「強」は原則発生しないため、P0は「影響度：高 × 根拠強度：中」の課題に限られます。これは確信度の高い課題のみを最優先に厳選する設計で、P0が少ないことは課題が少ないことを意味しません。実測データまたは実データに基づく定性調査を追加すると根拠強度が上がり、P0判定が増える可能性があります。"),
    ("ニールセン10原則によるヒューリスティック評価", "原則1：システム状態の視認性（今何が起きているか分かるか）／原則2：システムと実世界の一致（日常用語で書かれているか）／原則3：ユーザーコントロールと自由（戻る・取り消しができるか）／原則4：一貫性と標準（用語・配置が統一されているか）／原則5：エラーの防止（入力ミスが起きにくいか）／原則6：記憶より認識（選択肢が画面上に見えているか）／原則7：柔軟性と効率性（初心者・上級者の両方が使いやすいか）／原則8：美的でミニマルなデザイン（不要な要素で主要コンテンツが埋もれていないか）／原則9：エラーからの回復支援（エラー原因と対処法が分かるか）／原則10：ヘルプとドキュメント（必要時にサポート・FAQにアクセスできるか）"),
    ("認知的ウォークスルー", "ユーザーが目的達成までの操作を1ステップずつ辿り、各ステップで「次に何をすればよいか分かるか」「それが正しいと判断できるか」「実行可能なUIか」「実行後の結果が理解できるか」を確認する手法"),
    ("アクセシビリティ評価の観点", "視認性（文字・色・コントラスト・行間・余白）／操作性（タップ領域・フォーカス・キーボード操作）／フォーム（ラベル・必須任意・エラー文・入力補助）／ナビゲーション（現在地・戻り導線・見出し構造・リンク文言）／認知負荷（専門用語・選択肢過多・手順の複雑さ）／画像・代替・支援技術（alt属性・ARIA等）／動的UI（ローディング・送信中・完了・エラー等の状態変化）／レスポンシブ（SP表示・拡大表示・横スクロール）"),
]
def canon_legend_html():
    parts = ['<h4>評価手法・指標の凡例（参考）</h4>',
             '<p class="lgnote">※既に評価手法に習熟されている場合は読み飛ばし可。</p>']
    for label, body in CANON_LEGEND_BLOCKS:
        parts.append('<p class="lg"><strong>【%s】</strong> %s</p>' % (esc(label), esc(body)))
    return '\n'.join(parts)
 
def inline(t):
    t = esc(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    def _a(m):
        u = m.group(1)                                   # already HTML-escaped (& -> &amp;)
        vis = re.sub(r'([/._\-?=])', r'\1<wbr>', u)       # break after path/domain delimiters, not inside &amp;
        return '<a href="%s">%s</a>' % (u, vis)
    t = re.sub(r'(https?://[^\s|、）)]+)', _a, t)
    return t
 
def badge(cell):
    t = cell.strip()
    m = {'P0':'<span class="bd p0">P0</span>','P1':'<span class="bd p1">P1</span>','P2':'<span class="bd p2">P2</span>',
         '高':'<span class="ih">高</span>','中':'<span class="im">中</span>','低':'<span class="il">低</span>',
         '強':'<span class="ih">強</span>','弱':'<span class="il">弱</span>'}
    return m.get(t, inline(cell))
 
def split_row(line):
    s = line.strip()
    s = re.sub(r'^\|','',s); s = re.sub(r'\|$','',s)
    return [c.strip() for c in s.split('|')]
 
def is_sep(line):
    return bool(re.match(r'^\s*\|?[\s:|\-]*-[\s:|\-]*\|?\s*$', line)) and '-' in line
 
def norm(s): return re.sub(r'\s','', s)
 
# ---- table classification & column policy -------------------------------------
def classify_table(header):
    hs = [norm(h) for h in header]
    has = lambda kw: any(kw in h for h in hs)
    if has('着手順') and has('依存関係'):
        return 'dependency'
    if has('優先度') and has('場所') and has('要約'):
        return 'roadmap'
    if has('問題') and has('優先度') and (has('計測') or has('改善')):
        return 'issue'
    if has('関連ID'):                 # ⑥ セクション3（GA4/ヒートマップ/追加検証）の各テーブル
        return 'datacollect'
    return 'generic'
 
def issue_width(h):
    hn = norm(h)
    if hn == 'ID': return 3
    if '評価' in hn: return 11
    if '場所' in hn: return 10
    if '問題' in hn: return 15
    if '根拠強度' in hn: return 6
    if '根拠' in hn: return 15
    if '影響' in hn: return 5
    if '優先' in hn: return 5
    if '改善' in hn: return 18
    if '計測' in hn: return 10
    return 8
 
def issue_narrow(h):
    hn = norm(h)
    return hn == 'ID' or ('根拠強度' in hn) or ('影響' in hn) or ('優先' in hn)
 
RM_ORDER = ['ID','優先度','影響度','根拠強度','場所','要約']
def rm_rank(h):
    hn = norm(h)
    for i,k in enumerate(RM_ORDER):
        if hn == k or k in hn: return i
    return len(RM_ORDER) + 1
 
def rm_width(h):
    hn = norm(h)
    if hn == 'ID': return 4
    if '優先' in hn: return 8
    if '影響' in hn: return 7
    if '根拠強度' in hn: return 8
    if '場所' in hn: return 40
    if '要約' in hn: return 33
    return 10
 
def rm_narrow(h):
    hn = norm(h)
    return ('優先' in hn) or ('影響' in hn) or ('根拠強度' in hn)
 
def build_table(header, rows, cls):
    cols = len(header)
    if cls == 'issue':
        colg = '<colgroup>' + ''.join('<col style="width:%s%%">' % issue_width(h) for h in header) + '</colgroup>'
        narrow = [issue_narrow(h) for h in header]
    elif cls == 'roadmap':
        idx = sorted(range(cols), key=lambda j: (rm_rank(header[j]), j))
        header = [header[j] for j in idx]
        rows = [[ (r + ['']*cols)[:cols][j] for j in idx] for r in rows]
        colg = '<colgroup>' + ''.join('<col style="width:%s%%">' % rm_width(h) for h in header) + '</colgroup>'
        narrow = [rm_narrow(h) for h in header]
    elif cls == 'datacollect':
        colg = ''
        narrow = [('関連ID' in norm(h)) for h in header]   # ⑥ 関連ID列は折り返さない
    else:
        colg = ''
        narrow = [False]*cols
    tcls = {'issue':' class="issue"','roadmap':' class="rm"','datacollect':' class="dc"'}.get(cls, ' class="wide"' if cols >= 8 else '')
    th = ''.join('<th%s>%s</th>' % (' class="nw"' if narrow[j] else '', inline(header[j])) for j in range(cols))
    trs = ''
    for r in rows:
        r = (r + ['']*cols)[:cols]
        trs += '<tr>' + ''.join('<td%s>%s</td>' % (' class="nw"' if narrow[j] else '', badge(r[j])) for j in range(cols)) + '</tr>'
    return '<table%s>%s<thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (tcls, colg, th, trs)
 
def dependency_bullets(header, rows):
    cols = len(header); hn = [norm(h) for h in header]
    id_i = next((k for k,h in enumerate(hn) if 'ID' in h), None)
    dep_i = next((k for k,h in enumerate(hn) if '依存関係' in h), None)
    lis = []
    for r in rows:
        r = (r + ['']*cols)[:cols]
        idv = re.sub(r'^ID', '', (r[id_i].strip() if id_i is not None else ''))
        depv = r[dep_i].strip() if dep_i is not None else ' '.join(x for x in r if x.strip())
        prefix = ('ID%s：' % idv) if idv else ''
        lis.append('<li>' + inline(prefix + depv) + '</li>')
    return '<ul>' + ''.join(lis) + '</ul>'
 
def top5_table(id_matches):
    colg = '<colgroup><col style="width:8%"><col style="width:10%"><col style="width:82%"></colgroup>'
    th = '<th class="nw">順位</th><th class="nw">ID</th><th>理由</th>'
    trs = ''
    for k,m in enumerate(id_matches):
        trs += '<tr><td class="nw">%d</td><td class="nw">ID%s</td><td>%s</td></tr>' % (k+1, m.group(1).zfill(2), inline(m.group(2)))
    return '<table class="top5">%s<thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (colg, th, trs)
 
# ---- markdown -> html ---------------------------------------------------------
def md_to_html(md):
    lines = md.replace('\r','').split('\n'); out=[]; i=0; n=len(lines); in_top5=False; skipping=False
    while i < n:
        line = lines[i]
        is_heading = re.match(r'^(#{1,4})\s+(.*)$', line)
        if skipping:                                   # ⑤ GPTが出した凡例本文を次の見出しまで捨てる
            if is_heading:
                skipping = False
            else:
                i += 1; continue
        if re.match(r'^\s*\|', line) and i+1 < n and is_sep(lines[i+1]):
            header = split_row(line); i += 2; rows=[]
            while i < n and re.match(r'^\s*\|', lines[i]) and not is_sep(lines[i]):
                rows.append(split_row(lines[i])); i += 1
            cls = classify_table(header)
            if cls == 'dependency':
                out.append(dependency_bullets(header, rows))       # [C]
            else:
                out.append(build_table(header, rows, cls))          # [A][B][F]
            continue
        if is_heading:
            lv = len(is_heading.group(1)); txt = is_heading.group(2)
            if '評価手法' in norm(txt) and '凡例' in norm(txt):     # [E] 凡例をv38.2固定版に差し替え
                out.append(canon_legend_html())
                in_top5 = False; skipping = True
                i += 1; continue
            in_top5 = ('トップ5' in txt) or ('着手順トップ' in txt)  # [D] section flag
            out.append('<h%d>%s</h%d>' % (lv, inline(txt), lv)); i += 1; continue
        if re.match(r'^\s*[-*]\s+', line):
            raw = []
            while i < n and re.match(r'^\s*[-*]\s+', lines[i]):
                raw.append(re.sub(r'^\s*[-*]\s+','',lines[i])); i += 1
            ids = [re.match(r'^ID\s*0*(\d+)\s*[:：]\s*(.*)$', x) for x in raw]
            if in_top5 and raw and all(mm is not None for mm in ids):
                out.append(top5_table(ids))                          # [D]
            else:
                out.append('<ul>' + ''.join('<li>'+inline(x)+'</li>' for x in raw) + '</ul>')
            continue
        if re.match(r'^\s*$', line): i += 1; continue
        out.append('<p>' + inline(line) + '</p>'); i += 1
    return '\n'.join(out)
 
def render(md_path, pdf_path, title=None):
    md = open(md_path, encoding='utf-8').read()
    if title:
        md = '# ' + title + '\n\n' + md
    body = md_to_html(md)
    doc = '<!doctype html><html lang="ja"><head><meta charset="utf-8">%s</head><body><div class="report">%s</div></body></html>' % (CSS, body)
    tmp = tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8')
    tmp.write(doc); tmp.close()
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto('file://'+tmp.name); pg.wait_for_timeout(250)
        pg.pdf(path=pdf_path, format='A4', landscape=True, print_background=True,
               margin={'top':'12mm','bottom':'12mm','left':'12mm','right':'12mm'})
        b.close()
    os.unlink(tmp.name)
    print('OK ->', pdf_path)
 
if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    title = None
    for a in sys.argv[1:]:
        if a.startswith('--title='): title = a.split('=',1)[1]
    render(args[0], args[1], title)