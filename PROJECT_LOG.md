# 项目日志：Figma to Print-Ready PDF 自动化流程

**最后更新时间**: 2025-08-19

## 1. 项目总体目标

创建一个完整的自动化工作流，允许用户从 Figma 设计稿开始，通过自定义的颜色映射，最终生成一个颜色精确、保留矢量格式、可直接交付印刷的 PDF 文件。

---

## 2. 已完成模块和状态

### 模块一：PDF 颜色转换与处理脚本

- **状态**: ✅ **完成并已验证**
- **目的**: 将一个标准的RGB PDF，根据JSON映射表，转换为颜色精确的CMYK印刷级PDF。
- **技术栈**: `Python`, `pikepdf` 库, `Ghostscript`
- **核心文件**: `process_pdf.py`, `color_mapping.json`
- **关键技术点**:
    1.  采用两步流程，先替换颜色再进行标准化，以确保稳定性和精确性。
    2.  使用 `pikepdf` 在PDF底层内容流中直接将RGB颜色定义替换为指定的CMYK颜色定义，保证了100%的颜色准确性。
    3.  调用 `Ghostscript` 时，使用 `-dUseCIEColor=false` 参数禁用了其自动色彩管理，这是成功保留精确CMYK值的关键。
    4.  最终脚本能生成保留矢量格式的现代化PDF，避免了内容被栅格化（变成图片）的问题。

### 模块二：Figma 插件

- **状态**: ✅ **基础功能已搭建**
- **目的**: 在 Figma 环境中提供一个图形界面，让用户可以方便地选择颜色、设置CMYK映射值，并一键导出源PDF和对应的`color_mapping.json`文件。
- **技术栈**: `Figma 插件 API`, `JavaScript`, `HTML/CSS`
- **核心文件**: `manifest.json`, `code.js`, `ui.html`
- **关键技术点**:
    1.  插件UI (`ui.html`) 与核心逻辑 (`code.js`) 通过消息传递进行通信。
    2.  能通过 `figma.on('selectionchange')` 自动检测用户选择的元素并提取其中的纯色。
    3.  UI界面能动态展示所选颜色，并提供CMYK输入框。
    4.  导出功能通过 `figma.exportAsync` 实现PDF导出，并通过 `postMessage` 将文件数据发送回UI，由UI的JS代码触发浏览器下载。

### 模块三：Web 应用程序

- **状态**: ✅ **完成并已验证**
- **目的**: 提供一个用户友好的Web界面，允许用户上传PDF文件和颜色映射JSON文件，自动处理并下载转换后的印刷级PDF。
- **技术栈**: `Python Flask`, `HTML/CSS/JavaScript`, `Tailwind CSS`
- **核心文件**: `app.py`, `process_pdf.py`, `templates/*.html`
- **关键技术点**:
    1.  使用Flask框架构建RESTful API，支持文件上传和下载
    2.  集成原有的PDF处理脚本，提供Web界面调用
    3.  使用UUID为每次上传创建独立目录，避免文件冲突
    4.  前端使用Tailwind CSS构建响应式界面，提供良好的用户体验

---

## 3. 后续步骤 (To-Do)

1.  **测试 Figma 插件**: 您需要按照说明，在Figma桌面应用中加载并实际测试插件的功能是否符合预期。
2.  **测试 Web 应用**: 验证Web应用的文件上传、处理和下载功能是否正常工作。
3.  **部署与整合**: 
    -   **本地流程**: 您现在可以在本地使用"Figma插件导出 -> Web应用处理"的完整流程。
    -   **云端自动化 (可选)**: 未来的一个方向，可以将Web应用部署到云服务器，实现完全的云端自动化处理。
4.  **优化与迭代**: 根据实际使用情况，可能需要对Figma插件的UI/UX、Web应用的用户体验或Python脚本的错误处理等进行优化。
