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
├── backend/
│   ├── app.py              # Web 应用程序主文件
│   ├── process_pdf.py      # 核心 PDF 处理脚本
│   ├── templates/          # HTML 模板文件
│   └── uploads/            # 上传文件存储目录
├── figma-plugin/           # Figma 插件目录
├── README.md               # 项目说明
└── PROJECT_LOG.md          # 项目日志
```

---

## 5. 使用方式

### 方式一：Web 应用（推荐）

1.  **进入 Web 应用目录**：
    ```bash
    cd backend
    ```

2.  **启动 Web 应用**：
    为了确保使用正确的 Python 环境和依赖，推荐使用项目自带的虚拟环境。

    *   **方式 A (推荐):** 直接执行虚拟环境中的 Python
        ```bash
        ./venv/bin/python app.py
        ```
    *   **方式 B:** 先激活虚拟环境，再运行
        ```bash
        source venv/bin/activate
        python app.py
        ```
    如果 `python` 命令不起作用，请尝试 `python3`。

3.  **访问应用**：在浏览器中打开 `http://localhost:5000` (或您在启动时指定的其他端口)。

4.  **上传文件**：根据页面提示，上传从 Figma 导出的 PDF 文件和对应的 `color_mapping.json` 文件。

5.  **下载结果**：处理完成后，历史记录会自动更新，您可以直接下载转换后的印刷级 PDF 文件。

### 方式二：命令行脚本（开发者/高级用户）

`process_pdf.py` 脚本也可以独立于 Web 应用，在命令行中直接运行。这对于批量处理或集成到其他自动化流程中非常有用。

1.  **准备文件**：将需要处理的 PDF 文件和对应的 `color_mapping.json` 文件放在任意位置。

2.  **运行脚本**：打开终端，进入 `backend` 目录，然后执行以下命令，将 `<input_pdf_path>` 和 `<color_mapping_path>` 替换为您的实际文件路径。
    ```bash
    cd backend
    cd backend
    ./venv/bin/python process_pdf.py <input_pdf_path> <color_mapping_path>
    ```
    例如:
    ```bash
    ./venv/bin/python process_pdf.py /path/to/my/design.pdf /path/to/my/colors.json
    ```

3.  **获取成品**：脚本执行成功后，会在您执行命令的目录下生成最终文件 `*_modern_print.pdf`。

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