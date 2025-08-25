import os
import gradio as gr
import subprocess
import json
import uuid
from process_pdf import process_pdf_files
from werkzeug.utils import secure_filename

def process_files(pdf_file, json_file):
    return "Hello from dummy process_files!"

def create_gradio_interface():
    """创建Gradio界面"""
    with gr.Blocks(
        title="Figma2PDF - PDF颜色处理工具",
        theme=gr.themes.Soft()
    ) as demo:
        gr.Markdown("""
        # 🎨 Figma2PDF
        ### 专业的PDF颜色处理工具
        
        上传Figma导出的PDF文件和颜色映射JSON文件，进行专业的CMYK颜色转换和印刷优化。
        """)
        
        with gr.Row():
            with gr.Column():
                # pdf_input = gr.File(
                #     label="上传PDF文件",
                #     file_types=[".pdf"],
                #     file_count="single",
                #     type="filepath"
                # )
                # json_input = gr.File(
                #     label="上传颜色映射JSON",
                #     file_types=[".json"],
                #     file_count="single",
                #     type="filepath"
                # )
                
                process_btn = gr.Button(
                    "🚀 开始处理PDF",
                    variant="primary"
                )
            
            with gr.Column():
                output_text = gr.Textbox(
                    label="处理结果",
                    value="等待处理文件...",
                    lines=10
                )
                # output_files = gr.Files(
                #     label="下载文件",
                #     file_count="multiple"
                # )
        
        # 处理逻辑
        process_btn.click(
            fn=process_files,
            inputs=[], # Removed inputs
            outputs=[output_text] # Removed output_files
        )
    
    return demo

if __name__ == "__main__":
    # 确保上传目录存在
    os.makedirs('uploads', exist_ok=True)
    
    # 启动Gradio应用
    demo = create_gradio_interface()
    
    # 获取Render分配的端口，如果没有则使用默认端口
    port = int(os.environ.get("PORT", 7860))
    
    # 在Render上需要使用0.0.0.0来监听所有接口
    try:
        demo.launch(server_name="0.0.0.0", server_port=port, share=False, show_error=True)
    except Exception as e:
        print(f"启动错误: {e}")
        print("尝试使用prevent_thread_lock模式...")
        demo.launch(server_name="0.0.0.0", server_port=port, share=False, show_error=True, prevent_thread_lock=True)