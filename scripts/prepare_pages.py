#!/usr/bin/env python3
"""Copy the verified static output to GitHub Pages' supported /docs folder."""
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent.parent
source = root / "dist"
destination = root / "docs/site"
if not (source / "index.html").is_file():
    raise SystemExit("請先執行 python3 scripts/build.py")
if destination.exists():
    shutil.rmtree(destination)
shutil.copytree(source, destination)
(root / "docs/.nojekyll").touch()
(root / "docs/index.html").write_text('''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=site/index.html"><title>FreeRTOS 學習筆記</title></head><body><p><a href="site/index.html">前往 FreeRTOS 學習筆記</a></p></body></html>
''', encoding="utf-8")
print("GitHub Pages 發布副本已更新：docs/site/")
