"""Script to generate bao_cao_tong_nhom.docx with standardized Times New Roman font, easy-to-read typography, and updated roles (Nguyen Dinh Anh as Team Leader, Phu Anh at 28%)."""
import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_font_times(run, font_name="Times New Roman", size_pt=11, bold=False, italic=False, color_rgb=None):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb
    rPr = run._r.get_or_add_rPr()
    rFonts = parse_xml(
        f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" '
        f'w:cs="{font_name}" w:eastAsia="{font_name}"/>'
    )
    rPr.append(rFonts)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="D0D7DE", sz="6"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_heading_1(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(16)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    set_font_times(r, size_pt=14, bold=True, color_rgb=RGBColor(0x00, 0x33, 0x66)) # Navy
    return h

def add_heading_2(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    set_font_times(r, size_pt=12.5, bold=True, color_rgb=RGBColor(0x00, 0x5A, 0x9C)) # Dark Blue
    return h

def add_heading_3(doc, text):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(9)
    h.paragraph_format.space_after = Pt(3)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    set_font_times(r, size_pt=11.5, bold=True, color_rgb=RGBColor(0x22, 0x22, 0x22))
    return h

def add_body_p(doc, text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(space_after)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_font_times(r_pre, size_pt=11, bold=True, color_rgb=RGBColor(0x1B, 0x36, 0x5D))
        
    r = p.add_run(text)
    set_font_times(r, size_pt=11, color_rgb=RGBColor(0x22, 0x22, 0x22))
    return p

def add_bullet_p(doc, text, bold_title=None):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(4)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    r_bullet = p.add_run("• ")
    set_font_times(r_bullet, size_pt=11, bold=True, color_rgb=RGBColor(0x00, 0x5A, 0x9C))
    
    if bold_title:
        r_title = p.add_run(bold_title)
        set_font_times(r_title, size_pt=11, bold=True, color_rgb=RGBColor(0x1B, 0x36, 0x5D))
        
    r_txt = p.add_run(text)
    set_font_times(r_txt, size_pt=11, color_rgb=RGBColor(0x22, 0x22, 0x22))
    return p

def add_image_with_caption(doc, img_path, caption, width=Inches(5.5)):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(3)
        doc.add_picture(img_path, width=width)
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run(caption)
        set_font_times(r_cap, size_pt=9.5, italic=True, color_rgb=RGBColor(0x55, 0x55, 0x55))

def build_master_report(output_path):
    doc = docx.Document()
    
    # Set default style font
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(11)
    style.paragraph_format.line_spacing = 1.25
    style.paragraph_format.space_after = Pt(6)
    
    # Page setup: Margins 1 inch (2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    img_dir = r"C:\Users\ADMIN\Desktop\fire_detection_ai-main\docs\extracted_images"
    
    # ══════════════════════════════════════════════════════════════
    # ─── TRANG BÌA (COVER PAGE) ───
    # ══════════════════════════════════════════════════════════════
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_inst.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO\nTRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG VIỆT - HÀN (VKU)\n")
    set_font_times(r, size_pt=12, bold=True, color_rgb=RGBColor(0x00, 0x33, 0x66))
    
    r2 = p_inst.add_run("KHOA KỸ THUẬT MÁY TÍNH VÀ ĐIỆN TỬ\n")
    set_font_times(r2, size_pt=13, bold=True, color_rgb=RGBColor(0xB2, 0x22, 0x22))
    
    r_div = p_inst.add_run("━━━━━━━━━━━━━━━━━━━ ◆ ━━━━━━━━━━━━━━━━━━━\n\n\n")
    set_font_times(r_div, size_pt=10, color_rgb=RGBColor(0x88, 0x88, 0x88))
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.line_spacing = 1.25
    
    r_subt = p_title.add_run("BÁO CÁO TỔNG KẾT ĐỒ ÁN NHÓM CHUYÊN NGÀNH\n\n")
    set_font_times(r_subt, size_pt=14, bold=True, color_rgb=RGBColor(0x55, 0x55, 0x55))
    
    r_main = p_title.add_run("NGHIÊN CỨU VÀ XÂY DỰNG HỆ THỐNG GIÁM SÁT,\nCẢNH BÁO SỚM CHÁY & KHÓI BẰNG TRÍ TUỆ NHÂN TẠO\n(FIREEYES AI — YOLO11n & FASTAPI & SQLITE v2)\n\n\n")
    set_font_times(r_main, size_pt=17.5, bold=True, color_rgb=RGBColor(0x00, 0x33, 0x66))
    
    # Bảng thông tin sinh viên thực hiện ở trang bìa
    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_info.paragraph_format.left_indent = Inches(1.3)
    p_info.paragraph_format.line_spacing = 1.3
    
    r_info = p_info.add_run(
        "Nhóm sinh viên thực hiện:  Nhóm 4 thành viên\n"
        "1. Nguyễn Đình Anh        — Trưởng nhóm (Backend API, MVC Controller & CLI)\n"
        "2. Phú Anh                — Thành viên chính (Kiến trúc MVC, Frontend SPA & AI)\n"
        "3. Huy Hoàng              — Thành viên (Phân tích & Thiết kế CSDL SQLite v2)\n"
        "4. Thùy Ngân              — Thành viên (Thị giác máy tính & Huấn luyện YOLO11n)\n\n"
        "Ngành đào tạo:            Công nghệ Thông tin / Kỹ thuật Máy tính\n"
        "Khoa:                     Khoa Kỹ thuật Máy tính và Điện tử\n"
        "Khóa học:                 2024 - 2028 (Lớp 24IT)\n"
    )
    set_font_times(r_info, size_pt=11, color_rgb=RGBColor(0x22, 0x22, 0x22))
    
    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.space_before = Pt(36)
    r_loc = p_loc.add_run("ĐÀ NẴNG, THÁNG 10 NĂM 2026")
    set_font_times(r_loc, size_pt=11.5, bold=True, color_rgb=RGBColor(0x44, 0x44, 0x44))
    
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════
    # ─── BẢNG ĐÁNH GIÁ ĐÓNG GÓP THÀNH VIÊN (MỤC BẮT BUỘC) ───
    # ══════════════════════════════════════════════════════════════
    h_eval = doc.add_paragraph()
    h_eval.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h_eval.paragraph_format.space_before = Pt(6)
    h_eval.paragraph_format.space_after = Pt(4)
    r_he = h_eval.add_run("📊 BẢNG ĐÁNH GIÁ ĐÓNG GÓP CỦA TỪNG THÀNH VIÊN TRONG ĐỒ ÁN\n(BẢN CỨNG BẮT BUỘC KHI NỘP VÀ BÁO CÁO ĐỒ ÁN)\n")
    set_font_times(r_he, size_pt=13.5, bold=True, color_rgb=RGBColor(0xB2, 0x22, 0x22))
    
    p_notice = doc.add_paragraph()
    p_notice.paragraph_format.line_spacing = 1.2
    p_notice.paragraph_format.space_after = Pt(8)
    p_notice.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_n = p_notice.add_run(
        "📌 Căn cứ quy chế đánh giá đồ án nhóm của Khoa và Nhà trường:\n"
        "• Trước khi thi, trong bản cứng báo cáo nộp bắt buộc phải có Bảng đánh giá đóng góp của từng thành viên kèm tỷ lệ % và chữ ký xác nhận.\n"
        "• Tổng tỷ lệ đóng góp của cả nhóm không vượt quá 100%, không sử dụng số thập phân.\n"
        "• Không được có hơn 50% thành viên có cùng một tỷ lệ đóng góp (Đối với nhóm 4 người: tối đa 2 người có cùng tỷ lệ).\n"
        "• Tỷ lệ % đóng góp phản ánh trung thực khối lượng và mức độ phức tạp của công việc đã hoàn thành."
    )
    set_font_times(r_n, size_pt=10, italic=True, color_rgb=RGBColor(0x44, 0x44, 0x44))
    
    tbl_eval = doc.add_table(rows=5, cols=6)
    tbl_eval.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_eval)
    
    eval_headers = ["STT", "Họ và tên", "Mã SV", "Vai trò & Công việc cụ thể đã thực hiện", "Tỷ lệ %", "Chữ ký"]
    col_w = [Inches(0.4), Inches(1.3), Inches(0.9), Inches(3.0), Inches(0.7), Inches(0.8)]
    
    for i, h in enumerate(eval_headers):
        cell = tbl_eval.cell(0, i)
        cell.width = col_w[i]
        cell.text = h
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=90, bottom=90, left=90, right=90)
        p = cell.paragraphs[0]
        set_font_times(p.runs[0], size_pt=10, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))
        
    members_data = [
        (
            "1",
            "Nguyễn Đình Anh",
            "24IT007",
            "Trưởng nhóm: Điều phối chung tiến độ đồ án; Xây dựng máy chủ Backend RESTful API bằng FastAPI; Hiện thực lớp điều khiển AppController kết nối View và Model theo chuẩn MVC; Quản lý luồng nạp khung hình (Frame Ingestion), vòng đời sự cố cảnh báo (Acknowledge & Resolve Incident); Xây dựng công cụ dòng lệnh quản trị CLI (init, stats, incidents, demo) hỗ trợ UTF-8; Bổ sung kiểm thử hồi quy tự động đạt 26/26 Unit Tests; Tổng hợp và chuẩn hóa báo cáo đồ án nộp Khoa.",
            "26%",
            ""
        ),
        (
            "2",
            "Phú Anh",
            "24IT001",
            "Thành viên chính: Phụ trách kiến trúc tổng thể Full-stack MVC; Thiết kế và xây dựng Web Frontend SPA trực quan (HTML5, Tailwind CSS, Canvas); Hiện thực thuật toán nhận diện ngọn lửa thời gian thực (Real-time Flame Color Physics) và bộ lọc chống báo động giả trên da người & ánh sáng phòng; Hiện thực cơ chế tắt camera phần cứng triệt để (stream.getTracks().stop()); Tích hợp còi hú âm thanh Web Audio và Modal Snapshot; Soạn thảo Tài liệu hướng dẫn kiểm thử toàn diện.",
            "28%",
            ""
        ),
        (
            "3",
            "Huy Hoàng",
            "24IT032",
            "Thành viên: Phân tích yêu cầu và thiết kế Cơ sở dữ liệu SQLite v2 gồm đầy đủ 11 bảng chuẩn 3NF; Thiết lập ràng buộc toàn vẹn dữ liệu (Khóa ngoại, CHECK, UNIQUE, Index có điều kiện idx_one_open_incident, Triggers); Thiết kế luồng giao dịch nguyên tử ACID (BEGIN IMMEDIATE) và cơ chế chống trùng lặp dữ liệu bằng mã băm SHA-256; Xây dựng bộ test CSDL độc lập.",
            "23%",
            ""
        ),
        (
            "4",
            "Thùy Ngân",
            "24IT045",
            "Thành viên: Nghiên cứu lý thuyết và thực nghiệm mô hình thị giác máy tính YOLO11n; Tiền xử lý tập dữ liệu D-Fire (21.527 ảnh); Hiệu chỉnh ngưỡng phân lớp tối ưu F1-score (Calibrated thresholds cho Lửa và Khói); Thiết lập thuật toán cửa sổ trượt xác nhận đa khung hình (Sliding window 3/5 frames); Đánh giá các chỉ số thị giác máy tính (IoU, Precision, Recall, F1, mAP).",
            "23%",
            ""
        ),
    ]
    
    for row_idx, r_data in enumerate(members_data, 1):
        bg = "F7F9FC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(r_data):
            cell = tbl_eval.cell(row_idx, col_idx)
            cell.width = col_w[col_idx]
            cell.text = text
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=90, right=90)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            if col_idx in (0, 1, 4):
                set_font_times(p.runs[0], size_pt=9.5, bold=True, color_rgb=RGBColor(0xB2, 0x22, 0x22) if col_idx == 4 else RGBColor(0x1B, 0x36, 0x5D))
            else:
                set_font_times(p.runs[0], size_pt=9, color_rgb=RGBColor(0x22, 0x22, 0x22))
                
    p_sum = doc.add_paragraph()
    p_sum.paragraph_format.space_before = Pt(8)
    p_sum.paragraph_format.space_after = Pt(12)
    r_sum = p_sum.add_run(
        "👉 TỔNG TỶ LỆ ĐÓNG GÓP: 26% (Đình Anh) + 28% (Phú Anh) + 23% (Huy Hoàng) + 23% (Thùy Ngân) = 100%.\n"
        "(Đạt chuẩn 100%, số nguyên không thập phân, Phú Anh 28% cao hơn Đình Anh 26%, chỉ 2 thành viên cùng tỷ lệ 23% = 50% nhóm đúng quy định).\n"
        "Xác nhận của các thành viên trong nhóm: Toàn bộ thành viên cam kết thực hiện đúng phần việc được phân công."
    )
    set_font_times(r_sum, size_pt=9.5, bold=True, color_rgb=RGBColor(0x00, 0x33, 0x66))
    
    doc.add_page_break()
    
    # ══════════════════════════════════════════════════════════════
    # ─── MỤC LỤC & LỜI MỞ ĐẦU ───
    # ══════════════════════════════════════════════════════════════
    add_heading_1(doc, "MỤC LỤC BÁO CÁO")
    
    toc_items = [
        "LỜI MỞ ĐẦU VÀ ĐẶT VẤN ĐỀ",
        "CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI VÀ KIẾN TRÚC HỆ THỐNG FIREEYES AI",
        "  1.1. Mục tiêu và phạm vi bài toán",
        "  1.2. Mô hình kiến trúc tổng thể MVC (Model - View - Controller)",
        "  1.3. Luồng tương tác dữ liệu khép kín giữa các phân hệ",
        "CHƯƠNG 2: PHÂN HỆ THỊ GIÁC MÁY TÍNH VÀ MÔ HÌNH AI NHẬN DIỆN (Thùy Ngân)",
        "  2.1. Cơ sở lý thuyết phát hiện đối tượng bằng mạng YOLO11n",
        "  2.2. Tập dữ liệu D-Fire Dataset và cấu trúc nhãn chuẩn hóa",
        "  2.3. Hiệu chỉnh ngưỡng phân lớp tối ưu F1-score (Calibrated Thresholds)",
        "  2.4. Thuật toán xác nhận chuỗi khung hình thời gian thực (Sliding Window 3/5 Frames)",
        "  2.5. Các chỉ số toán học đánh giá mô hình thị giác máy tính (IoU, Precision, Recall, F1, mAP)",
        "  2.6. Quy trình 6 bước hoạt động của phân hệ AI",
        "CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ CƠ SỞ DỮ LIỆU (Huy Hoàng)",
        "  3.1. Mục tiêu và phạm vi thiết kế CSDL",
        "  3.2. Yêu cầu lưu trữ và xử lý dữ liệu chuẩn 11 bảng",
        "  3.3. Sơ đồ quan hệ thực thể ERD các bảng nghiệp vụ chính",
        "  3.4. Thiết kế chi tiết các thực thể dữ liệu",
        "  3.5. Ràng buộc toàn vẹn, Trigger và Tối ưu hóa truy vấn",
        "  3.6. Thiết kế giao dịch nguyên tử ACID và cơ chế chống trùng lặp Idempotency",
        "CHƯƠNG 4: PHÁT TRIỂN GIAO DIỆN WEB VÀ TÍCH HỢP HỆ THỐNG (Phú Anh & Đình Anh)",
        "  4.1. Thiết kế Giao diện Giám sát Người dùng (Frontend SPA - Phú Anh phụ trách)",
        "    4.1.1. Giao diện bảng điều khiển Dashboard và giám sát trực tiếp",
        "    4.1.2. Thuật toán thị giác máy tính phân tích màu ngọn lửa thời gian thực (Color Physics)",
        "    4.1.3. Thuật toán bộ lọc loại trừ báo động giả trên da người và tường phòng",
        "    4.1.4. Cơ chế ngắt kết nối phần cứng camera triệt để và còi hú âm thanh",
        "  4.2. Xây dựng Lớp Điều Khiển MVC & RESTful API Backend (Đình Anh phụ trách)",
        "    4.2.1. Hệ thống RESTful API chuẩn hóa bằng FastAPI",
        "    4.2.2. Hiện thực lớp điều khiển AppController theo đúng Class Diagram MVC",
        "    4.2.3. Quản trị hệ thống qua công cụ dòng lệnh CLI hỗ trợ UTF-8",
        "    4.2.4. Xử lý triệt để lỗi CameraUnavailableError trong seed demo",
        "CHƯƠNG 5: CÀI ĐẶT, THỰC NGHIỆM VÀ ĐÁNH GIÁ KẾT QUẢ",
        "  5.1. Môi trường triển khai và vận hành hệ thống",
        "  5.2. Kết quả kiểm thử tự động (26/26 Unit Tests đạt 100%)",
        "  5.3. Kết quả thực nghiệm nhận diện thực tế (Bật lửa, que diêm, ảnh hiện trường)",
        "  5.4. Đánh giá ưu điểm, hạn chế và bài học kinh nghiệm",
        "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN",
        "TÀI LIỆU THAM KHẢO"
    ]
    
    for item in toc_items:
        p_toc = doc.add_paragraph()
        p_toc.paragraph_format.line_spacing = 1.2
        p_toc.paragraph_format.space_after = Pt(2)
        r = p_toc.add_run(item)
        if not item.startswith("  "):
            set_font_times(r, size_pt=10.5, bold=True, color_rgb=RGBColor(0x00, 0x33, 0x66))
        else:
            set_font_times(r, size_pt=10, color_rgb=RGBColor(0x44, 0x44, 0x44))
            
    doc.add_page_break()
    
    # ─── LỜI MỞ ĐẦU ───
    add_heading_1(doc, "LỜI MỞ ĐẦU VÀ ĐẶT VẤN ĐỀ")
    add_body_p(
        doc,
        "Hỏa hoạn luôn là một trong những hiểm họa nghiêm trọng đe dọa trực tiếp đến tính mạng con người, tài sản "
        "và tàn phá cơ sở hạ tầng tại các đô thị, khu dân cư, nhà máy và kho bãi. Theo thống kê của cơ quan PCCC, thời gian vàng "
        "để dập tắt một đám cháy hiệu quả chỉ kéo dài từ 2 đến 3 phút đầu tiên kể từ khi phát sinh. Nếu vượt qua giai đoạn này, "
        "đám cháy sẽ bùng phát dữ dội (Flashover) và việc dập lửa trở nên vô cùng khó khăn, nguy hiểm."
    )
    add_body_p(
        doc,
        "Hiện nay, hầu hết các công trình đều phụ thuộc vào các thiết bị báo cháy truyền thống sử dụng cảm biến vật lý "
        "(cảm biến khói quang điện, cảm biến ion hoặc cảm biến gia tăng nhiệt). Mặc dù có vai trò thiết yếu, các thiết bị này "
        "thường có độ trễ cảnh báo lớn do khói hoặc nhiệt phải tích tụ đủ dày đặc lan tới trần nhà. Trong các không gian rộng lớn, "
        "trần cao hoặc có gió lưu thông, khói bị phân tán khiến cảm biến vật lý phản ứng rất chậm."
    )
    add_body_p(
        doc,
        "Nhằm giải quyết triệt để thách thức trên, đề tài 'Nghiên cứu và xây dựng hệ thống giám sát, cảnh báo sớm cháy & khói bằng "
        "Trí tuệ nhân tạo (FireEyes AI)' được nhóm sinh viên lựa chọn thực hiện. Bằng cách ứng dụng các tiến bộ mới nhất của mạng nơ-ron "
        "tích chập (YOLO11n) kết hợp với các thuật toán thị giác máy tính và kiến trúc phần mềm chuẩn mực (MVC, FastAPI, SQLite v2), "
        "hệ thống có khả năng nhận diện hình ảnh ngọn lửa và vệt khói bốc lên ngay từ những giây đầu tiên qua camera giám sát có sẵn. "
        "Đồng thời, hệ thống giải quyết bài toán chống báo động giả, tự động lưu trữ bằng chứng, và cung cấp giao diện trực quan cho "
        "lực lượng trực ban PCCC giám sát và xử lý tức thời."
    )
    
    # ══════════════════════════════════════════════════════════════
    # ─── CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI VÀ KIẾN TRÚC HỆ THỐNG ───
    # ══════════════════════════════════════════════════════════════
    add_heading_1(doc, "CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI VÀ KIẾN TRÚC HỆ THỐNG FIREEYES AI")
    
    add_heading_2(doc, "1.1. Mục tiêu và phạm vi bài toán")
    add_body_p(
        doc,
        "Hệ thống FireEyes AI tập trung giải quyết bài toán phát hiện đối tượng (Object Detection) thời gian thực cho hai lớp mục tiêu:\n"
        "1. Lửa (Fire): Các ngọn lửa rực sáng, đám cháy mới bùng phát, ngọn lửa từ các nguồn cháy mở.\n"
        "2. Khói (Smoke): Các luồng khói bốc lên từ đám cháy ban đầu, khói xám mờ hoặc đậm đặc."
    )
    add_body_p(
        doc,
        "Phạm vi ứng dụng của hệ thống bao gồm: xử lý nguồn video trực tiếp từ webcam giám sát, luồng video camera IP (RTSP), "
        "và tệp video/ảnh chụp hiện trường. Hệ thống không chỉ dừng lại ở bài toán phân loại ảnh nhị phân (Binary Classification) "
        "mà dự đoán chính xác tọa độ hộp bao (Bounding Box) [xc, yc, w, h] cùng độ tin cậy (Confidence). Để ngăn chặn cảnh báo giả, "
        "hệ thống tích hợp quy tắc xác nhận đa khung hình liên tiếp và lưu vết toàn bộ bằng chứng vào cơ sở dữ liệu."
    )
    
    add_heading_2(doc, "1.2. Mô hình kiến trúc tổng thể MVC (Model - View - Controller)")
    add_body_p(
        doc,
        "Hệ thống được thiết kế và hiện thực tuân thủ chặt chẽ mô hình kiến trúc MVC (Model - View - Controller), phân tách rõ ràng "
        "trách nhiệm giữa các lớp nhằm đảm bảo tính module hóa, dễ mở rộng, bảo trì và kiểm thử độc lập:"
    )
    add_bullet_p(doc, "Được hiện thực bằng ứng dụng web Single Page Application (SPA) giao diện hiện đại (HTML5, Tailwind CSS, Lucide Icons, Canvas API). Lớp View hiển thị thời gian thực màn hình camera AI, 11 thẻ số liệu thống kê CSDL, danh sách cảnh báo sự cố, hộp thoại modal xem bằng chứng ảnh chụp snapshot và hệ thống còi hú cảnh báo bằng âm thanh Web Audio.", "Lớp View (Giao diện người dùng):")
    add_bullet_p(doc, "Đóng vai trò trung gian tiếp nhận yêu cầu từ View, điều phối luồng nghiệp vụ và giao tiếp với Model. Lớp này bao gồm AppController (tại backend/CSDL/controllers/app_controller.py) và hệ thống RESTful API FastAPI (tại backend/api.py), cung cấp đầy đủ các phương thức nghiệp vụ: get_stats(), get_incidents(), run_demo(), record_frame(), acknowledge_incident(), close_incident().", "Lớp Controller (Bộ điều khiển nghiệp vụ):")
    add_bullet_p(doc, "Lớp FireEyesDB (tại backend/CSDL/models/database.py) trực tiếp quản lý cơ sở dữ liệu quan hệ SQLite v2 gồm 11 bảng chuẩn: locations, cameras, contacts, dataset_versions, dataset_samples, annotations, model_versions, frames, detections, incidents, notifications. Đảm bảo toàn vẹn dữ liệu, giao dịch nguyên tử ACID và kiểm soát khóa ngoại.", "Lớp Model (Mô hình dữ liệu):")
    add_bullet_p(doc, "Phân hệ xử lý AI dựa trên mô hình YOLO11n fine-tuned kết hợp thuật toán thị giác máy tính quét phổ màu ngọn lửa thời gian thực (Color Physics Segmentation) và bộ đệm cửa sổ trượt (Sliding Window 3/5 Frames) chống báo động giả.", "Phân hệ Thị giác máy tính AI:")
    
    add_heading_2(doc, "1.3. Luồng tương tác dữ liệu khép kín giữa các phân hệ")
    add_body_p(
        doc,
        "Toàn bộ luồng dữ liệu từ khi camera thu nhận hình ảnh đến khi sự cố được xử lý diễn ra theo chu trình khép kín:"
    )
    add_bullet_p(doc, "Khung hình từ camera được phân tích qua mô hình AI/thuật toán thị giác máy tính để trích xuất các bounding box ngọn lửa và khói.", "1. Thu nhận & Phân tích:")
    add_bullet_p(doc, "Bộ đệm cửa sổ trượt tích lũy trạng thái 5 frame gần nhất. Khi đạt từ 3 frame trở lên, sự kiện được xác nhận chính thức.", "2. Xác nhận đa khung hình:")
    add_bullet_p(doc, "Hệ thống phát còi hú âm thanh, kích hoạt banner đỏ khẩn cấp, chụp ảnh snapshot hiện trường và gửi request ghi nhận tới Controller.", "3. Cảnh báo tức thời & Chụp snapshot:")
    add_bullet_p(doc, "Controller nhận payload, xác thực hash SHA-256 chống trùng lặp, mở giao dịch ghi nguyên tử vào các bảng frames, detections, incidents và notifications.", "4. Ghi nhận giao dịch CSDL:")
    add_bullet_p(doc, "Giao diện tự động cập nhật thẻ thống kê, hiển thị sự cố mới trên bảng nhật ký và cán bộ trực ban thực hiện xác nhận (Acknowledge) hoặc đóng sự cố (Resolve).", "5. Giám sát & Xử lý:")
    
    add_image_with_caption(doc, os.path.join(img_dir, "architecture_diagram.png"), "Hình 1.1: Sơ đồ kiến trúc tổng thể và luồng tương tác các phân hệ trong FireEyes AI")
    
    # ══════════════════════════════════════════════════════════════
    # ─── CHƯƠNG 2: PHÂN HỆ THỊ GIÁC MÁY TÍNH & MÔ HÌNH AI (THÙY NGÂN) ───
    # ══════════════════════════════════════════════════════════════
    add_heading_1(doc, "CHƯƠNG 2: PHÂN HỆ THỊ GIÁC MÁY TÍNH VÀ MÔ HÌNH AI NHẬN DIỆN")
    add_body_p(doc, "Phân hệ do sinh viên Thùy Ngân phụ trách nghiên cứu, huấn luyện và đánh giá thực nghiệm.", bold_prefix="Phụ trách: ")
    
    add_heading_2(doc, "2.1. Cơ sở lý thuyết phát hiện đối tượng bằng mạng YOLO11n")
    add_body_p(
        doc,
        "YOLO (You Only Look Once) là họ mô hình phát hiện đối tượng theo kiến trúc một giai đoạn (Single-stage Object Detection). "
        "Khác với các phương pháp truyền thống hai giai đoạn (như R-CNN, Fast R-CNN cần một bước đề xuất vùng ảnh Region Proposals rồi mới phân loại), "
        "YOLO xem bài toán phát hiện đối tượng như một bài toán hồi quy duy nhất (Regression Problem). Hình ảnh đầu vào được đưa qua mạng nơ-ron "
        "để dự đoán trực tiếp tọa độ bounding box và xác suất lớp đối tượng chỉ trong một lần lan truyền tiến (Single forward pass). "
        "Điều này mang lại tốc độ xử lý vượt trội, đáp ứng hoàn hảo yêu cầu giám sát video thời gian thực."
    )
    add_body_p(
        doc,
        "Trong dự án này, nhóm lựa chọn kiến trúc tiên tiến YOLO11n (bản nano của YOLO11 phát hành bởi Ultralytics). YOLO11n sở hữu cấu trúc "
        "C3k2 và SPPF cải tiến, vừa tối ưu số lượng tham số để có thể chạy mượt mà trên CPU của máy tính thông thường, vừa đạt độ chính xác cao. "
        "Mô hình được khởi tạo từ trọng số tiền huấn luyện yolo11n.pt và tiến hành fine-tuning trên tập dữ liệu chuyên dụng D-Fire."
    )
    
    add_heading_2(doc, "2.2. Tập dữ liệu D-Fire Dataset và cấu trúc nhãn chuẩn hóa")
    add_body_p(
        doc,
        "D-Fire là một trong những bộ dữ liệu chuẩn học máy mã nguồn mở lớn và chất lượng cao nhất hiện nay dành riêng cho bài toán phát hiện "
        "cháy và khói, được thu thập từ nhiều bối cảnh thực tế (trong nhà, ngoài trời, rừng cây, nhà kho, môi trường ánh sáng phức tạp). "
        "Tập dữ liệu được phân chia chặt chẽ thành 3 tập không giao thoa nhau:"
    )
    
    # Bảng dataset D-Fire
    tbl_ds = doc.add_table(rows=4, cols=3)
    tbl_ds.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_ds)
    ds_h = ["Tập dữ liệu (Split)", "Số lượng ảnh", "Tỷ lệ phần trăm"]
    for i, h in enumerate(ds_h):
        cell = tbl_ds.cell(0, i)
        cell.text = h
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        p = cell.paragraphs[0]
        set_font_times(p.runs[0], size_pt=10, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))
        
    ds_rows = [
        ("Tập huấn luyện (Training Set)", "13.950 ảnh", "64,8%"),
        ("Tập kiểm định (Validation Set)", "3.271 ảnh", "15,2%"),
        ("Tập kiểm thử độc lập (Test Set)", "4.306 ảnh", "20,0%"),
    ]
    for r_idx, r_data in enumerate(ds_rows, 1):
        bg = "F7F9FC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, txt in enumerate(r_data):
            cell = tbl_ds.cell(r_idx, c_idx)
            cell.text = txt
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=120, right=120)
            p = cell.paragraphs[0]
            set_font_times(p.runs[0], size_pt=9.5, color_rgb=RGBColor(0x33, 0x33, 0x33))
            
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    
    add_body_p(
        doc,
        "Định dạng nhãn YOLO được chuẩn hóa theo tọa độ tương đối trong khoảng [0, 1] theo công thức: "
        "<class_id> <x_center> <y_center> <width> <height>, trong đó:\n"
        "• class_id: 0 đại diện cho Lớp Lửa (Fire), 1 đại diện cho Lớp Khói (Smoke).\n"
        "• x_center, y_center: Tọa độ tâm của hộp bao chia cho chiều rộng và chiều cao ảnh.\n"
        "• width, height: Chiều rộng và chiều cao của hộp bao chia cho kích thước ảnh."
    )
    
    add_heading_2(doc, "2.3. Hiệu chỉnh ngưỡng phân lớp tối ưu F1-score (Calibrated Thresholds)")
    add_body_p(
        doc,
        "Trong bài toán phát hiện đám cháy thực tế, ngọn lửa và khói có đặc tính vật lý và biểu hiện quang học rất khác biệt: "
        "ngọn lửa có biên độ phát sáng cao, chuyển động nhanh và cục bộ; trong khi khói có tính khuếch tán, không có biên cạnh rõ ràng "
        "và dễ bị nhầm lẫn với mây mù, bụi hoặc hơi nước. Do đó, việc áp dụng cùng một ngưỡng tin cậy mặc định (0.25 hoặc 0.50) cho cả hai lớp "
        "sẽ dẫn đến hiện tượng mất cân bằng giữa Precision và Recall."
    )
    add_body_p(
        doc,
        "Nhóm đã tiến hành thử nghiệm quét ngưỡng (Threshold Tuning) trên toàn bộ tập Validation để tìm ra điểm cực đại của đường cong F1-Score, "
        "kết quả được lưu tại configs/detection_thresholds.json:\n"
        "• Ngưỡng Lửa (Fire Threshold): 0.2633 (Đạt F1-score tối ưu = 0.62)\n"
        "• Ngưỡng Khói (Smoke Threshold): 0.1792 (Đạt F1-score tối ưu = 0.50)"
    )
    
    add_heading_2(doc, "2.4. Thuật toán xác nhận chuỗi khung hình thời gian thực (Sliding Window 3/5 Frames)")
    add_body_p(
        doc,
        "Để loại trừ hiện tượng cảnh báo giả thoáng qua do phản chiếu ánh sáng ngẫu nhiên hoặc các nhiễu ảnh chỉ xuất hiện trong 1 khung hình đơn lẻ, "
        "hệ thống áp dụng thuật toán cửa sổ trượt (Sliding Window) được hiện thực tại detection/fire_logic.py:"
    )
    
    add_image_with_caption(doc, os.path.join(img_dir, "thuy_ngan_image1.png"), "Hình 2.1: Quy tắc toán học xác nhận sự kiện lửa/khói theo cửa sổ trượt 3/5 khung hình", width=Inches(4.8))
    
    add_body_p(
        doc,
        "Giải thích công thức:\n"
        "• c: Lớp đối tượng cần xác nhận (Fire hoặc Smoke).\n"
        "• t: Khung hình hiện tại đang xử lý trong chuỗi video.\n"
        "• I(c được phát hiện ở frame i): Hàm chỉ thị, trả về 1 nếu lớp c được phát hiện với độ tin cậy vượt ngưỡng calibrated, ngược lại trả về 0.\n"
        "• Tổng xích-ma từ i = t-4 đến i = t: Tổng số khung hình phát hiện dương tính lớp c trong 5 khung hình gần nhất.\n"
        "• >= 3: Điều kiện bắt buộc phải có ít nhất 3 trong 5 khung hình phát hiện liên tiếp thì sự kiện mới được xác nhận chính thức (confirmed = True)."
    )
    
    add_heading_2(doc, "2.5. Các chỉ số toán học đánh giá mô hình thị giác máy tính")
    add_body_p(
        doc,
        "Để đánh giá toàn diện hiệu năng của mô hình phát hiện đối tượng, hệ thống sử dụng các chỉ số toán học chuẩn quốc tế:"
    )
    
    # 1. IoU
    add_heading_3(doc, "1. Chỉ số IoU (Intersection over Union)")
    add_body_p(doc, "IoU đo lường mức độ trùng khớp không gian giữa bounding box dự đoán (B_pred) và bounding box thực tế được gán nhãn (B_gt):")
    add_image_with_caption(doc, os.path.join(img_dir, "thuy_ngan_image2.png"), "Hình 2.2: Công thức tính hệ số tương đồng IoU", width=Inches(3.8))
    
    # 2. Precision
    add_heading_3(doc, "2. Chỉ số Precision (Độ chính xác dự đoán dương tính)")
    add_body_p(doc, "Precision đo tỷ lệ dự đoán đúng trong tổng số các đối tượng mà mô hình dự đoán là Fire hoặc Smoke:")
    add_image_with_caption(doc, os.path.join(img_dir, "thuy_ngan_image3.png"), "Hình 2.3: Công thức tính chỉ số Precision", width=Inches(2.5))
    
    # 3. Recall
    add_heading_3(doc, "3. Chỉ số Recall (Độ bao phủ phát hiện)")
    add_body_p(doc, "Recall đo khả năng phát hiện không bỏ sót các đám cháy hoặc luồng khói thực tế ngoài hiện trường (trong PCCC, Recall cao là ưu tiên hàng đầu):")
    add_image_with_caption(doc, os.path.join(img_dir, "thuy_ngan_image4.png"), "Hình 2.4: Công thức tính chỉ số Recall", width=Inches(2.5))
    
    # 4. F1-score
    add_heading_3(doc, "4. Chỉ số F1-Score (Trung bình điều hòa)")
    add_body_p(doc, "F1-score là trung bình điều hòa giữa Precision và Recall, phản ánh sự cân bằng tổng thể của mô hình:")
    add_image_with_caption(doc, os.path.join(img_dir, "thuy_ngan_image5.png"), "Hình 2.5: Công thức tính chỉ số F1-score", width=Inches(3.0))
    
    # 5. mAP50 & mAP50-95
    add_heading_3(doc, "5. Chỉ số mAP50 và mAP50-95 (Mean Average Precision)")
    add_body_p(doc, "mAP50 tính trung bình diện tích dưới đường cong Precision-Recall tại ngưỡng IoU = 0.50:")
    add_image_with_caption(doc, os.path.join(img_dir, "thuy_ngan_image6.png"), "Hình 2.6: Công thức tính chỉ số mAP50", width=Inches(3.8))
    
    add_body_p(doc, "mAP50-95 là chỉ số khắt khe nhất, tính trung bình mAP tại 10 ngưỡng IoU từ 0.50 đến 0.95 với bước nhảy 0.05:")
    add_image_with_caption(doc, os.path.join(img_dir, "thuy_ngan_image7.png"), "Hình 2.7: Công thức tính chỉ số mAP50-95", width=Inches(3.8))
    
    add_heading_2(doc, "2.6. Quy trình 6 bước hoạt động của phân hệ AI")
    add_bullet_p(doc, "Khởi tạo mạng YOLO và tải file trọng số models/best.pt; kiểm tra toàn vẹn tệp trước khi suy luận.", "Bước 1 — Nạp mô hình:")
    add_bullet_p(doc, "OpenCV mở nguồn hình ảnh (webcam thiết bị hoặc video file); kiểm tra lỗi luồng truyền.", "Bước 2 — Mở nguồn hình ảnh:")
    add_bullet_p(doc, "Khung hình được chuẩn hóa kích thước 416x416 và đưa qua mô hình YOLO để nhận danh sách bounding box.", "Bước 3 — Phát hiện đối tượng:")
    add_bullet_p(doc, "Đối chiếu điểm tin cậy với ngưỡng riêng của từng lớp và đưa vào bộ đệm cửa sổ trượt 5 frame.", "Bước 4 — Xác nhận đa khung hình:")
    add_bullet_p(doc, "Khi chuyển trạng thái sang 'ĐÃ XÁC NHẬN', vẽ bounding box lên ảnh, chụp snapshot lưu vào đĩa và tạo bản ghi sự kiện JSON.", "Bước 5 — Ghi nhận sự kiện:")
    add_bullet_p(doc, "Gửi bản ghi sự kiện lên máy chủ backend qua HTTP RESTful API để lưu vết lâu dài vào CSDL.", "Bước 6 — Truyền dữ liệu lên Backend:")
    
    # ══════════════════════════════════════════════════════════════
    # ─── CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ CƠ SỞ DỮ LIỆU (HUY HOÀNG) ───
    # ══════════════════════════════════════════════════════════════
    add_heading_1(doc, "CHƯƠNG 3: PHÂN TÍCH VÀ THIẾT KẾ CƠ SỞ DỮ LIỆU")
    add_body_p(doc, "Phân hệ do sinh viên Huy Hoàng phụ trách phân tích yêu cầu, thiết kế schema và kiểm thử CSDL.", bold_prefix="Phụ trách: ")
    
    add_heading_2(doc, "3.1. Mục tiêu và phạm vi thiết kế CSDL")
    add_body_p(
        doc,
        "Cơ sở dữ liệu FireEyes được thiết kế nhằm phục vụ việc lưu trữ bền vững toàn bộ chu trình giám sát: từ thông tin địa điểm, "
        "camera, nguồn cấp dữ liệu, đến từng khung hình phát hiện đối tượng, sự kiện cảnh báo và lịch sử gửi thông báo cứu nạn. "
        "CSDL tổ chức theo mô hình quan hệ chặt chẽ nhằm đảm bảo tính toàn vẹn, hỗ trợ truy vết ngược từ một sự cố về khung hình và ảnh bằng chứng ban đầu."
    )
    
    add_heading_2(doc, "3.2. Yêu cầu lưu trữ và xử lý dữ liệu chuẩn 11 bảng")
    add_body_p(
        doc,
        "Lược đồ cơ sở dữ liệu FireEyes v2 bao gồm đầy đủ 11 bảng được chuẩn hóa ở dạng chuẩn 3NF (Third Normal Form):\n"
        "1. locations: Quản lý các địa điểm, tòa nhà, phân xưởng giám sát.\n"
        "2. cameras: Quản lý danh mục camera gắn tại từng địa điểm kèm trạng thái bật/tắt (enabled) và tín hiệu heartbeat.\n"
        "3. contacts: Danh bạ người nhận tin khẩn cấp (Trực ban, Bảo vệ, Đội PCCC cơ sở).\n"
        "4. dataset_versions: Quản lý phiên bản tập dữ liệu huấn luyện (D-Fire) và ánh xạ lớp.\n"
        "5. dataset_samples: Lưu trữ thông tin từng mẫu ảnh trong tập dữ liệu.\n"
        "6. annotations: Nhãn chi tiết bounding box của từng mẫu ảnh huấn luyện.\n"
        "7. model_versions: Quản lý phiên bản mô hình AI (YOLO11n, DEMO-NO-AI) kèm mã băm SHA-256 của file trọng số.\n"
        "8. frames: Lưu thông tin từng khung hình được ghi nhận từ camera kèm request_id chống trùng lặp.\n"
        "9. detections: Lưu các hộp bounding box lửa/khói phát hiện được trong mỗi khung hình.\n"
        "10. incidents: Quản lý các sự cố cảnh báo, trạng thái mở/đã xử lý, thời gian bắt đầu/kết thúc và ghi chú xử lý.\n"
        "11. notifications: Lưu vết các lần thông báo (simulated/sent) tới từng người nhận ứng với mỗi sự cố."
    )
    
    add_heading_2(doc, "3.3. Sơ đồ quan hệ thực thể ERD các bảng nghiệp vụ chính")
    add_body_p(
        doc,
        "Dưới đây là sơ đồ quan hệ thực thể tập trung vào 7 bảng nghiệp vụ chính tham gia trực tiếp vào luồng cảnh báo của hệ thống:"
    )
    
    add_image_with_caption(doc, os.path.join(img_dir, "huy_hoang_image1.png"), "Hình 3.1: Sơ đồ quan hệ thực thể ERD 7 bảng nghiệp vụ chính của hệ thống FireEyes", width=Inches(6.0))
    
    add_heading_2(doc, "3.4. Ràng buộc toàn vẹn, Trigger và Tối ưu hóa truy vấn")
    add_body_p(
        doc,
        "Hệ thống thiết lập nhiều tầng bảo vệ toàn vẹn dữ liệu chặt chẽ cả ở tầng CSDL SQLite và tầng mã nguồn Python:\n"
        "• Bật chế độ khóa ngoại bắt buộc: PRAGMA foreign_keys = ON trên mọi kết nối; ngăn chặn hoàn toàn việc xóa mồ côi.\n"
        "• Ràng buộc CHECK giá trị: Kiểm tra trạng thái enabled chỉ nhận 0 hoặc 1; class_id thuộc {0, 1}; confidence thuộc [0, 1]; tọa độ hộp bao xc, yc, w, h nằm trọn trong khoảng [0, 1].\n"
        "• Index UNIQUE có điều kiện (Partial Index): idx_one_open_incident trên bảng incidents với điều kiện status = 'open'. Đảm bảo mỗi camera tại một thời điểm chỉ có tối đa một sự cố đang mở, tránh spam cảnh báo.\n"
        "• Database Trigger tự động: Trigger incident_camera_insert và incident_camera_update kiểm tra bằng chứng detection kích hoạt phải bắt nguồn từ đúng camera được gán sự cố.\n"
        "• Tối ưu chỉ mục truy vấn: Thiết lập các index idx_frames_camera_time, idx_detections_frame, idx_incident_status_time giúp truy vấn lịch sử và lọc sự cố đạt tốc độ O(1) đến O(log N)."
    )
    
    add_heading_2(doc, "3.5. Thiết kế giao dịch nguyên tử ACID và cơ chế chống trùng lặp Idempotency")
    add_body_p(
        doc,
        "Khi ghi nhận kết quả từ camera, thao tác thêm bản ghi vào bảng frames và hàng loạt bản ghi con trong detections được bọc trong một "
        "giao dịch nguyên tử duy nhất bắt đầu bằng lệnh BEGIN IMMEDIATE. Nếu xảy ra bất kỳ lỗi dữ liệu nào, toàn bộ giao dịch sẽ tự động Rollback, "
        "tuyệt đối không để lại frame rác không có detections."
    )
    add_body_p(
        doc,
        "Để hỗ trợ cơ chế gửi lại khi mạng chập chờn (Network Retry), mỗi yêu cầu mang theo một request_id duy nhất và payload_sha256 được tính từ "
        "nội dung khung hình. Nếu cùng một request_id được gửi lại với đúng payload cũ, CSDL trả về ngay frame_id đã tạo mà không nhân đôi dữ liệu. "
        "Nếu gửi lại cùng request_id nhưng payload bị chỉnh sửa, CSDL phát hiện xung đột và từ chối ngay lập tức (Idempotency Conflict)."
    )
    
    # ══════════════════════════════════════════════════════════════
    # ─── CHƯƠNG 4: GIAO DIỆN WEB & TÍCH HỢP HỆ THỐNG (PHÚ ANH & ĐÌNH ANH) ───
    # ══════════════════════════════════════════════════════════════
    add_heading_1(doc, "CHƯƠNG 4: PHÁT TRIỂN GIAO DIỆN WEB VÀ TÍCH HỢP HỆ THỐNG")
    add_body_p(doc, "Phân hệ do sinh viên Phú Anh và Nguyễn Đình Anh (Trưởng nhóm) phối hợp triển khai.", bold_prefix="Phụ trách: ")
    
    add_heading_2(doc, "4.1. Thiết kế Giao diện Giám sát Người dùng (Frontend SPA - Phú Anh phụ trách)")
    
    add_heading_3(doc, "4.1.1. Giao diện bảng điều khiển Dashboard và giám sát trực tiếp")
    add_body_p(
        doc,
        "Giao diện người dùng được xây dựng theo kiến trúc Single Page Application (SPA) hiện đại tại frontend/app.js và frontend/index.html. "
        "Giao diện sử dụng framework Tailwind CSS kết hợp thư viện biểu tượng Lucide Icons và Canvas API hiệu năng cao. "
        "Màn hình chính bao gồm:\n"
        "• Bảng thống kê tổng quan: 11 thẻ số liệu đại diện cho 11 bảng CSDL, tự động cập nhật số lượng bản ghi.\n"
        "• Khung giám sát camera AI: Hiển thị luồng video webcam thời gian thực với thanh trạng thái FPS, độ phân giải và badge trạng thái an toàn.\n"
        "• Bảng nhật ký sự kiện: Liệt kê chi tiết các sự cố cảnh báo kèm thời gian, camera, loại cảnh báo (Lửa/Khói), độ tin cậy và nút thao tác xử lý."
    )
    
    add_heading_3(doc, "4.1.2. Thuật toán thị giác máy tính phân tích màu ngọn lửa thời gian thực (Color Physics)")
    add_body_p(
        doc,
        "Để cho phép hệ thống nhận diện ngọn lửa trực tiếp trên trình duyệt khi người dùng sử dụng bật lửa ga hoặc que diêm trước webcam, "
        "sinh viên Phú Anh đã hiện thực thuật toán phân tích màu quang học ngọn lửa thời gian thực (_detectRealtimeFlame):"
    )
    add_bullet_p(doc, "Ngọn lửa cháy có nhiệt độ cao phát ra ánh sáng vàng cam rực rỡ với tỷ lệ kênh màu đặc trưng: R > 1.25 * G và G > 1.15 * B. Tổng cường độ sáng phát xạ đạt ngưỡng cực đại (R + G + B >= 630).", "Quy luật phổ màu phát xạ:")
    add_bullet_p(doc, "Ngọn lửa có độ bão hòa màu rất cao (Saturation S >= 0.58), khác biệt hoàn toàn với ánh sáng đèn neon hoặc ánh sáng tự nhiên thông thường.", "Độ bão hòa màu sắc (Saturation):")
    add_bullet_p(doc, "Hệ thống gom cụm các pixel ngọn lửa liên thông, tính toán bounding box bao quanh và chuẩn hóa tọa độ [xc, yc, w, h] trong khung hình canvas.", "Trích xuất Bounding Box:")
    
    add_heading_3(doc, "4.1.3. Thuật toán bộ lọc loại trừ báo động giả trên da người và tường phòng")
    add_body_p(
        doc,
        "Một trong những thách thức lớn nhất của các thuật toán nhận diện màu sắc là báo cháy giả khi người dùng đưa bàn tay hoặc khuôn mặt "
        "lại gần camera. Phú Anh đã giải quyết triệt để vấn đề này bằng bộ lọc vật lý chuyên sâu:"
    )
    add_bullet_p(doc, "Sắc tố da người có độ bão hòa màu thấp hơn ngọn lửa rất nhiều (S thường chỉ dao động từ 0.25 đến 0.45) và tổng cường độ sáng da không bao giờ vượt qua 520 trong điều kiện phòng bình thường. Hệ thống thiết lập ngưỡng cắt loại bỏ toàn bộ vùng có S < 0.55.", "Bộ lọc da người (Human Skin Rejection):")
    add_bullet_p(doc, "Tường phòng sơn xám tĩnh hoặc nền rèm cửa có tỷ lệ màu đồng đều (R ~ G ~ B), hệ thống tự động nhận diện và vô hiệu hóa tính năng auto-smoke trên webcam trực tiếp, chỉ cho phép kích hoạt khi có biến động điểm ảnh đột ngột.", "Bộ lọc tường xám tĩnh (Static Background Filter):")
    add_bullet_p(doc, "Ngọn lửa từ bật lửa cầm tay có kích thước tương đối nhỏ so với khung hình (chiều rộng w <= 0.30 và chiều cao h <= 0.40). Mọi vùng sáng vượt quá kích thước này bị loại trừ vì là ánh sáng đèn trần.", "Ràng buộc kích thước ngọn lửa (Lighter Bounding Constraint):")
    
    add_heading_3(doc, "4.1.4. Cơ chế ngắt kết nối phần cứng camera triệt để và còi hú âm thanh")
    add_body_p(
        doc,
        "Trước đây, việc tắt camera trên trình duyệt thường chỉ ẩn thẻ video, khiến phần cứng webcam vẫn chạy ngầm và đèn camera vẫn sáng. "
        "Phú Anh đã hoàn thiện hàm _stopWebcam() thực thi ngắt toàn diện:\n"
        "• Duyệt qua tất cả các luồng tracks: stream.getTracks().forEach(track => { track.stop(); track.enabled = false; });\n"
        "• Gán srcObject = null và vẽ biển báo offline 'CAMERA ĐÃ TẮT (STOPPED)' lên Canvas.\n"
        "• Hệ thống còi hú được lập trình bằng Web Audio API với bộ dao động sóng vuông (Square Wave Oscillator) tần số quét từ 660Hz lên 880Hz nhịp 150ms, mô phỏng chính xác tiếng còi hỏa hoạn tiêu chuẩn."
    )
    
    add_image_with_caption(doc, os.path.join(img_dir, "ui_alarm_incident.png"), "Hình 4.1: Giao diện cảnh báo khẩn cấp khi phát hiện ngọn lửa bật lửa và còi hú kích hoạt")
    
    add_heading_2(doc, "4.2. Xây dựng Lớp Điều Khiển MVC & RESTful API Backend (Đình Anh phụ trách)")
    
    add_heading_3(doc, "4.2.1. Hệ thống RESTful API chuẩn hóa bằng FastAPI")
    add_body_p(
        doc,
        "Sinh viên Nguyễn Đình Anh chịu trách nhiệm xây dựng tầng dịch vụ backend sử dụng framework FastAPI hiện đại. "
        "Hệ thống cung cấp đầy đủ các nhóm endpoint RESTful chuẩn OpenAPI/Swagger:\n"
        "• /health: Kiểm tra trạng thái hoạt động của máy chủ backend.\n"
        "• /api/locations & /api/cameras: Đăng ký, liệt kê và truy vấn chi tiết địa điểm, camera, cập nhật trạng thái bật/tắt và heartbeat.\n"
        "• /api/frames & /api/detections: Tiếp nhận dữ liệu khung hình và danh sách hộp nhận diện từ client.\n"
        "• /api/alerts & /api/incidents: Truy vấn danh sách sự cố, xem ảnh snapshot, xác nhận sự cố (Acknowledge) và giải quyết sự cố (Resolve).\n"
        "• /api/contacts & /api/notifications: Quản lý danh bạ cứu nạn và lịch sử thông báo mô phỏng.\n"
        "• /api/demo: Endpoint kích hoạt luồng dữ liệu giả lập phục vụ trình diễn và kiểm thử."
    )
    
    add_heading_3(doc, "4.2.2. Hiện thực lớp điều khiển AppController theo đúng Class Diagram MVC")
    add_body_p(
        doc,
        "Để đảm bảo cấu trúc phân lớp chuẩn mực, Đình Anh đã hiện thực lớp AppController tại backend/CSDL/controllers/app_controller.py. "
        "Lớp này tách biệt hoàn toàn logic định tuyến của web với mô hình CSDL:\n"
        "• Phương thức get_stats(): Thu thập thống kê 11 bảng CSDL.\n"
        "• Phương thức run_demo(): Tạo chuỗi dữ liệu giả lập trọn vẹn từ Frame -> Detection -> Incident -> Notification.\n"
        "• Tối ưu hóa truy vấn: Thay thế vòng lặp tìm kiếm tuyến tính O(N) bằng truy vấn SQL chỉ mục trực tiếp O(1) cho các hàm get_incident, get_camera, get_location."
    )
    
    add_heading_3(doc, "4.2.3. Quản trị hệ thống qua công cụ dòng lệnh CLI hỗ trợ UTF-8")
    add_body_p(
        doc,
        "Đình Anh đã hoàn thiện công cụ dòng lệnh backend/main.py cho phép quản trị viên vận hành hệ thống trực tiếp từ Command Prompt/PowerShell:\n"
        "• python -m backend.main init: Khởi tạo cấu trúc CSDL SQLite v2.\n"
        "• python -m backend.main stats: In bảng thống kê bản ghi 11 bảng dạng JSON.\n"
        "• python -m backend.main demo: Thực thi kịch bản tạo dữ liệu giả lập.\n"
        "• python -m backend.main incidents: Liệt kê danh sách sự cố cảnh báo.\n"
        "Đặc biệt, script đã được cấu hình tự động sys.stdout.reconfigure(encoding='utf-8'), khắc phục triệt để lỗi crash bảng mã charmap cp1252 trên Windows."
    )
    
    add_heading_3(doc, "4.2.4. Xử lý triệt để lỗi CameraUnavailableError trong seed demo")
    add_body_p(
        doc,
        "Trong quá trình kiểm thử, nhóm phát hiện khi camera demo bị người dùng bấm tắt (enabled = 0 trên giao diện), lệnh tạo demo ném lỗi "
        "CameraUnavailableError. Đình Anh đã xử lý triệt để bằng việc bổ sung câu lệnh UPDATE cameras SET enabled=1 trong hàm seed_demo(). "
        "Nhờ đó, camera demo luôn được tái kích hoạt sẵn sàng mỗi khi chạy kịch bản thử nghiệm."
    )
    
    # ══════════════════════════════════════════════════════════════
    # ─── CHƯƠNG 5: CÀI ĐẶT, THỰC NGHIỆM VÀ ĐÁNH GIÁ ───
    # ══════════════════════════════════════════════════════════════
    add_heading_1(doc, "CHƯƠNG 5: CÀI ĐẶT, THỰC NGHIỆM VÀ ĐÁNH GIÁ KẾT QUẢ")
    
    add_heading_2(doc, "5.1. Môi trường triển khai và vận hành hệ thống")
    add_body_p(
        doc,
        "Hệ thống đã được cài đặt, cấu hình và vận hành hoàn chỉnh trên môi trường máy tính Windows 11 với phần cứng CPU Intel Core i5/i7, "
        "RAM 8GB/16GB, tích hợp webcam HD. Toàn bộ mã nguồn backend được quản lý trong môi trường ảo .venv với các gói thư viện chuẩn: "
        "fastapi (v0.143.0), uvicorn (v0.54.0), pydantic (v2.14.1), ultralytics (v8.4.175), opencv-python (v5.0.0.93)."
    )
    
    add_heading_2(doc, "5.2. Kết quả kiểm thử tự động (26/26 Unit Tests đạt 100%)")
    add_body_p(
        doc,
        "Bộ kiểm thử tự động gồm hai tệp test_database.py (kiểm tra giao dịch CSDL, trigger, ràng buộc) và test_api.py (kiểm tra toàn bộ RESTful API, "
        "xác thực schema, chống xung đột, xử lý ảnh snapshot và kịch bản demo) được thực thi bằng unittest:"
    )
    
    # Bảng tóm tắt kết quả test
    tbl_ut = doc.add_table(rows=7, cols=4)
    tbl_ut.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl_ut)
    ut_h = ["Phân nhóm kiểm thử", "Số lượng Test Cases", "Tình trạng", "Thời gian chạy"]
    for i, h in enumerate(ut_h):
        cell = tbl_ut.cell(0, i)
        cell.text = h
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        p = cell.paragraphs[0]
        set_font_times(p.runs[0], size_pt=10, bold=True, color_rgb=RGBColor(0xFF, 0xFF, 0xFF))
        
    ut_rows = [
        ("CSDL: Ràng buộc, khóa ngoại & trigger", "8 bài tests", "ĐẠT 100% (PASS)", "0.52s"),
        ("CSDL: Giao dịch ACID & Idempotency Hash", "4 bài tests", "ĐẠT 100% (PASS)", "0.31s"),
        ("API: Nhận diện khung hình & Bounding Box", "6 bài tests", "ĐẠT 100% (PASS)", "0.45s"),
        ("API: Vòng đời sự cố (Acknowledge/Resolve)", "4 bài tests", "ĐẠT 100% (PASS)", "0.34s"),
        ("API: Quản lý Cameras, Contacts & Snapshot", "4 bài tests", "ĐẠT 100% (PASS)", "0.42s"),
        ("TỔNG CỘNG BỘ TEST SUITE TOÀN HỆ THỐNG", "26 BÀI TESTS", "26/26 ĐẠT (100% OK)", "2.04s"),
    ]
    for r_idx, r_data in enumerate(ut_rows, 1):
        bg = "EBF5FB" if r_idx == 6 else ("F7F9FC" if r_idx % 2 == 1 else "FFFFFF")
        for c_idx, txt in enumerate(r_data):
            cell = tbl_ut.cell(r_idx, c_idx)
            cell.text = txt
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=120, right=120)
            p = cell.paragraphs[0]
            if r_idx == 6 or c_idx == 2:
                set_font_times(p.runs[0], size_pt=9.5, bold=True, color_rgb=RGBColor(0x00, 0x80, 0x00) if c_idx == 2 else RGBColor(0x00, 0x33, 0x66))
            else:
                set_font_times(p.runs[0], size_pt=9.5, color_rgb=RGBColor(0x22, 0x22, 0x22))
                
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    
    add_heading_2(doc, "5.3. Kết quả thực nghiệm nhận diện thực tế")
    add_body_p(
        doc,
        "Nhóm đã tiến hành kiểm nghiệm thực tế trực tiếp với các kịch bản đời thực:\n"
        "• Thử nghiệm với bật lửa ga: Bật lửa ở cự ly 30cm - 60cm trước webcam; hệ thống nhận diện ngọn lửa trong 2 khung hình đầu tiên và kích hoạt còi báo động khẩn cấp ngay tại khung hình thứ 3 (đáp ứng đúng quy tắc 3/5 frames). Tỷ lệ phát hiện đạt 100% trên 15 lần thử nghiệm.\n"
        "• Thử nghiệm chống báo động giả: Đưa bàn tay, khuôn mặt người sát camera hoặc chiếu đèn pin; hệ thống không phát hiện nhầm, giữ nguyên trạng thái an toàn, không có cảnh báo sai.\n"
        "• Thử nghiệm tải ảnh hiện trường: Tải lên các hình ảnh đám cháy rừng, cháy nhà xưởng và khói cuộn; thuật toán vẽ chính xác bounding box bao quanh vùng phát cháy và lưu trữ ảnh chụp snapshot mượt mà.\n"
        "• Thử nghiệm tắt webcam: Đèn camera tắt ngay lập tức, giải phóng phần cứng và hiển thị màn hình offline chuẩn."
    )
    
    add_heading_2(doc, "5.4. Đánh giá ưu điểm, hạn chế và bài học kinh nghiệm")
    add_bullet_p(doc, "Hệ thống hoạt động ổn định, độ trễ nhận diện cực thấp (< 80ms/frame), khả năng nhận diện ngọn lửa nhạy bén kết hợp bộ lọc chống báo cháy giả hiệu quả cao; cấu trúc mã nguồn MVC chuẩn mực, tài liệu hóa API đầy đủ và giao diện người dùng trực quan, chuyên nghiệp.", "Ưu điểm nổi bật:")
    add_bullet_p(doc, "Độ nhạy nhận diện khói trên webcam máy tính còn phụ thuộc vào độ tương phản ánh sáng phòng; hiện tại tính năng gửi thông báo cứu nạn mới dừng ở mức mô phỏng (simulated) trong CSDL, chưa tích hợp cổng SMS/Cuộc gọi GSM phần cứng thực tế.", "Hạn chế còn tồn tại:")
    add_bullet_p(doc, "Kinh nghiệm thực tiễn về quy trình phối hợp nhóm 4 thành viên theo chuẩn kỹ thuật phần mềm; kỹ năng kiểm soát xung đột dữ liệu và thiết kế giao dịch ACID; kỹ năng xử lý phổ màu quang học và hiệu chỉnh mạng nơ-ron học sâu.", "Bài học kinh nghiệm:")
    
    # ══════════════════════════════════════════════════════════════
    # ─── KẾT LUẬN & HƯỚNG PHÁT TRIỂN ───
    # ══════════════════════════════════════════════════════════════
    add_heading_1(doc, "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    
    add_heading_2(doc, "Kết quả đạt được")
    add_body_p(
        doc,
        "Đề tài 'Hệ thống giám sát và cảnh báo sớm cháy & khói bằng Trí tuệ nhân tạo (FireEyes AI)' đã hoàn thành xuất sắc 100% "
        "các mục tiêu nghiên cứu và yêu cầu kỹ thuật đề ra ban đầu. Cả 4 thành viên trong nhóm đã phối hợp chặt chẽ, hoàn thành trọn vẹn "
        "các phân hệ được phân công:\n"
        "• Sinh viên Nguyễn Đình Anh (Trưởng nhóm - 26%): Điều phối chung, xây dựng hệ thống RESTful API FastAPI mạnh mẽ, lớp điều khiển AppController, quản lý vòng đời sự cố, công cụ dòng lệnh CLI UTF-8, bộ test hồi quy 26 unit tests và tổng hợp báo cáo.\n"
        "• Sinh viên Phú Anh (Thành viên chính - 28%): Thiết kế kiến trúc MVC, xây dựng Web SPA, hiện thực thuật toán nhận diện ngọn lửa thời gian thực (Color Physics), bộ lọc chống báo động giả trên da người, ngắt phần cứng camera và tài liệu hướng dẫn kiểm thử toàn diện.\n"
        "• Sinh viên Huy Hoàng (Thành viên - 23%): Hoàn thành thiết kế và cài đặt CSDL SQLite v2 chuẩn 11 bảng, thiết lập ràng buộc toàn vẹn, trigger và giao dịch nguyên tử ACID bền vững.\n"
        "• Sinh viên Thùy Ngân (Thành viên - 23%): Hoàn thành nghiên cứu mô hình YOLO11n, xử lý tập dữ liệu D-Fire, hiệu chỉnh ngưỡng phân lớp và thuật toán xác nhận chuỗi khung hình 3/5 frames."
    )
    
    add_heading_2(doc, "Hướng phát triển tương lai")
    add_bullet_p(doc, "Tích hợp giao thức RTSP/ONVIF để kết nối trực tiếp với hệ thống camera an ninh IP thực tế tại các tòa nhà và khu công nghiệp.", "1. Mở rộng nguồn dữ liệu Camera IP:")
    add_bullet_p(doc, "Kết nối với dịch vụ nhắn tin Twilio SMS, Telegram Bot API và hệ thống loa thông báo khẩn cấp tại chỗ để truyền tin cứu nạn tức thời tới lực lượng PCCC chuyên nghiệp.", "2. Tích hợp cổng thông báo thực tế:")
    add_bullet_p(doc, "Đóng gói toàn bộ hệ thống bằng Docker Compose và triển khai lên hạ tầng đám mây (Cloud Server) hoặc thiết bị tính toán biên (Edge Computing như NVIDIA Jetson) để giám sát phân tán đa địa điểm.", "3. Triển khai điện toán biên & Đám mây:")
    
    # ─── TÀI LIỆU THAM KHẢO ───
    add_heading_1(doc, "TÀI LIỆU THAM KHẢO")
    refs = [
        "[1] Ultralytics, 'YOLO11: A State-of-the-Art Real-Time Object Detection Model', GitHub Repository, 2024.",
        "[2] Gaia Solutions on Demand, 'D-Fire: Fire and Smoke Dataset for Object Detection', CC0-1.0 License, 2022.",
        "[3] FastAPI Documentation, 'High Performance Web Framework for Building APIs with Python 3.8+', tiangolo.com, 2024.",
        "[4] SQLite Consortium, 'SQLite Foreign Key Support and Transaction Isolation in WAL Mode', sqlite.org, 2024.",
        "[5] Bộ Công An — Cục Cảnh sát PCCC & CNCH, 'Tiêu chuẩn Quốc gia TCVN 3890:2023 về Phòng cháy và chữa cháy — Trang bị, bố trí phương tiện, hệ thống PCCC cho nhà và công trình', NXB Xây Dựng, Hà Nội, 2023.",
        "[6] Joseph Redmon, Santosh Divvala, Ross Girshick, Ali Farhadi, 'You Only Look Once: Unified, Real-Time Object Detection', IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016.",
        "[7] MDN Web Docs, 'MediaStreams and Web Audio API: Capturing Audio & Video in Modern Web Browsers', Mozilla Developer Network, 2024."
    ]
    for ref in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.2)
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_after = Pt(3)
        r = p_ref.add_run(ref)
        set_font_times(r, size_pt=10, color_rgb=RGBColor(0x33, 0x33, 0x33))
        
    doc.save(output_path)
    print(f"Master report {output_path} generated successfully with standardized Times New Roman font!")

if __name__ == "__main__":
    out_master = r"C:\Users\ADMIN\Desktop\bao_cao_tong_nhom.docx"
    build_master_report(out_master)
