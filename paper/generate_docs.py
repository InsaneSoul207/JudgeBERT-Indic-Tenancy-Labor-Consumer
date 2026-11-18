"""
Utility script to generate formatted Word (.docx) and PDF versions of the IEEE research paper.
"""

import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def generate_docx():
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t_run = title_p.add_run('Explainable Multilingual Legal Meaning Preservation Using Cross-Encoder Transformers\n')
    t_run.font.size = Pt(16)
    t_run.font.bold = True
    t_run.font.name = 'Times New Roman'

    author_p = doc.add_paragraph()
    author_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    a_run = author_p.add_run('Eshaan Mishra, Fairy Tyagi, Ansh Dixit, Anvi Tyagi\nDepartment of Computer Science and Engineering, Bennett University, Greater Noida, India\nCourse: CSET 346 – Natural Language Processing | Instructor: Dr. Surabhi Solanki\n')
    a_run.font.size = Pt(9.5)
    a_run.font.italic = True
    a_run.font.name = 'Times New Roman'

    with open('paper/IEEE_Research_Paper.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith('# ') or line.startswith('---'):
            continue
        if line.startswith('## '):
            h = doc.add_heading(line.replace('## ', ''), level=1)
            for r in h.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(12)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 51, 102)
        elif line.startswith('### '):
            h = doc.add_heading(line.replace('### ', ''), level=2)
            for r in h.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(50, 50, 50)
        elif line.startswith('|') and '---' not in line:
            cols = [c.strip() for c in line.split('|')[1:-1]]
            text = '  |  '.join(cols)
            p = doc.add_paragraph()
            r = p.add_run(text)
            r.font.name = 'Courier New'
            r.font.size = Pt(8.5)
        else:
            clean = line.replace('**', '').replace('*', '').replace('$', '')
            p = doc.add_paragraph()
            r = p.add_run(clean)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)

    doc.save('paper/IEEE_Research_Paper.docx')
    print('Generated paper/IEEE_Research_Paper.docx successfully!')

def generate_pdf():
    pdf_path = 'paper/IEEE_Research_Paper.pdf'
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=1, spaceAfter=8
    )
    author_style = ParagraphStyle(
        'DocAuthor', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=11, alignment=1, spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'DocH1', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=13, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor('#002B49')
    )
    body_style = ParagraphStyle(
        'DocBody', parent=styles['BodyText'],
        fontName='Helvetica', fontSize=8.5, leading=11, spaceAfter=5
    )

    story = []
    story.append(Paragraph('Explainable Multilingual Legal Meaning Preservation Using Cross-Encoder Transformers', title_style))
    story.append(Paragraph('Eshaan Mishra, Fairy Tyagi, Ansh Dixit, Anvi Tyagi<br/>Department of Computer Science and Engineering, Bennett University, Greater Noida, India<br/>Course: CSET 346 – Natural Language Processing | Instructor: Dr. Surabhi Solanki', author_style))

    with open('paper/IEEE_Research_Paper.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith('# ') or line.startswith('---'):
            continue
        if line.startswith('## '):
            story.append(Paragraph(line.replace('## ', ''), h1_style))
        elif line.startswith('### '):
            story.append(Paragraph(f"<b>{line.replace('### ', '')}</b>", body_style))
        elif line.startswith('|') and '---' not in line:
            cols = [c.strip() for c in line.split('|')[1:-1]]
            text = ' &nbsp;|&nbsp; '.join(cols)
            story.append(Paragraph(f"<font face='Courier' size=7.5>{text}</font>", body_style))
        else:
            # Cleanly strip markdown formatting for ReportLab
            clean = line.replace('**', '').replace('*', '').replace('$', '').replace('`', '')
            clean = clean.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(clean, body_style))

    doc.build(story)
    print('Generated paper/IEEE_Research_Paper.pdf successfully!')

if __name__ == '__main__':
    generate_docx()
    generate_pdf()
