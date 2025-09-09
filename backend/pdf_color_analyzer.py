import pikepdf
import json
import os
from collections import Counter

def analyze_pdf_colors(input_pdf_path):
    """分析PDF文件中使用的颜色值"""
    colors_found = []
    color_operators = []
    
    try:
        with pikepdf.open(input_pdf_path) as pdf:
            print(f"分析PDF文件: {input_pdf_path}")
            print(f"总页数: {len(pdf.pages)}")
            
            for i, page in enumerate(pdf.pages):
                print(f"\n--- 第 {i+1} 页 ---")
                
                try:
                    page_colors = []
                    page_operators = []
                    
                    for operands, operator in pikepdf.parse_content_stream(page):
                        op_str = str(operator)
                        
                        # 记录颜色操作符
                        if op_str in ('rg', 'RG', 'sc', 'SC', 'scn', 'SCN', 'k', 'K'):
                            page_operators.append(op_str)
                            
                            if op_str in ('rg', 'RG', 'sc', 'SC', 'scn', 'SCN') and len(operands) >= 3:
                                r, g, b = [float(c) for c in operands[:3]]
                                rgb_int = (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))
                                page_colors.append(rgb_int)
                                colors_found.append(rgb_int)
                                color_operators.append(op_str)
                                
                            elif op_str in ('k', 'K') and len(operands) >= 4:
                                c, m, y, k = [float(c) for c in operands[:4]]
                                cmyk_int = (int(round(c * 100)), int(round(m * 100)), int(round(y * 100)), int(round(k * 100)))
                                page_colors.append(f"CMYK({cmyk_int})")
                    
                    if page_colors:
                        print(f"  发现的颜色值: {list(set(page_colors))}")
                        print(f"  使用的操作符: {list(set(page_operators))}")
                    else:
                        print("  未发现RGB颜色定义")
                        
                except Exception as e:
                    print(f"  处理页面时出错: {e}")
    
    except Exception as e:
        print(f"打开PDF文件时出错: {e}")
        return
    
    # 统计颜色使用情况
    if colors_found:
        print(f"\n=== 颜色统计 ===")
        color_counts = Counter(colors_found)
        print(f"总共有 {len(color_counts)} 种不同的RGB颜色:")
        
        for color, count in color_counts.most_common():
            print(f"  RGB{color}: 出现 {count} 次")
            
        # 显示操作符统计
        op_counts = Counter(color_operators)
        print(f"\n操作符统计:")
        for op, count in op_counts.most_common():
            print(f"  {op}: {count} 次")
    else:
        print("\n未发现任何RGB颜色值")

def compare_with_mappings(colors_found, mapping_file_path):
    """将找到的颜色与映射文件进行比较"""
    try:
        with open(mapping_file_path, 'r') as f:
            mappings_data = json.load(f)['mappings']
    except Exception as e:
        print(f"读取映射文件时出错: {e}")
        return
    
    print(f"\n=== 与映射文件对比 ===")
    print(f"映射文件中的颜色:")
    
    mapping_colors = []
    for item in mappings_data:
        rgb = tuple(item['rgb_255'])
        mapping_colors.append(rgb)
        print(f"  RGB{rgb} -> CMYK{item['cmyk_100']}")
    
    print(f"\n匹配分析:")
    matched_colors = []
    unmatched_colors = []
    
    for color in set(colors_found):
        if color in mapping_colors:
            matched_colors.append(color)
            print(f"  ✓ RGB{color} - 找到匹配")
        else:
            # 检查是否有接近的颜色
            close_matches = []
            for mapping_color in mapping_colors:
                distance = sum(abs(a - b) for a, b in zip(color, mapping_color))
                if distance <= 30:  # 容差为30
                    close_matches.append((mapping_color, distance))
            
            if close_matches:
                close_matches.sort(key=lambda x: x[1])
                closest = close_matches[0]
                print(f"  ⚠ RGB{color} - 接近映射颜色 RGB{closest[0]} (距离: {closest[1]})")
            else:
                unmatched_colors.append(color)
                print(f"  ✗ RGB{color} - 无匹配")
    
    print(f"\n总结:")
    print(f"  PDF中的颜色总数: {len(set(colors_found))}")
    print(f"  完全匹配的颜色: {len(matched_colors)}")
    print(f"  不匹配的颜色: {len(unmatched_colors)}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python pdf_color_analyzer.py <pdf_file_path> [mapping_file_path]")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    mapping_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(pdf_file):
        print(f"PDF文件不存在: {pdf_file}")
        sys.exit(1)
    
    print("PDF颜色分析工具")
    print("=" * 50)
    
    colors_found = analyze_pdf_colors(pdf_file)
    
    if mapping_file and os.path.exists(mapping_file):
        compare_with_mappings(colors_found, mapping_file)
    elif mapping_file:
        print(f"\n映射文件不存在: {mapping_file}")