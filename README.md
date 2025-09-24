# Figma PDF 到印刷级 CMYK 转换器

## 1. 项目目标

这是一个全栈Web应用，旨在自动化一个核心的印刷前准备流程：将从 Figma 导出的标准 RGB 色彩空间的 PDF 文件，精确地转换为符合印刷要求的、使用指定 CMYK 颜色值的 PDF 文件。

应用通过一个现代化的 Vue.js 前端界面和强大的 Python 后端，确保最终输出的文件保留所有文字和形状的矢量特性，并确保颜色值100%对应，可直接交付印刷厂。

---

## 2. 技术栈

*   **前端**:
    *   **框架**: Vue.js 3 (使用组合式 API)
    *   **构建工具**: Vite
    *   **UI**: Tailwind CSS, shadcn-vue
    *   **PDF 预览**: `vue-pdf-embed`

*   **后端**:
    *   **框架**: Flask
    *   **PDF 颜色处理**: `pikepdf`
    *   **PDF 标准化**: Ghostscript
    *   **Web 服务器**: Gunicorn (生产), Flask Dev Server (开发)

---

## 3. 环境要求

在运行此项目前，请确保您的系统中已安装以下软件：

*   **Node.js**: v18 或更高版本。 [下载地址](https://nodejs.org/)
*   **Yarn**: v1.22 或更高版本。 [安装指南](https://classic.yarnpkg.com/en/docs/install)。如果未安装，请先安装 Yarn。
*   **Python 3**: v3.8 或更高版本。 [下载地址](https://www.python.org/)
*   **Ghostscript**: 必须安装，并确保 `gs` 命令在系统的环境变量 `PATH` 中可用。
    *   **macOS (Homebrew)**: `brew install ghostscript`
    *   **Windows/Linux**: 从 [官网下载](https://www.ghostscript.com/releases/gsdnld.html)

---

## 4. 文件结构

```
/fig2pdf/
├── backend/                # Python Flask 后端
│   ├── app.py              # Web 应用主文件
│   ├── process_pdf.py      # 核心 PDF 处理脚本
│   ├── requirements.txt    # Python 依赖
│   ├── venv/               # Python 虚拟环境
│   └── uploads/            # 上传文件存储目录

├── vue-app/                # Vue.js 前端
│   ├── src/                # 源代码
│   ├── public/             # 公共静态资源
│   ├── package.json        # Node.js 依赖
│   └── vite.config.js      # Vite 配置文件
├── README.md               # 项目说明
└── PROJECT_LOG.md          # 项目日志
```

---

## 5. 开发环境启动指南

为了在本地运行此项目，你需要分别启动后端服务和前端开发服务器。

### 第一步：启动后端服务 (Flask)

1.  **进入后端目录**:
    ```bash
    cd backend
    ```

2.  **创建并激活虚拟环境** (如果第一次运行):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安装 Python 依赖**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **启动后端服务器**:
    ```bash
    python app.py
    ```
    服务将默认在 `http://localhost:5001` 上运行。

### 第二步：启动前端服务 (Vue)

1.  **打开一个新的终端窗口**。

2.  **进入前端目录**:
    ```bash
    cd vue-app
    ```

3.  **安装 Node.js 依赖** (如果第一次运行，请确保已安装 Yarn):
    ```bash
    yarn install
    ```

4.  **启动前端开发服务器**:
    ```bash
    yarn dev
    ```
    服务将默认在 `http://localhost:5173` 上运行。

### 第三步：访问应用

一切就绪！在浏览器中打开前端服务的地址 (`http://localhost:5173`) 即可访问和使用该工具。前端应用会自动连接到在 `5001` 端口上运行的后端服务。

---

## 6. 核心技术流程 (后端)

为了解决“精确颜色”和“保留矢量”两大核心问题，我们采用了一个稳定可靠的两步流程：

1.  **使用 Python (pikepdf) 进行精确颜色替换**: 在 PDF 文件的底层内容流中，将源文件中的特定 RGB 颜色，精确地替换为目标 CMYK 颜色，确保颜色映射的100%准确性。

2.  **使用 Ghostscript 进行标准化和保值处理**: 调用 Ghostscript，但通过禁用其内置的自动色彩管理引擎 (`-dUseCIEColor=false`)，来防止我们手动设置的精确CMYK值被改动。同时处理PDF的兼容性问题，最终输出保留矢量特性和精确颜色的现代化印刷PDF。


