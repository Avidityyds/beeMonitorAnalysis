# Bee Monitor Analysis Pipeline / 蜜蜂監測自動分析流程

This repository contains an automated data analysis pipeline powered by **GitHub Actions**.

本專案透過 GitHub Actions 於每月排程執行 Python 分析程式，  
自動讀取由 TX2 上傳的每月 CSV 資料，並產生蜜蜂進出行為與花粉率的視覺化圖表，最後將結果存回此 GitHub repo。

---

## Features / 功能特色

- 每月自動排程執行（GitHub Actions）
- 使用 Python 分析 TX2 上傳的 CSV 資料
- 自動產生多張視覺化圖表（PNG）
- 將圖表結果自動 commit 回 GitHub repo
- 固定檔名覆蓋更新，不會造成 repo 無限成長

---

## 📂 Project Structure / 專案結構

```text
beeMonitorAnalysis/
├── .github/
│   └── workflows/
│       └── monthly-analysis.yml     # GitHub Actions 工作流程
├── analysis.py                      # 主要分析腳本
├── requirements.txt                 # Python 套件需求
├── data/
│   └── 2025-09_TX2_6_inout.csv      # TX2 上傳的每月原始資料
└── output/
    ├── inout_01-10.png              # 1–10 日進出量圖
    ├── inout_11-20.png              # 11–20 日進出量圖
    ├── inout_21-XX.png              # 21–月底 進出量圖（自動判斷）
    ├── pollen_01-10.png             # 1–10 日花粉率圖
    ├── pollen_11-20.png             # 11–20 日花粉率圖
    └── pollen_21-XX.png             # 21–月底花粉率圖
```

---

## ⚙️ How It Works / 運作方式

1. GitHub Actions 依排程於每月 1 號自動觸發 workflow。
2. Runner 安裝 requirements.txt 中的 Python 套件。
3. 執行 analysis.py：
    - 自動搜尋 data/ 目錄中最新的 *_TX2_6_inout.csv 檔案
    - 解析時間欄位
    - 自動判斷當月天數（28 / 30 / 31 天）
    - 將資料拆分為三個區段：
      - 1–10 日
      - 11–20 日
      - 21–月底
    - 產生圖表並輸出到 output/ 目錄
4. Workflow 會將 output/ 底下更新的圖片檔案 commit 並 push 回 GitHub repo。

---

## 🕒 Schedule / 排程說明

自動執行時間：每月 1 號 00:00（UTC+8 / 台灣時間）

也可以手動觸發：
```text
GitHub → Actions → monthly-analysis → Run workflow
```
