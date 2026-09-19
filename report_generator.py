"""
Smart Meeting Summarizer: Document & Report Generation Engine
Generates publication-ready PDF Minutes of Meeting (MoM), Markdown archives,
and formatted team email drafts.
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

def generate_pdf_mom(mom_data: dict, output_filename: str = None) -> str:
    """Generates an executive-ready PDF document of the Minutes of Meeting."""
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"Meeting_Minutes_{timestamp}.pdf"
        
    pdf_path = os.path.join(EXPORTS_DIR, output_filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a')
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0284c7'),
        spaceBefore=10,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    
    bullet_style = ParagraphStyle(
        'BulletPoint',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=12,
        spaceAfter=3
    )

    story = []

    # 1. Header & Title
    story.append(Paragraph(mom_data.get("title", "Executive Minutes of Meeting"), title_style))
    date_str = mom_data.get("generated_at", datetime.now().strftime("%B %d, %Y"))
    story.append(Paragraph(f"<b>Date:</b> {date_str} &nbsp;|&nbsp; <b>Tone:</b> {mom_data.get('telemetry', {}).get('tone', 'Productive')} &nbsp;|&nbsp; <b>Compression:</b> {mom_data.get('telemetry', {}).get('compression_ratio', '75%')}", body_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    # 2. Executive Summary
    story.append(Paragraph("1. Executive Summary", section_heading))
    story.append(Paragraph(mom_data.get("executive_summary", "No summary available."), body_style))
    story.append(Spacer(1, 10))

    # 3. Point-Wise Discussion Topics
    story.append(Paragraph("2. Point-Wise Key Discussions", section_heading))
    for topic_group in mom_data.get("discussion_points", []):
        story.append(Paragraph(f"<b>📌 {topic_group.get('topic', 'Discussion Topic')}:</b>", body_style))
        for bullet in topic_group.get("bullets", []):
            story.append(Paragraph(f"• {bullet}", bullet_style))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 6))

    # 4. Action Items Table
    story.append(Paragraph("3. Action Items & Deliverables Matrix", section_heading))
    action_items = mom_data.get("action_items", [])
    if action_items:
        table_data = [["Task Description", "Owner", "Target Deadline", "Priority"]]
        for a in action_items:
            table_data.append([
                Paragraph(a.get("task", ""), body_style),
                Paragraph(f"<b>{a.get('owner', 'TBD')}</b>", body_style),
                Paragraph(a.get("deadline", "Next Sprint"), body_style),
                Paragraph(a.get("priority", "Medium"), body_style)
            ])
            
        action_table = Table(table_data, colWidths=[280, 85, 105, 60])
        action_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#f1f5f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(action_table)
    else:
        story.append(Paragraph("• No explicit pending action items recorded.", bullet_style))
    story.append(Spacer(1, 10))

    # 5. Decisions Taken
    story.append(Paragraph("4. Key Decisions & Agreements", section_heading))
    for d in mom_data.get("decisions", []):
        story.append(Paragraph(f"✅ <b>Decision:</b> {d}", bullet_style))
    story.append(Spacer(1, 8))

    # 6. Risks & Blockers
    if mom_data.get("risks_and_blockers"):
        story.append(Paragraph("5. Identified Risks & Follow-Ups", section_heading))
        for r in mom_data.get("risks_and_blockers", []):
            story.append(Paragraph(f"⚠️ {r}", bullet_style))

    # Build Document
    doc.build(story)
    return pdf_path

def generate_markdown_mom(mom_data: dict) -> str:
    """Generates clean Markdown representation of the Minutes of Meeting."""
    lines = [
        f"# {mom_data.get('title', 'Minutes of Meeting')}",
        f"**Date:** {mom_data.get('generated_at')} | **Tone:** {mom_data.get('telemetry', {}).get('tone')} | **Compression:** {mom_data.get('telemetry', {}).get('compression_ratio')}",
        "",
        "## 1. Executive Summary",
        mom_data.get("executive_summary", ""),
        "",
        "## 2. Key Discussion Topics (Point-Wise)"
    ]
    
    for group in mom_data.get("discussion_points", []):
        lines.append(f"\n### 📌 {group.get('topic')}")
        for bullet in group.get("bullets", []):
            lines.append(f"- {bullet}")
            
    lines.append("\n## 3. Action Items Matrix")
    lines.append("| Task | Assignee | Deadline | Priority |")
    lines.append("| :--- | :--- | :--- | :--- |")
    for a in mom_data.get("action_items", []):
        lines.append(f"| {a.get('task')} | **{a.get('owner')}** | {a.get('deadline')} | `{a.get('priority')}` |")
        
    lines.append("\n## 4. Key Decisions Reached")
    for d in mom_data.get("decisions", []):
        lines.append(f"- ✅ **Decision:** {d}")
        
    if mom_data.get("risks_and_blockers"):
        lines.append("\n## 5. Identified Risks & Follow-Ups")
        for r in mom_data.get("risks_and_blockers", []):
            lines.append(f"- ⚠️ {r}")
            
    return "\n".join(lines)

def generate_email_draft(mom_data: dict) -> str:
    """Generates a structured email draft ready to copy and send to meeting participants."""
    lines = [
        f"Subject: Minutes of Meeting: {mom_data.get('title')}",
        "",
        "Hi Team,",
        "",
        "Thank you for attending today's sync. Below is the point-wise summary of discussions, decisions, and assigned action items.",
        "",
        "🎯 EXECUTIVE SUMMARY:",
        mom_data.get("executive_summary", ""),
        "",
        "📋 KEY DISCUSSION POINTS:"
    ]
    
    for group in mom_data.get("discussion_points", []):
        lines.append(f"\n• {group.get('topic')}:")
        for bullet in group.get("bullets", []):
            lines.append(f"   - {bullet}")
            
    lines.append("\n📌 ACTION ITEMS & DELIVERABLES:")
    for a in mom_data.get("action_items", []):
        lines.append(f"• [{a.get('priority').upper()}] {a.get('owner')}: {a.get('task')} (Due: {a.get('deadline')})")
        
    lines.append("\n✅ KEY DECISIONS MADE:")
    for d in mom_data.get("decisions", []):
        lines.append(f"• {d}")
        
    lines.append("\nPlease let me know if any updates or corrections are needed.")
    lines.append("\nBest regards,\nMeeting Secretary")
    return "\n".join(lines)
