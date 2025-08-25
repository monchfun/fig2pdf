# Figma PDF 到印刷级 CMYK 转换器

## 1. 项目目标

本工具旨在自动化一个核心的印刷前准备流程：将从 Figma 导出的标准 RGB 色彩空间的 PDF 文件，精确地转换为符合印刷要求的、使用指定 CMYK 颜色值的 PDF 文件。

最终输出的文件将保留所有文字和形状的矢量特性（不会变成图片），并确保颜色值100%对应，可直接交付印刷厂。

---

## 2. 技术流程

为了解决“精确颜色”和“保留矢量”两大核心问题，我们采用了一个稳定可靠的两步流程：

**第一步：使用 Python (pikepdf) 进行精确颜色替换**

- **目的**：将源文件中的特定 RGB 颜色，精确地替换为目标 CMYK 颜色。
- **原理**：此步骤直接在 PDF 文件的底层内容流中操作。脚本会查找并匹配原始的 RGB 颜色定义（例如，`R:8, G:77, B:232`），然后将其整个定义直接替换为指定的 CMYK 颜色定义（例如，`C:95, M:60, Y:0, K:20`）。这一步确保了颜色映射的100%准确性，并生成一个临时的、颜色正确但未经最终处理的中间文件 (`*_cmyk.pdf`)。

**第二步：使用 Ghostscript 进行标准化和保值处理**

- **目的**：将中间文件处理成最终的、兼容性强的印刷文件，同时确保第一步的颜色值不被改动。
- **原理**：此步骤调用 Ghostscript，但通过使用关键参数 `-dUseCIEColor=false` 来**禁用其内置的自动色彩管理引擎**。这可以防止 Ghostscript “自作主张”地修改我们手动设置的精确CMYK值。同时，此步骤也会处理好PDF的版本兼容性等问题，最终输出一个保留了矢量特性和精确颜色的现代化印刷PDF (`*_modern_print.pdf`)。

---

## 3. 环境要求

在运行此脚本前，请确保您的系统中已安装以下软件：

1.  **Python 3**: [https://www.python.org/](https://www.python.org/)
2.  **pikepdf 库**: 通过 pip 安装。
    ```bash
    pip install pikepdf
    ```
3.  **Ghostscript**: 必须安装，并确保 `gs` 命令在系统的环境变量 `PATH` 中可用。
    -   **macOS (Homebrew)**: `brew install ghostscript`
    -   **Windows/Linux**: 从 [官网下载](https://www.ghostscript.com/releases/gsdnld.html)

---

## 4. 文件结构

```
/fig2pdf/
├── process_pdf.py          # 核心执行脚本
├── color_mapping.json      # 颜色映射配置文件
├── PPT.pdf                 # 【输入】您的原始PDF文件
├── PPT_cmyk.pdf            # 【中间】仅替换了颜色的临时文件
└── PPT_modern_print.pdf    # 【输出】最终的印刷文件
```

---

## 5. 使用方式

1.  **放置文件**：将您从 Figma 导出的 PDF 文件放入此文件夹，并将其重命名为 `PPT.pdf`（或者在 `process_pdf.py` 脚本中修改 `INPUT_PDF` 变量的值）。

2.  **配置颜色**：打开 `color_mapping.json` 文件。这是一个包含映射规则的列表。根据您的设计稿，修改或添加颜色条目。
    -   `rgb_255`: 您在 Figma 中使用的原始 RGB 值 (0-255)。
    -   `cmyk_100`: 您希望在最终印刷品中呈现的、精确的 CMYK 值 (0-100)。
    ```json
    {
      "mappings": [
        {
          "comment": "The main blue color used in titles and diagrams",
          "rgb_255": [8, 77, 232],
          "cmyk_100": [95, 60, 0, 20]
        },
        {
          "comment": "The red color for 'abnormal' paths in the diagram",
          "rgb_255": [237, 85, 85],
          "cmyk_100": [0, 80, 65, 0]
        }
      ]
    }
    ```

3.  **运行脚本**：打开终端（命令行工具），进入当前文件夹 (`/Users/monch/fig2pdf`)，然后执行以下命令：
    ```bash
    python3 process_pdf.py
    ```

4.  **获取成品**：脚本执行成功后，文件夹内会生成最终文件 `PPT_modern_print.pdf`。

---

## 6. Figma 插件设置

本仓库包含一个 Figma 插件，用于辅助 PDF 导出流程。要设置和运行此插件，请遵循以下步骤：

1.  **进入插件目录**：
    ```bash
    cd figma-plugin
    ```

2.  **安装依赖**：
    ```bash
    npm install
    ```
    这将安装插件所需的所有 Node.js 依赖项。

3.  **构建插件 (如果需要)**：
    如果插件有 TypeScript 源文件 (`.ts`)，你可能需要将其编译为 JavaScript (`.js`)。通常，`package.json` 中会定义一个构建脚本。请查阅 `figma-plugin/package.json` 中的 `scripts` 部分，例如：
    ```bash
    npm run build
    ```
    (请根据实际情况调整此命令)

4.  **在 Figma 中加载插件**：
    -   打开 Figma 桌面应用。
    -   进入 "Plugins" > "Development" > "Import plugin from manifest..."。
    -   选择 `figma-plugin` 目录下的 `manifest.json` 文件。
    -   插件现在应该可以在 Figma 中运行了。