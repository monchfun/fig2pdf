import os
import gradio as gr
import subprocess
import json
import uuid
from process_pdf import process_pdf_files
from werkzeug.utils import secure_filename

def process_files(pdf_file, json_file):
    """处理上传的PDF和JSON文件"""
    try:
        # 创建唯一的上传目录
        upload_id = str(uuid.uuid4())
        upload_dir = os.path.join('uploads', upload_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        pdf_filename = secure_filename(os.path.basename(pdf_file))
        json_filename = secure_filename(os.path.basename(json_file))
        
        pdf_path = os.path.join(upload_dir, pdf_filename)
        json_path = os.path.join(upload_dir, json_filename)
        
        # 保存文件内容
        with open(pdf_path, 'wb') as f:
            with open(pdf_file, 'rb') as src:
                f.write(src.read())
        with open(json_path, 'wb') as f:
            with open(json_file, 'rb') as src:
                f.write(src.read())
        
        # 处理PDF文件 - 添加文字转曲线参数
        processing_result = process_pdf_files(pdf_path, json_path, upload_dir, convert_text_to_curves=True)
        
        if processing_result["success"]:
            # 返回文件路径供Gradio文件组件使用
            result_files = []
            result_message = "✅ 处理成功！\n\n" + processing_result['message']
            
            if processing_result["output_cmyk_pdf"]:
                result_files.append(processing_result["output_cmyk_pdf"])
            
            if processing_result["output_final_pdf"]:
                result_files.append(processing_result["output_final_pdf"])
            
            return result_message, result_files
        else:
            return f"❌ 处理失败！\n\n{processing_result['message']}", None
            
    except Exception as e:
        return f"❌ 发生错误！\n\n{str(e)}", None

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
                pdf_input = gr.File(
                    label="上传PDF文件",
                    file_types=[".pdf"],
                    file_count="single"
                )
                json_input = gr.File(
                    label="上传颜色映射JSON",
                    file_types=[".json"],
                    file_count="single"
                )
                
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
                output_files = gr.Files(
                    label="下载文件",
                    file_count="multiple"
                )
        
        # 处理逻辑
        process_btn.click(
            fn=process_files,
            inputs=[pdf_input, json_input],
            outputs=[output_text, output_files]
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