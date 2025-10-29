from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem, Image, Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import os
import matplotlib.pyplot as plt

def generate_pdf_report(role, result, feedback, ats_score, portfolio_data=None, resume_skill_df=None):
    out_dir = os.path.abspath(os.path.dirname(__file__))
    filename = f"resume_portfolio_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(out_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0A3D62"),
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1E3799"),
        spaceBefore=10,
        spaceAfter=6
    )

    normal = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        fontSize=11,
        leading=15
    )

    highlight = ParagraphStyle(
        "Highlight",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#006266")
    )

    footer = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=9,
        leading=11,
        alignment=1,
        textColor=colors.grey
    )

    content = []

    content.append(Paragraph("Resume & Portfolio Analyzer Report", title_style))
    content.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"<b>Selected Role:</b> {role}", normal))
    content.append(Spacer(1, 8))

    # keyword analysis
    content.append(Paragraph("Keyword Analysis", section_style))
    found = result.get("found", []) if isinstance(result, dict) else []
    missing = result.get("missing", []) if isinstance(result, dict) else []
    content.append(Paragraph(f"<b>Found Keywords:</b> {', '.join(found) if found else 'None'}", normal))
    content.append(Paragraph(f"<b>Missing Keywords:</b> {', '.join(missing) if missing else 'None'}", normal))
    content.append(Spacer(1, 8))

    # resume feedback
    content.append(Paragraph("Resume Feedback", section_style))
    feedback_lines = []
    if isinstance(feedback, (list, tuple)):
        for item in feedback:
            if isinstance(item, str):
                feedback_lines.extend([ln.strip() for ln in item.splitlines() if ln.strip()])
    else:
        feedback_lines.extend([ln.strip() for ln in str(feedback).splitlines() if ln.strip()])

    list_items = [ListItem(Paragraph(line.lstrip("-•* ").strip(), normal), bulletColor=colors.HexColor("#0A3D62")) for line in feedback_lines]
    if list_items:
        content.append(ListFlowable(list_items, bulletType="bullet", leftIndent=12))
    else:
        content.append(Paragraph("No specific feedback generated.", normal))

    content.append(Spacer(1, 10))

    # ats score
    content.append(Paragraph("ATS Score", section_style))
    content.append(Paragraph(f"Your resume scored <b>{ats_score}/100</b> for the role: <b>{role}</b>", normal))
    content.append(Spacer(1, 12))

    # portfolio section
    if portfolio_data:
        content.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
        content.append(Spacer(1, 8))
        content.append(Paragraph("Portfolio Summary (GitHub)", section_style))
        username = portfolio_data.get("username", "N/A")
        repos = portfolio_data.get("repositories", "N/A")
        followers = portfolio_data.get("followers", "N/A")
        contributions = portfolio_data.get("contributions", "N/A")

        content.append(Paragraph(f"<b>GitHub Username:</b> {username}", normal))
        content.append(Paragraph(f"<b>Repositories:</b> {repos}", normal))
        content.append(Paragraph(f"<b>Followers:</b> {followers}", normal))
        content.append(Paragraph(f"<b>Contributions (this year):</b> {contributions}", normal))
        content.append(Spacer(1, 10))

        # generate charts
        github_langs = portfolio_data.get("top_languages", {})

        if resume_skill_df is not None and not resume_skill_df.empty and github_langs:
            # resume pie chart
            pie_path = os.path.join(out_dir, "resume_pie_chart.png")
            plt.figure(figsize=(4, 4))
            plt.pie(resume_skill_df["Count"], labels=resume_skill_df["Skill"], autopct="%1.1f%%", startangle=90)
            plt.title("Resume Skill Distribution")
            plt.tight_layout()
            plt.savefig(pie_path)
            plt.close()

            # gitHub bar chart
            bar_path = os.path.join(out_dir, "github_bar_chart.png")
            plt.figure(figsize=(4, 4))
            langs = list(github_langs.keys())
            lines = list(github_langs.values())
            plt.bar(langs, lines)
            plt.xlabel("Languages")
            plt.ylabel("Lines of Code")
            plt.title("GitHub Language Distribution")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(bar_path)
            plt.close()

            content.append(Paragraph("Combined Skill Visualization", section_style))
            table_data = [
                [Image(pie_path, width=200, height=200), Image(bar_path, width=200, height=200)]
            ]
            table = Table(table_data, hAlign="CENTER")
            table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            content.append(table)
            content.append(Spacer(1, 12))

    content.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    content.append(Spacer(1, 6))
    content.append(Paragraph("Generated by Resume & Portfolio Analyzer", footer))
    doc.build(content)

    return filepath