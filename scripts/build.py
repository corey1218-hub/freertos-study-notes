#!/usr/bin/env python3
"""Build and validate the notebook with Python's standard library."""
import datetime
import html
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from string import Template
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"
CATEGORIES = ("Task", "Queue", "Timer", "同步")
FIELDS = {"slug", "order", "title", "category", "minutes", "updated", "summary", "one_sentence", "steps", "code", "code_note", "explanation", "pitfalls", "check", "sources"}
ESC = lambda value: html.escape(str(value), quote=True)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text_ok(value):
    return isinstance(value, str) and value.strip() and "請填寫" not in value


def validate(note, path):
    require(set(note) == FIELDS, f"{path.name}: 欄位不符；缺少 {FIELDS - set(note)}，多出 {set(note) - FIELDS}")
    for key in FIELDS - {"order", "minutes", "steps", "explanation", "pitfalls", "check", "sources"}:
        require(text_ok(note[key]), f"{path.name}: {key} 不可為空或含範本文字")
    require(re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", note["slug"]) is not None, f"{path.name}: slug 格式錯誤")
    require(path.stem == note["slug"], f"{path.name}: 檔名與 slug 不同")
    for key in ("order", "minutes"):
        require(type(note[key]) is int and note[key] > 0, f"{path.name}: {key} 必須為正整數")
    require(note["category"] in CATEGORIES, f"{path.name}: 分類不在 AGENTS.md 清單中")
    require(re.fullmatch(r"\d{4}-\d{2}-\d{2}", note["updated"]) is not None, "日期格式錯誤")
    datetime.date.fromisoformat(note["updated"])
    for key, minimum, maximum, subfields in (("steps", 3, 5, {"title", "text"}), ("explanation", 2, 5, {"term", "text"}), ("sources", 1, 10, {"title", "url", "used_for"})):
        require(isinstance(note[key], list) and minimum <= len(note[key]) <= maximum, f"{path.name}: {key} 數量不符")
        for item in note[key]:
            require(isinstance(item, dict) and set(item) == subfields and all(text_ok(v) for v in item.values()), f"{path.name}: {key} 子欄位不完整")
    require(isinstance(note["pitfalls"], list) and 2 <= len(note["pitfalls"]) <= 4 and all(text_ok(x) for x in note["pitfalls"]), f"{path.name}: pitfalls 格式錯誤")
    require(isinstance(note["check"], dict) and set(note["check"]) == {"question", "answer"} and all(text_ok(v) for v in note["check"].values()), f"{path.name}: 自我檢查不完整")
    for source in note["sources"]:
        parsed = urlsplit(source["url"])
        official = parsed.hostname == "freertos.org" or (parsed.hostname or "").endswith(".freertos.org") or (parsed.hostname == "github.com" and parsed.path.startswith("/FreeRTOS/"))
        require(parsed.scheme == "https" and official, f"{path.name}: 來源必須是 FreeRTOS 官方 HTTPS 文件")


def write_page(path, title, description, body, base=""):
    template = Template((ROOT / "templates/base.html").read_text(encoding="utf-8"))
    rendered = template.substitute(title=ESC(title), description=ESC(description), body=body, base=base)
    destination = OUT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(rendered, encoding="utf-8")


def homepage(notes):
    cards = ""
    for n in notes:
        search = " ".join([n["title"], n["summary"], n["category"], n["code"], n["one_sentence"]])
        cards += f'''<a class="note-card" href="notes/{n['slug']}.html" data-note data-category="{ESC(n['category'])}" data-search="{ESC(search.lower())}">
          <div class="card-top"><span class="note-number">{n['order']:02d}</span><span class="tag">{ESC(n['category'])}</span></div>
          <h3>{ESC(n['title'])}</h3><p>{ESC(n['summary'])}</p><div class="card-bottom"><span>約 {n['minutes']} 分鐘</span><span class="read-link">閱讀筆記 <span aria-hidden="true">↗</span></span></div></a>'''
    categories = "".join(f'<button class="filter" type="button" data-filter="{ESC(cat)}" aria-pressed="false">{ESC(cat)} <span>{sum(n["category"] == cat for n in notes)}</span></button>' for cat in CATEGORIES if any(n["category"] == cat for n in notes))
    first = notes[0]
    body = f'''<section class="hero shell">
      <div class="hero-copy"><p class="eyebrow"><span class="dot"></span> 作業系統 / 學習筆記</p><h1>FreeRTOS<br><span class="underline">從這裡開始。</span></h1><p class="hero-description">Task 什麼時候會等？Queue 滿了怎麼辦？<br>把容易卡住的觀念拆開，一次看懂一件事。</p><a class="button primary" href="notes/{first['slug']}.html">從第一篇開始 <span aria-hidden="true">→</span></a><a class="text-link" href="#notes">查看全部筆記</a><div class="hero-meta"><span>{len(notes):02d} 篇筆記</span><span>C 語言範例</span><span>官方文件參照</span></div></div>
      <div class="notebook" aria-label="Task 延遲的概念示意"><div class="paper-top"><span>NOTE 01</span><span>先釐清這件事</span></div><h2>等的是 Task，<br>不是整個 CPU。</h2><div class="time-label">單核心排程示意 <span>時間 →</span></div><div class="lane"><span>Task A</span><div class="track"><b>執行</b><i>Blocked · 等待</i><b>Ready</b></div></div><div class="lane"><span>Task B</span><div class="track"><i>Ready</i><b class="accent">取得 CPU，執行工作</b></div></div><div class="paper-note"><span>→</span> A 等待時，B 有機會執行。<br>時間到後，A 仍要等排程器安排。</div><div class="paper-bottom"><span>vTaskDelay()</span><span>概念圖，非實測時間軸</span></div></div>
    </section>
    <section class="notes-section" id="notes"><div class="shell"><div class="section-heading"><div><p class="eyebrow">01 / 筆記一覽</p><h2>先挑一個想弄懂的問題</h2></div><label class="search"><span aria-hidden="true">⌕</span><span class="sr-only">搜尋筆記</span><input id="note-search" type="search" placeholder="搜尋觀念或 API…" autocomplete="off"></label></div><div class="filters"><button class="filter active" type="button" data-filter="all" aria-pressed="true">全部 <span>{len(notes)}</span></button>{categories}<span id="result-count" class="result-count" role="status">{len(notes)} 篇筆記</span></div><div class="note-grid">{cards}</div><div id="empty-result" class="empty" hidden>沒有符合的筆記。試試「Task」、「Queue」或「callback」。<button type="button" id="clear-search">清除搜尋與篩選</button></div></div></section>
    <section class="shell experiment" id="try"><div class="experiment-intro"><p class="eyebrow">02 / 動手試試</p><h2>Queue 滿了，<br>下一筆放得進去嗎？</h2><p>先按「放入資料」填滿 5 格，再放一次。<br>看看原本的資料會不會被覆蓋。</p><a class="text-link" href="notes/queue-basics.html">回到 Queue 筆記 <span aria-hidden="true">→</span></a></div><div class="queue-panel"><div class="queue-header"><strong>FIFO 收件匣</strong><span id="queue-count">0 / 5 筆</span></div><div class="queue-direction"><span>取出 ←</span><span>← 放入</span></div><ol id="queue-slots" class="queue-slots" aria-label="Queue 內容"><li>—</li><li>—</li><li>—</li><li>—</li><li>—</li></ol><div class="queue-controls"><button type="button" class="button primary" id="enqueue">放入資料 +</button><button type="button" class="button secondary" id="dequeue">取出一筆 −</button><button type="button" class="reset" id="reset-queue">重設</button></div><p id="queue-message" class="queue-message" role="status" aria-live="polite">Queue 目前是空的，放入第一筆資料試試。</p><p class="fine-print">簡化示意：容量 5、FIFO、等待時間 0。這不是實際的 FreeRTOS 排程或效能測試。</p></div></section>
    <section class="shell rule-strip"><div><p class="eyebrow">03 / 留給下一次的規則</p><h2>新增一篇，不用重做整個網站。</h2><p>內容放進固定格式，版型、首頁與前後篇連結一起產生。</p></div><a class="button secondary" href="rules.html">看專案怎麼延續 <span aria-hidden="true">↗</span></a></section>'''
    write_page("index.html", "首頁", "從 Task、Queue、Timer 的常見問題開始，用簡短說明與 C 語言範例整理 FreeRTOS。", body)


def article(note, previous, following):
    n = note
    steps = "".join(f'<li><span class="step-number">{i:02d}</span><div><h3>{ESC(s["title"])}</h3><p>{ESC(s["text"])}</p></div></li>' for i, s in enumerate(n["steps"], 1))
    explanation = "".join(f'<div><dt><code>{ESC(x["term"])}</code></dt><dd>{ESC(x["text"])}</dd></div>' for x in n["explanation"])
    pitfalls = "".join(f'<li>{ESC(x)}</li>' for x in n["pitfalls"])
    sources = "".join(f'<li><a href="{ESC(s["url"])}" target="_blank" rel="noopener noreferrer">{ESC(s["title"])} ↗</a><p>{ESC(s["used_for"])}</p></li>' for s in n["sources"])
    nav = ""
    for adjacent, label in ((previous, "上一篇"), (following, "下一篇")):
        nav += f'<a href="{adjacent["slug"]}.html"><small>{label}</small><strong>{ESC(adjacent["title"])}</strong></a>' if adjacent else '<span></span>'
    toc = "".join(f'<a href="#{anchor}"><span>{i:02d}</span> {label}</a>' for i, (anchor, label) in enumerate((("idea", "一句話理解"), ("flow", "運作流程"), ("code", "程式片段"), ("pitfalls", "容易弄錯的地方"), ("check", "自我檢查"), ("sources", "參考資料")), 1))
    body = f'''<div class="shell article-shell"><div class="breadcrumb"><a href="../index.html#notes">全部筆記</a><span>/</span>{ESC(n['category'])}</div><header class="article-header"><p class="eyebrow">NOTE {n['order']:02d} <span class="sep">/</span> {ESC(n['category'])}</p><h1>{ESC(n['title'])}</h1><p class="article-summary">{ESC(n['summary'])}</p><div class="article-meta">約 {n['minutes']} 分鐘 <span>·</span> 更新 {ESC(n['updated'])} <span>·</span> C 語言教學片段</div></header><div class="article-layout"><aside class="toc"><p>這一篇的重點</p><nav aria-label="文章目錄">{toc}</nav><a class="back-link" href="../index.html#notes">← 返回筆記一覽</a></aside><article class="article-body"><section id="idea"><h2>一句話理解</h2><p class="key-idea">{ESC(n['one_sentence'])}</p></section><section id="flow"><h2>運作流程</h2><ol class="steps">{steps}</ol></section><section id="code"><h2>程式片段</h2><div class="code-window"><div class="code-bar"><span>C / 教學片段</span><button class="copy-code" type="button">複製程式碼</button></div><pre tabindex="0" aria-label="C 程式片段"><code>{ESC(n['code'])}</code></pre></div><p class="code-note">{ESC(n['code_note'])}</p><dl class="explanation">{explanation}</dl></section><section id="pitfalls"><h2>容易弄錯的地方</h2><ul class="pitfalls">{pitfalls}</ul></section><section id="check" class="self-check"><p class="eyebrow">停一下，想想看</p><h2>自我檢查</h2><p>{ESC(n['check']['question'])}</p><details><summary>看說明</summary><p>{ESC(n['check']['answer'])}</p></details></section><section id="sources"><h2>參考資料</h2><p class="source-note">概念依官方文件整理，以下列出各來源用到的部分。</p><ul class="sources">{sources}</ul></section><nav class="article-next" aria-label="前後篇筆記">{nav}</nav></article></div></div>'''
    write_page(f"notes/{n['slug']}.html", n["title"], n["summary"], body, "../")


def rules_page(count):
    rules = ESC((ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    body = f'''<div class="shell rules-page"><a class="text-link" href="index.html">← 回首頁</a><p class="eyebrow rule-eyebrow">第九週 / 專案型 AI Agent</p><h1>這個網站，<br>下一次要怎麼繼續做？</h1><p class="rules-lead">我把每篇筆記該有的內容、檔案放法和檢查步驟寫進 AGENTS.md。之後換一個主題，AI 先讀規則，就能沿用同一套做法。</p><div class="rule-facts"><div><span>內容</span><strong>每篇一個 JSON</strong><p>固定欄位，不把內容綁死在網頁裡。</p></div><div><span>版型</span><strong>所有頁面共用</strong><p>首頁清單、目錄和前後篇連結自動產生。</p></div><div><span>檢查</span><strong>發布前先建置</strong><p>缺欄位、重複排序、壞掉的站內連結都會報錯。</p></div></div><section class="extension"><p class="eyebrow">實際擴充示範</p><h2>從 2 篇，增加到 {count} 篇。</h2><p>先完成 Task 與 Queue 筆記，再依同一份規則新增 Timer 筆記。文章數、分類與前後篇連結由建置程式更新，沒有為第三篇另外寫一份 HTML。</p><ol><li>讀取 <code>AGENTS.md</code> 與現有筆記。</li><li>依 <code>templates/note.example.json</code> 欄位建立 <code>content/timer-callback.json</code>。</li><li>執行 <code>python3 scripts/build.py</code>。</li><li>檢查首頁的 Timer 分類及新增文章。</li></ol><a class="text-link" href="notes/timer-callback.html">查看依規則新增的 Timer 筆記 →</a></section><section class="prompt-block"><h2>下次可以這樣交辦</h2><p>先讀 AGENTS.md 與現有的 Queue 筆記，再新增一篇「Binary Semaphore 和 Mutex 有什麼差別？」。依範本填寫內容，查閱官方文件；維持既有版型，完成建置與頁面檢查後回報。不要直接修改 dist 裡的檔案。</p></section><div class="rules-heading"><h2>完整專案規則</h2><a class="button secondary" href="AGENTS.md" download>下載 AGENTS.md ↓</a></div><pre class="rules-source" tabindex="0">{rules}</pre><p class="fine-print">這是使用 AI 協作建立的課堂專案。頁面內容、建置規則與檢查方式都保留在原始碼中；C 範例為教學片段，未宣稱完成硬體驗證。</p></div>'''
    write_page("rules.html", "專案規則與擴充方式", "AGENTS.md 如何規範 FreeRTOS 筆記的新增、版型、來源與驗證。", body)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            require(attrs["id"] not in self.ids, f"重複 HTML id: {attrs['id']}")
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])


def check_links():
    parsed = {}
    for path in OUT.rglob("*.html"):
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8"))
        parsed[path.resolve()] = parser
    total = 0
    for path, parser in parsed.items():
        for link in parser.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            require(target.is_relative_to(OUT.resolve()), f"連結越出網站: {link}")
            require(target.is_file(), f"缺少站內檔案: {path.name} -> {link}")
            if parts.fragment and target.suffix == ".html":
                require(parts.fragment in parsed[target].ids, f"缺少錨點: {link}")
            total += 1
    return len(parsed), total


def main():
    notes = []
    for path in sorted((ROOT / "content").glob("*.json")):
        note = json.loads(path.read_text(encoding="utf-8"))
        validate(note, path)
        notes.append(note)
    require(notes, "至少要有一篇筆記")
    for field in ("slug", "order"):
        require(len({n[field] for n in notes}) == len(notes), f"{field} 不可重複")
    notes.sort(key=lambda n: n["order"])
    OUT.mkdir(exist_ok=True)
    # Remove only generated article pages; keep source files outside dist untouched.
    (OUT / "notes").mkdir(exist_ok=True)
    for path in (OUT / "notes").glob("*.html"):
        path.unlink()
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    shutil.copy2(ROOT / "AGENTS.md", OUT / "AGENTS.md")
    (OUT / ".nojekyll").touch()
    homepage(notes)
    for index, note in enumerate(notes):
        article(note, notes[index - 1] if index else None, notes[index + 1] if index + 1 < len(notes) else None)
    # The rules page includes the Timer extension only after it exists.
    if any(n["slug"] == "timer-callback" for n in notes):
        rules_page(len(notes))
    else:
        write_page("rules.html", "專案規則", "閱讀專案規則", '<div class="shell rules-page"><h1>專案規則</h1><a href="AGENTS.md">閱讀 AGENTS.md</a></div>')
    pages, links = check_links()
    print(json.dumps({"notes": len(notes), "html_pages": pages, "local_links_checked": links, "schema": "passed", "local_links": "passed", "output": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
