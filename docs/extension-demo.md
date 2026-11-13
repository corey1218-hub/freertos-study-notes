# 實際擴充紀錄

日期：2026-11-13

## 先建兩篇

第一次建置時，`content/` 只有 `task-delay.json`、`queue-basics.json`。

實際執行 `python3 scripts/build.py` 的結果：

```json
{"notes": 2, "html_pages": 4, "local_links_checked": 61, "schema": "passed", "local_links": "passed"}
```

## 依照同一份規則新增 Timer

參考 `AGENTS.md`、`templates/note.example.json` 及現有文章欄位，新增 `content/timer-callback.json`。

新增時填入單一問題、流程、C 片段、範例前提、常見錯誤、自我檢查與官方來源。沒有手寫 Timer 的 HTML，也沒有為它另做文章版型。

重新建置後應檢查：

- 首頁由 2 篇變成 3 篇。
- 新增 Timer 分類，計數為 1。
- 搜尋 callback 能找到 Timer 筆記。
- Queue 頁的下一篇連到 Timer；Timer 的上一篇連回 Queue。
- 新文章保留與其他文章相同的章節與版型。

第二次建置與瀏覽器檢查的實際結果列在 `verification.md`。

## 這個示範能證明什麼

新增資料檔之後，共用建置流程能更新相關頁面，不需要重複寫版型。這不代表任何 AI 都一定會遵守規則，也不代表內容自動正確；來源查證與頁面檢查仍是規則的一部分。
