from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def generate_pdf_report(role, found, missing, feedback, ats_score):

    filename = f"resume_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("🎓 Resume & Portfolio Analyzer Report", styles['Title']))
    content.append(Spacer(1, 20))

    content.append(Paragraph(f"<b>Selected Role:</b> {role}", styles['Normal']))
    content.append(Spacer(1, 12))

    content.append(Paragraph("<b>🔎 Keyword Analysis</b>", styles['Heading2']))
    content.append(Paragraph(f"<b>✅ Found Keywords:</b> {', '.join(found) if found else 'None'}", styles['Normal']))
    content.append(Paragraph(f"<b>❌ Missing Keywords:</b> {', '.join(missing) if missing else 'None'}", styles['Normal']))
    content.append(Spacer(1, 12))

    content.append(Paragraph("<b>📝 Resume Feedback</b>", styles['Heading2']))
    for line in feedback:
        content.append(Paragraph(line, styles['Normal']))
    content.append(Spacer(1, 12))

    content.append(Paragraph("<b>📊 ATS Score</b>", styles['Heading2']))
    content.append(Paragraph(f"⭐ Your resume scored <b>{ats_score}/100</b> for the role: <b>{role}</b>", styles['Normal']))

    doc.build(content)

    return filename