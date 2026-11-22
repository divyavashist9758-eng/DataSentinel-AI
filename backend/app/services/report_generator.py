import os
import io
import csv
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models.investigation import Investigation
from app.models.dataset import Dataset
from app.core.logging import logger

class ReportGenerator:
    @classmethod
    def generate_investigation_pdf(cls, investigation: Investigation, dataset: Dataset) -> bytes:
        """Generate a structured, professional PDF investigation report."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=12
        )
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#2563eb'),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6
        )

        elements = []

        # Header Title
        elements.append(Paragraph("DataSentinel AI - Autonomous Investigation Report", title_style))
        elements.append(Paragraph(f"<b>Dataset:</b> {dataset.name} | <b>Investigation ID:</b> {investigation.id} | <b>Status:</b> {investigation.status}", body_style))
        elements.append(Paragraph(f"<b>Generated:</b> {investigation.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')} | <b>Confidence:</b> {investigation.confidence_score}%", body_style))
        elements.append(Spacer(1, 12))

        # Executive Summary
        elements.append(Paragraph("Executive Summary", heading_style))
        summary_text = investigation.summary or "Autonomous investigation completed. No critical anomalies detected."
        elements.append(Paragraph(summary_text, body_style))
        elements.append(Spacer(1, 8))

        # Root Cause
        elements.append(Paragraph("Root Cause Analysis", heading_style))
        root_cause_text = investigation.root_cause_hypothesis or "No operational failure identified."
        elements.append(Paragraph(root_cause_text, body_style))
        elements.append(Spacer(1, 8))

        # Agent Traces Table
        elements.append(Paragraph("Multi-Agent Investigation Traces", heading_style))
        traces = investigation.agent_traces or []
        table_data = [["Agent Name", "Status", "Duration (ms)", "Summary Insight"]]
        
        for t in traces:
            name = t.get("agent_name", "Agent")
            st = t.get("status", "SUCCESS")
            dur = str(t.get("execution_time_ms", 0))
            insight = t.get("summary_insight", "")[:75] + ("..." if len(t.get("summary_insight", "")) > 75 else "")
            table_data.append([name, st, dur, insight])

        if len(table_data) > 1:
            t_table = Table(table_data, colWidths=[120, 60, 80, 260])
            t_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ]))
            elements.append(t_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @classmethod
    def generate_investigation_csv(cls, investigation: Investigation, dataset: Dataset) -> str:
        """Export agent traces and findings in CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["Investigation ID", "Dataset Name", "Status", "Confidence", "Agent Name", "Duration MS", "Summary Insight"])
        traces = investigation.agent_traces or []
        for t in traces:
            writer.writerow([
                investigation.id,
                dataset.name,
                investigation.status,
                investigation.confidence_score,
                t.get("agent_name", ""),
                t.get("execution_time_ms", 0),
                t.get("summary_insight", "")
            ])
            
        return output.getvalue()
