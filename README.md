# Remove Text Extra Spaces v3

`Remove Text Extra Spaces v3` 是一個專門用來整理 AI 語音轉文字、OCR 擷取文字、以及中英混排 TXT 內容的小工具。它可以快速清掉多餘空格、修正常見標點格式，並支援兩種使用方式：批次處理文字檔，或直接把短文字貼進 GUI 即時整理。

相關文章：
[AI 語音轉文字格式太亂？獨創免安裝小工具「Remove Text Extra Spaces」幫你一鍵搞定！](https://taoyutsun.blogspot.com/2025/02/Remove-Text-Extra-Spaces.html)

上面的部落格文章介紹的是本工具的初始版本，當時以單一 TXT 檔案清理為主。  
目前這個 repository 內提供的是後續升級的 `v3` 版本，功能比文章中的初版更完整。

## v3 版本重點

- 支援單檔或多檔 TXT 批次清理
- 支援拖曳 `.txt` 檔加入處理清單
- 支援直接貼上純文字後即時清理
- 可勾選不同清理規則
- 可選擇是否保留段落換行
- 檔案模式會自動輸出為同資料夾下的 `_cleaned.txt`

## 適用情境

- AI 語音轉文字後的格式整理
- OCR 掃描文字後的空格與標點修正
- 中英文混排內容的快速清理
- 多份 TXT 檔案的批次後處理
- 短篇逐字稿、留言、會議片段的即時整理

## 下載與部署

### 方式一：一般使用者直接下載 Windows 執行檔

如果你只是想直接使用，不需要安裝 Python，建議從 GitHub Releases 下載現成的 `.exe`：

1. 前往 [Releases 頁面](https://github.com/taoyutsun/remove-text-extra-spaces/releases)
2. 下載最新版本的 `remove_text_extra_spaces_v3.exe`
3. 將檔案放到你想使用的資料夾
4. 直接雙擊執行即可

這個方式最適合一般使用者，也最接近「下載後即可使用」的體驗。

### 方式二：從原始碼執行

如果你想自行查看程式、修改規則或重新打包，可以直接從原始碼執行。

#### 環境需求

- Windows 10 / 11
- Python 3.10 以上
- 不需安裝第三方套件即可執行主程式

#### 下載原始碼

方法 A：直接下載 ZIP

1. 前往本專案首頁：[taoyutsun/remove-text-extra-spaces](https://github.com/taoyutsun/remove-text-extra-spaces)
2. 點選 `Code`
3. 選擇 `Download ZIP`
4. 解壓縮後進入專案資料夾

方法 B：使用 Git clone

```powershell
git clone https://github.com/taoyutsun/remove-text-extra-spaces.git
cd remove-text-extra-spaces
```

#### 執行主程式

```powershell
python .\remove_text_extra_spaces_v3.py
```

## 使用方式

程式啟動後，畫面主要分成兩個工作模式與一個選項區。

### 1. 檔案模式

適合處理一個或多個 `.txt` 檔案。

操作步驟：

1. 切換到「檔案模式」
2. 點選「新增檔案」選擇一個或多個 `.txt` 檔
3. 或直接把 `.txt` 檔拖曳到視窗中
4. 右側勾選需要的清理規則
5. 按下「開始處理檔案」

處理完成後，程式會在原始檔案同一個資料夾中，自動輸出：

```text
原檔名_cleaned.txt
```

例如：

```text
meeting_notes.txt
→ meeting_notes_cleaned.txt
```

### 2. 直接貼文字

適合處理較短的內容，例如：

- 一小段逐字稿
- 一段 OCR 擷取內容
- 臨時從網頁或文件複製的文字

操作步驟：

1. 切換到「直接貼文字」
2. 把原始文字貼到上方的「原始文字」區塊
3. 右側勾選需要的清理規則
4. 按下「清理文字」
5. 在下方的「清理後文字」區塊查看結果
6. 可再用「複製結果」或「儲存結果」輸出內容

### 3. 右側清理選項

右側的「清理選項」可以依需求勾選，常見用途如下：

- `將連續空白壓成單一空格`：清掉重複空格
- `移除中文字與中文字之間的空格`：把「我 是 學 生」整理成「我是學生」
- `修正全形標點前後的多餘空格`：整理 `， 。 ！ ？` 這類標點
- `修正英文半形標點後缺少空格`：例如把 `Hello,world` 修正為 `Hello, world`
- `修正常見「呢他」為「呢，他」`：修正某些語音轉文字常見黏字情況
- `保留段落換行`：保留以空白行分隔的段落，不把整篇合成單段

## 目前支援的清理規則

- 將連續空白壓成單一空格
- 移除中文字與中文字之間的空格
- 修正全形標點前後的多餘空格
- 修正英文半形標點後缺少空格
- 修正常見的 `呢他 -> 呢，他`
- 可選擇保留段落換行

## 清理範例

| 原始文字 | 輸出結果 |
| --- | --- |
| `我 是 一 個 學 生` | `我是一個學生` |
| `這 是 ， 一個 測試 ！` | `這是，一個測試！` |
| `Hello,world` | `Hello, world` |
| `他說呢他會來` | `他說呢，他會來` |

## 重新打包 Windows 執行檔

如果你修改了程式，想重新產生 `.exe`，可使用 PyInstaller：

```powershell
pyinstaller .\remove_text_extra_spaces_v3.spec
```

打包完成後，執行檔會出現在：

```text
dist\remove_text_extra_spaces_v3.exe
```

## 備註

- 檔案模式輸出檔案會以 UTF-8 編碼寫出
- 讀取輸入檔時，會優先嘗試 UTF-8，並對常見 Windows 編碼提供 fallback
