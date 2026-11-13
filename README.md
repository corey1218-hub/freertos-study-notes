# FreeRTOS 學習筆記

生成式 AI 第九週作業：建立自己的 `AGENTS.md`，讓 AI 能沿用規則持續新增內容。

這個專案把 FreeRTOS 入門時容易卡住的問題整理成短篇筆記。每篇先說明觀念，再看運作流程與 C 程式片段，最後列出容易弄錯的地方和官方參考資料。

## 目前內容

1. Task 延遲時，CPU 在做什麼？
2. 兩個 Task，怎麼把資料交給對方？
3. Timer 的 callback，為什麼不能慢慢等？

首頁提供關鍵字搜尋、分類篩選，以及容量 5 的 Queue 互動示意。這個互動只表現 FIFO 與等待時間為 0 時的滿／空行為，並不是 FreeRTOS 核心或效能模擬器。

## 為什麼要寫 AGENTS.md

如果只叫 AI「幫我做一個筆記網站」，下次新增內容時，文章格式、檔案位置和說明深度可能都不一致。因此這次先寫出具體規則：一篇只回答一個問題、固定章節、資料來源要求、檔案命名、建立頁面的方法，以及完成前的檢查。

完整規則在 [AGENTS.md](AGENTS.md)。網站內的「專案規則」頁也可閱讀及下載相同檔案。

## 在自己的電腦執行

需要 Python 3.9 或以上，不需要安裝第三方套件。

```bash
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

Windows 若沒有 `python3` 指令，可改用 `py`。在瀏覽器開啟 `http://localhost:8000`。也可以直接開啟 `dist/index.html`；搜尋與 Queue 示意仍可運作，但部分瀏覽器會限制本機檔案的剪貼簿功能。

## 新增一篇筆記

1. 先讀 `AGENTS.md` 與一篇現有筆記。
2. 複製 `templates/note.example.json` 到 `content/`，填好欄位並調整檔名、slug 與 order。
3. 查閱官方文件，將用到的來源與用途寫入 `sources`。
4. 執行 `python3 scripts/build.py`。
5. 檢查首頁、搜尋結果、新文章及前後篇連結。

不用另外手寫新文章的 HTML。建置器會讀取所有內容檔，產生一致版型、首頁清單、分類數量與前後篇導覽。

可參考 [實際擴充紀錄](docs/extension-demo.md) 與 [檢查紀錄](docs/verification.md)。

## 部署到 GitHub Pages

完整專案應包含規則、內容、版型、建置程式與 `dist/` 網頁成果，不能只上傳 `index.html`。

本專案的 Pages 發布方式為：將 `dist/` 網頁複製到 `docs/site/` 並以 GitHub Pages 的 `main` 分支、`/docs` 目錄發布。`docs/index.html` 會導向 `site/index.html`。執行下列命令即可更新這份靜態發布副本：

```bash
python3 scripts/build.py
python3 scripts/prepare_pages.py
```

首次發布後於 Repository 的 **Settings → Pages** 選擇 **Deploy from a branch → main → /docs → Save**。後續更新後提交全部變更，Pages 就會重新發布。

## 協作與限制

- 本專案由 AI 協助撰寫內容與程式，所有規則、內容來源與檢查紀錄均保留在專案中。
- C 範例是需要接入既有 FreeRTOS 專案的教學片段，不是可直接燒錄的完整韌體。
- 未宣稱完成硬體執行、精確計時或 FreeRTOS 核心測試。
- 網頁沒有登入、外部 API 或資料庫，也不需要輸入任何金鑰。
- 網站內容不包含課程講義全文、個人學號或私人設備資料。
