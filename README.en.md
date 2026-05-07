# Remove Text Extra Spaces v3

[繁體中文](README.md) | [English](README.en.md)

`Remove Text Extra Spaces v3` is a small Windows-oriented utility for cleaning messy text from AI speech-to-text output, OCR extraction, and mixed Chinese/English TXT files.

It can remove excessive spaces, normalize common punctuation patterns, and work in two modes: batch file processing and direct paste-and-clean text input.

Project repository: [taoyutsun/remove-text-extra-spaces](https://github.com/taoyutsun/remove-text-extra-spaces)

Related articles:

- [AI 語音轉文字格式太亂？獨創免安裝小工具「Remove Text Extra Spaces」幫你一鍵搞定！](https://taoyutsun.blogspot.com/2025/02/Remove-Text-Extra-Spaces.html)
- [從雲端 AI LLM 到本地 AI Agent：我用 Vibe Coding 升級 Remove Text Extra Spaces](https://taoyutsun.blogspot.com/2026/04/cloud-ai-llm-to-local-ai-agent-vibe-coding-upgrade-remove-text-extra-spaces.html)

## What Is New In v3

- A GUI workflow for both file mode and paste-text mode.
- Cleaner handling of mixed Chinese and English text.
- Options for punctuation cleanup and whitespace normalization.
- Drag-and-drop support when the optional dependency is installed.
- A more practical workflow for cleaning long transcript or OCR text files.

## Use Cases

This tool is useful when you need to clean:

- AI transcription output with unnatural spacing.
- OCR text copied from images or PDF files.
- Mixed Chinese/English notes.
- TXT files with line breaks, extra spaces, and inconsistent punctuation.
- Draft content before sending it to an editor, AI model, or publishing workflow.

## Download And Deployment

### Option 1: Download The Windows Executable

For general users, download the packaged Windows executable from GitHub Releases if available:

[https://github.com/taoyutsun/remove-text-extra-spaces/releases](https://github.com/taoyutsun/remove-text-extra-spaces/releases)

This is the simplest way to use the tool without setting up Python.

### Option 2: Run From Source

Requirements:

- Python 3.10 or newer
- `tkinterdnd2`, optional but recommended for drag-and-drop support

Clone the repository:

```powershell
git clone https://github.com/taoyutsun/remove-text-extra-spaces.git
cd remove-text-extra-spaces
```

Install dependency and run:

```powershell
python -m pip install tkinterdnd2
python .\remove_text_extra_spaces_v3.py
```

## How To Use

### 1. File Mode

Choose one or more text files, select the cleanup options, and run the conversion. The tool creates cleaned output files according to the application settings.

### 2. Paste Text Mode

Paste short text into the GUI, apply cleanup, and copy the result.

### 3. Cleanup Options

The GUI exposes options for common cleanup rules, such as:

- Removing repeated spaces.
- Fixing spacing around Chinese punctuation.
- Cleaning line breaks.
- Normalizing mixed Chinese/English text.
- Removing redundant blank lines.

## Example

Input:

```text
這 是 一 段  被 OCR  拆 得 很 亂 的文字 。
AI  transcript   may also contain   too many spaces .
```

Output:

```text
這是一段被 OCR 拆得很亂的文字。
AI transcript may also contain too many spaces.
```

## Build A Windows Executable

If you want to package the app yourself, use the build script or PyInstaller configuration included in the repository. The exact command may depend on your Python environment.

## Notes

This tool is intentionally focused on practical text cleanup. It is not a full natural-language rewriting tool and does not send your text to any cloud service by default.

## License

See the repository license for details.
