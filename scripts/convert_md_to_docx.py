# -*- coding: utf-8 -*-
"""
Production-grade Markdown to Word Document (.docx) converter for the
Women's Travel Safety Guardian & Companion Matching Platform (Safira) Project Report.
Generates an academic, beautifully styled .docx document.
"""

import re
import os
import sys
from pathlib import Path

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_background(cell, hex_color):
    """Sets background shading of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}" w:val="clear"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets inner margins/padding of a table cell in dxa (1 pt = 20 dxa)."""
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

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    """Sets subtle borders for an entire table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_formatted_runs(paragraph, text, base_font="Times New Roman", base_size=11.5, base_color=(31, 41, 55), italic_override=False):
    """
    Parses markdown inline tokens:
      - ***bold-italic***
      - **bold**
      - *italic*
      - `code`
      - $math$
      - [link](url)
    and attaches formatted runs to the paragraph.
    """
    token_pattern = re.compile(
        r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|`.*?`|\$.*?\$|\[.*?\]\(.*?\))'
    )
    parts = token_pattern.split(text)
    
    for part in parts:
        if not part:
            continue
            
        # Bold-Italic ***text***
        if part.startswith('***') and part.endswith('***') and len(part) >= 6:
            inner = part[3:-3]
            run = paragraph.add_run(inner)
            run.font.name = base_font
            run.font.size = Pt(base_size)
            run.font.color.rgb = RGBColor(*base_color)
            run.bold = True
            run.italic = True
            
        # Bold **text**
        elif part.startswith('**') and part.endswith('**') and len(part) >= 4:
            inner = part[2:-2]
            run = paragraph.add_run(inner)
            run.font.name = base_font
            run.font.size = Pt(base_size)
            run.font.color.rgb = RGBColor(*base_color)
            run.bold = True
            if italic_override:
                run.italic = True
                
        # Italic *text*
        elif part.startswith('*') and part.endswith('*') and len(part) >= 2:
            inner = part[1:-1]
            run = paragraph.add_run(inner)
            run.font.name = base_font
            run.font.size = Pt(base_size)
            run.font.color.rgb = RGBColor(*base_color)
            run.italic = True
            
        # Inline Code `code`
        elif part.startswith('`') and part.endswith('`') and len(part) >= 2:
            inner = part[1:-1]
            run = paragraph.add_run(inner)
            run.font.name = "Consolas"
            run.font.size = Pt(base_size - 1.0)
            run.font.color.rgb = RGBColor(190, 24, 93)  # Rose/Berry accent
            run.bold = False
            
        # Math $math$
        elif part.startswith('$') and part.endswith('$') and len(part) >= 2:
            inner = part[1:-1]
            # Clean common LaTeX syntax for Word readability
            clean_math = inner.replace(r'\text', '').replace('{', '').replace('}', '')
            clean_math = clean_math.replace(r'\le', '≤').replace(r'\ge', '≥').replace(r'\approx', '≈')
            clean_math = clean_math.replace(r'\Delta', 'Δ').replace(r'\sigma', 'σ').replace(r'\phi', 'ϕ')
            clean_math = clean_math.replace(r'\lambda', 'λ').replace(r'\pm', '±').replace(r'\cdot', '·')
            run = paragraph.add_run(clean_math)
            run.font.name = "Cambria Math" if "Cambria Math" in ["Cambria Math"] else "Times New Roman"
            run.font.size = Pt(base_size)
            run.font.color.rgb = RGBColor(15, 23, 42)
            run.italic = True
            
        # Link [text](url)
        elif part.startswith('[') and '](' in part and part.endswith(')'):
            match = re.match(r'\[(.*?)\]\((.*?)\)', part)
            if match:
                link_text, url = match.groups()
                run = paragraph.add_run(link_text)
                run.font.name = base_font
                run.font.size = Pt(base_size)
                run.font.color.rgb = RGBColor(37, 99, 235)  # Blue
                run.underline = True
            else:
                run = paragraph.add_run(part)
                run.font.name = base_font
                run.font.size = Pt(base_size)
                run.font.color.rgb = RGBColor(*base_color)
                
        # Normal text
        else:
            run = paragraph.add_run(part)
            run.font.name = base_font
            run.font.size = Pt(base_size)
            run.font.color.rgb = RGBColor(*base_color)
            if italic_override:
                run.italic = True

def convert_md_to_docx(md_path: Path, docx_path: Path):
    print(f"Reading markdown from: {md_path}")
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = Document()

    # 1. Page Setup: Standard Academic Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

        # Header setup
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("WOMEN'S TRAVEL SAFETY GUARDIAN (SAFIRA)  |  B.TECH MAJOR PROJECT REPORT")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(148, 163, 184)

        # Footer setup
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Department of Computer Science & Engineering  •  Career Point University, Kota")
        frun.font.name = "Times New Roman"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(148, 163, 184)

    lines = md_text.splitlines()
    total_lines = len(lines)
    print(f"Processing {total_lines:,} lines of text...")

    i = 0
    in_code_block = False
    code_block_lines = []
    code_block_lang = ""

    in_table = False
    table_lines = []

    in_math_block = False
    math_block_lines = []

    is_cover_page = True

    while i < total_lines:
        line = lines[i]
        stripped = line.strip()

        # Handle page breaks
        if 'page-break-after: always' in stripped:
            doc.add_page_break()
            is_cover_page = False
            i += 1
            continue

        # Check for start/end of Code Block
        if stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_lang = stripped[3:].strip()
                code_block_lines = []
                i += 1
                continue
            else:
                # End of code block
                in_code_block = False
                
                # Render code block in a callout table
                tbl = doc.add_table(rows=1, cols=1)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell = tbl.cell(0, 0)
                cell.width = Inches(6.5)
                set_cell_background(cell, "F8FAFC")
                set_cell_margins(cell, top=140, bottom=140, left=180, right=180)

                # Set subtle left accent border
                tcPr = cell._tc.get_or_add_tcPr()
                borders = parse_xml(
                    f'<w:tcBorders {nsdecls("w")}>'
                    f'<w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
                    f'<w:left w:val="single" w:sz="24" w:space="0" w:color="3B82F6"/>'
                    f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
                    f'<w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
                    f'</w:tcBorders>'
                )
                tcPr.append(borders)

                cp = cell.paragraphs[0]
                cp.paragraph_format.space_before = Pt(0)
                cp.paragraph_format.space_after = Pt(0)
                cp.paragraph_format.line_spacing = 1.05

                code_text = "\n".join(code_block_lines)
                c_run = cp.add_run(code_text)
                c_run.font.name = "Consolas"
                c_run.font.size = Pt(9.0)
                c_run.font.color.rgb = RGBColor(15, 23, 42)

                # Spacer paragraph after table
                sp = doc.add_paragraph()
                sp.paragraph_format.space_before = Pt(0)
                sp.paragraph_format.space_after = Pt(4)

                code_block_lines = []
                i += 1
                continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

        # Check for Math Display Block ($$)
        if stripped.startswith('$$'):
            if not in_math_block:
                if stripped.endswith('$$') and len(stripped) > 2:
                    # Single-line display math
                    math_expr = stripped[2:-2].strip()
                    mp = doc.add_paragraph()
                    mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    mp.paragraph_format.space_before = Pt(6)
                    mp.paragraph_format.space_after = Pt(6)
                    add_formatted_runs(mp, f"${math_expr}$", base_size=12.0)
                    i += 1
                    continue
                else:
                    in_math_block = True
                    math_block_lines = []
                    i += 1
                    continue
            else:
                in_math_block = False
                math_expr = " ".join(math_block_lines).strip()
                mp = doc.add_paragraph()
                mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                mp.paragraph_format.space_before = Pt(6)
                mp.paragraph_format.space_after = Pt(6)
                add_formatted_runs(mp, f"${math_expr}$", base_size=12.0)
                math_block_lines = []
                i += 1
                continue

        if in_math_block:
            math_block_lines.append(stripped)
            i += 1
            continue

        # Check for Markdown Table (| col1 | col2 |)
        if stripped.startswith('|') and stripped.endswith('|'):
            if not in_table:
                in_table = True
                table_lines = [stripped]
                i += 1
                continue
            else:
                table_lines.append(stripped)
                i += 1
                continue
        else:
            if in_table:
                # Flush and render accumulated table
                in_table = False
                render_markdown_table(doc, table_lines)
                table_lines = []
                # Fall through to process current line

        # Horizontal rule ---
        if stripped in ('---', '***', '___'):
            # Only add small divider or ignore if followed by heading
            i += 1
            continue

        # Empty lines
        if not stripped:
            i += 1
            continue

        # Headings
        if stripped.startswith('# '):
            title_text = stripped[2:].strip().replace('**', '')
            p = doc.add_paragraph()
            p.paragraph_format.keep_with_next = True
            
            if is_cover_page or "A PROJECT REPORT" in title_text or "CERTIFICATE" in title_text or "ACKNOWLEDGEMENT" in title_text or "ABSTRACT" in title_text or "TABLE OF CONTENTS" in title_text:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(8)
                run = p.add_run(title_text)
                run.font.name = "Times New Roman"
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(30, 58, 138)  # Deep Navy
                run.bold = True
            elif title_text.startswith("CHAPTER"):
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(18)
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(title_text)
                run.font.name = "Times New Roman"
                run.font.size = Pt(18)
                run.font.color.rgb = RGBColor(30, 58, 138)
                run.bold = True
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(6)
                run = p.add_run(title_text)
                run.font.name = "Times New Roman"
                run.font.size = Pt(16)
                run.font.color.rgb = RGBColor(30, 58, 138)
                run.bold = True
            i += 1
            continue

        if stripped.startswith('## '):
            h2_text = stripped[3:].strip().replace('**', '')
            p = doc.add_paragraph()
            p.paragraph_format.keep_with_next = True
            if is_cover_page:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(8)
                p.paragraph_format.space_after = Pt(8)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(12)
                p.paragraph_format.space_after = Pt(4)
            run = p.add_run(h2_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(30, 58, 138)
            run.bold = True
            i += 1
            continue

        if stripped.startswith('### '):
            h3_text = stripped[4:].strip().replace('**', '')
            p = doc.add_paragraph()
            p.paragraph_format.keep_with_next = True
            if is_cover_page:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(6)
                p.paragraph_format.space_after = Pt(6)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(3)
            run = p.add_run(h3_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(12.5)
            run.font.color.rgb = RGBColor(31, 41, 55)
            run.bold = True
            i += 1
            continue

        if stripped.startswith('#### '):
            h4_text = stripped[5:].strip().replace('**', '')
            p = doc.add_paragraph()
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(h4_text)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11.5)
            run.font.color.rgb = RGBColor(71, 85, 105)
            run.bold = True
            run.italic = True
            i += 1
            continue

        # Bullet Lists (- or *)
        if stripped.startswith(('- ', '* ')) and not stripped.startswith(('***', '**')):
            item_text = stripped[2:].strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            add_formatted_runs(p, item_text)
            i += 1
            continue

        # Numbered Lists (1. , 2. )
        num_match = re.match(r'^(\d+)\.\s+(.*)', stripped)
        if num_match:
            item_text = num_match.group(2).strip()
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            add_formatted_runs(p, item_text)
            i += 1
            continue

        # Standard Paragraphs
        p = doc.add_paragraph()
        if is_cover_page:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        add_formatted_runs(p, stripped)

        i += 1

    # End of document processing - check if dangling table
    if in_table and table_lines:
        render_markdown_table(doc, table_lines)

    print(f"Saving compiled Word Document to: {docx_path}")
    doc.save(str(docx_path))
    file_size_kb = os.path.getsize(str(docx_path)) / 1024
    print(f"SUCCESS: Document created ({file_size_kb:.2f} KB) at {docx_path}")

def render_markdown_table(doc, table_lines):
    """Parses markdown table lines and creates an academic table in Word."""
    if len(table_lines) < 2:
        return

    # Extract rows
    rows_data = []
    for line in table_lines:
        line_clean = line.strip().strip('|')
        cells = [c.strip() for c in line_clean.split('|')]
        rows_data.append(cells)

    if len(rows_data) < 2:
        return

    header_row = rows_data[0]
    separator_row = rows_data[1]
    data_rows = rows_data[2:]

    num_cols = len(header_row)
    num_rows = 1 + len(data_rows)

    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_table_borders(table, color="CBD5E1", sz="4")

    # Format Header Row
    for col_idx, heading_text in enumerate(header_row):
        cell = table.cell(0, col_idx)
        set_cell_background(cell, "1E3A8A")  # Deep Navy
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(heading_text.replace('**', ''))
        run.font.name = "Times New Roman"
        run.font.size = Pt(10.0)
        run.font.color.rgb = RGBColor(255, 255, 255)
        run.bold = True

    # Make header repeat across page splits
    trPr = table.rows[0]._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    # Format Data Rows
    for row_idx, row_data in enumerate(data_rows):
        bg_color = "F8FAFC" if (row_idx % 2 == 1) else "FFFFFF"
        for col_idx in range(num_cols):
            cell_text = row_data[col_idx] if col_idx < len(row_data) else ""
            cell = table.cell(row_idx + 1, col_idx)
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=90, bottom=90, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            add_formatted_runs(p, cell_text, base_size=9.5)

    # Spacer after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(6)

if __name__ == "__main__":
    md_file = Path("PROJECT_REPORT_WOMEN_SAFETY_GUARDIAN.md")
    docx_file = Path("PROJECT_REPORT_WOMEN_SAFETY_GUARDIAN.docx")
    convert_md_to_docx(md_file, docx_file)
