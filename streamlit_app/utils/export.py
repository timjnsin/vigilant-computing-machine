import streamlit as st
import pandas as pd
import numpy as np
import io
import base64
import tempfile
import os
import time
import uuid
import json
import qrcode
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.platypus import PageBreak, Frame, PageTemplate, NextPageTemplate
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
import xlsxwriter
import markdown
from weasyprint import HTML, CSS
from typing import Dict, List, Optional, Union, Any, Tuple
import hashlib

# Constants for styling
BRAND_COLORS = {
    "primary": "#f59e0b",     # Gold
    "secondary": "#0f172a",   # Dark blue
    "accent": "#6366f1",      # Purple
    "success": "#10b981",     # Green
    "warning": "#f97316",     # Orange
    "danger": "#ef4444",      # Red
    "background": "#0f172a",  # Dark blue
    "text": "#f8fafc",        # Light gray
    "muted": "#94a3b8"        # Muted gray
}

LOGO_PATH = "streamlit_app/assets/logo.png"
DEFAULT_FONT = "Helvetica"

# Helper functions for export styling
def apply_brand_styling(doc: SimpleDocTemplate) -> List[ParagraphStyle]:
    """Apply consistent brand styling to a ReportLab document."""
    styles = getSampleStyleSheet()
    
    # Create custom styles based on brand colors
    styles.add(ParagraphStyle(
        name='Heading1_Brand',
        parent=styles['Heading1'],
        fontName=DEFAULT_FONT+'-Bold',
        fontSize=18,
        textColor=colors.HexColor(BRAND_COLORS["primary"]),
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='Heading2_Brand',
        parent=styles['Heading2'],
        fontName=DEFAULT_FONT+'-Bold',
        fontSize=14,
        textColor=colors.HexColor(BRAND_COLORS["primary"]),
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='Normal_Brand',
        parent=styles['Normal'],
        fontName=DEFAULT_FONT,
        fontSize=10,
        textColor=colors.HexColor(BRAND_COLORS["text"]),
        backColor=colors.HexColor(BRAND_COLORS["background"])
    ))
    
    return styles

def create_branded_header(canvas, doc):
    """Add branded header to PDF pages."""
    canvas.saveState()
    
    # Add logo if it exists
    try:
        if os.path.exists(LOGO_PATH):
            canvas.drawImage(LOGO_PATH, inch, doc.height + inch, width=1.5*inch, height=0.5*inch)
    except:
        pass  # Skip logo if file not found
    
    # Add title
    canvas.setFont(DEFAULT_FONT+'-Bold', 10)
    canvas.setFillColor(colors.HexColor(BRAND_COLORS["primary"]))
    canvas.drawString(3*inch, doc.height + inch, "Financial Model Export")
    
    # Add date
    canvas.setFont(DEFAULT_FONT, 8)
    canvas.setFillColor(colors.HexColor(BRAND_COLORS["muted"]))
    canvas.drawRightString(doc.width + inch, doc.height + inch, 
                           f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Add horizontal line
    canvas.setStrokeColor(colors.HexColor(BRAND_COLORS["primary"]))
    canvas.line(inch, doc.height + 0.9*inch, doc.width + inch, doc.height + 0.9*inch)
    
    canvas.restoreState()

def create_branded_footer(canvas, doc):
    """Add branded footer to PDF pages."""
    canvas.saveState()
    
    # Add horizontal line
    canvas.setStrokeColor(colors.HexColor(BRAND_COLORS["primary"]))
    canvas.line(inch, 0.9*inch, doc.width + inch, 0.9*inch)
    
    # Add page number
    canvas.setFont(DEFAULT_FONT, 8)
    canvas.setFillColor(colors.HexColor(BRAND_COLORS["muted"]))
    page_num = canvas.getPageNumber()
    canvas.drawString(inch, 0.75*inch, f"Page {page_num}")
    
    # Add confidentiality notice
    canvas.setFont(DEFAULT_FONT+'-Italic', 7)
    canvas.drawRightString(doc.width + inch, 0.75*inch, 
                           "Confidential - For internal use only")
    
    canvas.restoreState()

def show_export_progress(message: str, progress_value: float):
    """Display a progress bar with custom message."""
    if "export_progress" not in st.session_state:
        st.session_state.export_progress = st.progress(0.0)
        st.session_state.export_status = st.empty()
    
    st.session_state.export_progress.progress(progress_value)
    st.session_state.export_status.text(message)
    time.sleep(0.1)  # Small delay for visual effect

def show_export_success(message: str, file_path: str = None, file_data: bytes = None, file_name: str = None):
    """Show success notification with download button if file is provided."""
    if "export_progress" in st.session_state:
        st.session_state.export_progress.empty()
        st.session_state.export_status.empty()
        del st.session_state.export_progress
        del st.session_state.export_status
    
    # Success message with animation
    success_container = st.empty()
    success_container.success(message)
    
    # Add download button if file is provided
    if file_data and file_name:
        b64 = base64.b64encode(file_data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}" ' \
               f'style="display: inline-block; padding: 0.5rem 1rem; ' \
               f'background-color: {BRAND_COLORS["primary"]}; color: white; ' \
               f'text-decoration: none; border-radius: 4px; margin-top: 1rem;">' \
               f'⬇️ Download {file_name}</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    # Clear success message after a few seconds
    time.sleep(5)
    success_container.empty()

def generate_chart_for_pdf(chart_type: str, data: Dict[str, Any], width: int = 400, height: int = 200) -> Drawing:
    """Generate a ReportLab chart for PDF inclusion."""
    drawing = Drawing(width, height)
    
    if chart_type == "pie":
        chart = Pie()
        chart.x = 50
        chart.y = 50
        chart.width = width - 100
        chart.height = height - 100
        chart.data = data.get("values", [25, 25, 25, 25])
        chart.labels = data.get("labels", ["A", "B", "C", "D"])
        chart.slices.strokeWidth = 0.5
        
        # Apply brand colors
        for i, color_key in enumerate(["primary", "accent", "success", "warning"]):
            if i < len(chart.slices):
                chart.slices[i].fillColor = colors.HexColor(BRAND_COLORS[color_key])
        
        drawing.add(chart)
        
    elif chart_type == "line":
        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 50
        chart.width = width - 100
        chart.height = height - 100
        chart.data = data.get("series", [[1, 2, 3, 4, 5]])
        chart.categoryAxis.categoryNames = data.get("labels", ["A", "B", "C", "D", "E"])
        chart.valueAxis.valueMin = data.get("min", 0)
        chart.valueAxis.valueMax = data.get("max", 10)
        chart.lines[0].strokeColor = colors.HexColor(BRAND_COLORS["primary"])
        chart.lines[0].strokeWidth = 2
        
        drawing.add(chart)
        
    elif chart_type == "bar":
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.width = width - 100
        chart.height = height - 100
        chart.data = data.get("series", [[1, 2, 3, 4, 5]])
        chart.categoryAxis.categoryNames = data.get("labels", ["A", "B", "C", "D", "E"])
        chart.valueAxis.valueMin = data.get("min", 0)
        chart.valueAxis.valueMax = data.get("max", 10)
        chart.bars[0].fillColor = colors.HexColor(BRAND_COLORS["primary"])
        
        drawing.add(chart)
    
    return drawing

@st.cache_data
def export_pitch_deck(
    title: str,
    data: Dict[str, Any],
    charts: Dict[str, Any],
    assumptions: Dict[str, Any]
) -> bytes:
    """
    Generate a 5-slide PDF pitch deck with key charts and assumptions.
    
    Parameters:
    -----------
    title : str
        Title of the pitch deck
    data : Dict[str, Any]
        Dictionary containing financial data
    charts : Dict[str, Any]
        Dictionary containing chart configurations
    assumptions : Dict[str, Any]
        Dictionary containing model assumptions
    
    Returns:
    --------
    bytes
        PDF file as bytes
    """
    show_export_progress("Initializing pitch deck export...", 0.1)
    
    # Create PDF buffer
    buffer = io.BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=1.2*inch,
        bottomMargin=inch
    )
    
    # Apply brand styling
    styles = apply_brand_styling(doc)
    
    # Create story (content)
    story = []
    
    # Slide 1: Title Page
    show_export_progress("Creating title slide...", 0.2)
    story.append(Paragraph(title, styles["Heading1_Brand"]))
    story.append(Spacer(1, 0.5*inch))
    
    # Add company info
    company_info = f"<b>Prepared for:</b> {data.get('company_name', 'Company')}"
    story.append(Paragraph(company_info, styles["Normal_Brand"]))
    story.append(Spacer(1, 0.25*inch))
    
    # Add date
    date_info = f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}"
    story.append(Paragraph(date_info, styles["Normal_Brand"]))
    story.append(Spacer(1, inch))
    
    # Add key metrics table
    key_metrics = [
        ["Metric", "Value"],
        ["IRR", f"{data.get('irr', 0):.1%}"],
        ["MOIC", f"{data.get('moic', 0):.2f}x"],
        ["Payback", f"{data.get('payback', 0):.1f} years"],
        ["5-Year Revenue", f"${data.get('total_revenue', 0)/1000000:.1f}M"]
    ]
    
    table = Table(key_metrics, colWidths=[2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor(BRAND_COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), DEFAULT_FONT+'-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (1, 0), 8),
        ('BACKGROUND', (0, 1), (1, -1), colors.HexColor(BRAND_COLORS["secondary"])),
        ('TEXTCOLOR', (0, 1), (1, -1), colors.HexColor(BRAND_COLORS["text"])),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BRAND_COLORS["muted"])),
    ]))
    
    story.append(table)
    story.append(PageBreak())
    
    # Slide 2: Revenue Projection
    show_export_progress("Creating revenue projection slide...", 0.4)
    story.append(Paragraph("Revenue Projection", styles["Heading1_Brand"]))
    story.append(Spacer(1, 0.25*inch))
    
    # Add revenue chart
    if "revenue" in charts:
        revenue_chart = generate_chart_for_pdf("line", charts["revenue"], width=500, height=300)
        story.append(revenue_chart)
    
    # Add revenue breakdown table
    revenue_data = [
        ["Year", "Revenue", "Growth"],
        ["Year 1", f"${data.get('revenue_y1', 0)/1000:.1f}K", ""],
        ["Year 2", f"${data.get('revenue_y2', 0)/1000:.1f}K", f"{data.get('growth_y2', 0):.1%}"],
        ["Year 3", f"${data.get('revenue_y3', 0)/1000:.1f}K", f"{data.get('growth_y3', 0):.1%}"],
        ["Year 4", f"${data.get('revenue_y4', 0)/1000:.1f}K", f"{data.get('growth_y4', 0):.1%}"],
        ["Year 5", f"${data.get('revenue_y5', 0)/1000:.1f}K", f"{data.get('growth_y5', 0):.1%}"]
    ]
    
    table = Table(revenue_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.HexColor(BRAND_COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.white),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), DEFAULT_FONT+'-Bold'),
        ('FONTSIZE', (0, 0), (2, 0), 10),
        ('BOTTOMPADDING', (0, 0), (2, 0), 8),
        ('BACKGROUND', (0, 1), (2, -1), colors.HexColor(BRAND_COLORS["secondary"])),
        ('TEXTCOLOR', (0, 1), (2, -1), colors.HexColor(BRAND_COLORS["text"])),
        ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BRAND_COLORS["muted"])),
    ]))
    
    story.append(Spacer(1, 0.25*inch))
    story.append(table)
    story.append(PageBreak())
    
    # Slide 3: Channel Mix
    show_export_progress("Creating channel mix slide...", 0.6)
    story.append(Paragraph("Channel Mix", styles["Heading1_Brand"]))
    story.append(Spacer(1, 0.25*inch))
    
    # Add channel mix chart
    if "channel_mix" in charts:
        channel_chart = generate_chart_for_pdf("pie", charts["channel_mix"], width=400, height=300)
        story.append(channel_chart)
    
    # Add channel mix table
    channels = data.get("channels", {})
    channel_data = [["Channel", "Revenue", "Margin", "% of Total"]]
    
    for channel, values in channels.items():
        channel_data.append([
            channel,
            f"${values.get('revenue', 0)/1000:.1f}K",
            f"{values.get('margin', 0):.1%}",
            f"{values.get('percent', 0):.1%}"
        ])
    
    table = Table(channel_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), colors.HexColor(BRAND_COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (3, 0), colors.white),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (3, 0), DEFAULT_FONT+'-Bold'),
        ('FONTSIZE', (0, 0), (3, 0), 10),
        ('BOTTOMPADDING', (0, 0), (3, 0), 8),
        ('BACKGROUND', (0, 1), (3, -1), colors.HexColor(BRAND_COLORS["secondary"])),
        ('TEXTCOLOR', (0, 1), (3, -1), colors.HexColor(BRAND_COLORS["text"])),
        ('ALIGN', (1, 1), (3, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BRAND_COLORS["muted"])),
    ]))
    
    story.append(Spacer(1, 0.25*inch))
    story.append(table)
    story.append(PageBreak())
    
    # Slide 4: Cash Flow
    show_export_progress("Creating cash flow slide...", 0.8)
    story.append(Paragraph("Cash Flow Projection", styles["Heading1_Brand"]))
    story.append(Spacer(1, 0.25*inch))
    
    # Add cash flow chart
    if "cash_flow" in charts:
        cash_flow_chart = generate_chart_for_pdf("bar", charts["cash_flow"], width=500, height=300)
        story.append(cash_flow_chart)
    
    # Add cash flow table
    cf_data = [
        ["Year", "Revenue", "Expenses", "Cash Flow", "Cumulative"],
        ["Year 1", f"${data.get('revenue_y1', 0)/1000:.1f}K", f"${data.get('expenses_y1', 0)/1000:.1f}K", 
         f"${data.get('cf_y1', 0)/1000:.1f}K", f"${data.get('cumulative_y1', 0)/1000:.1f}K"],
        ["Year 2", f"${data.get('revenue_y2', 0)/1000:.1f}K", f"${data.get('expenses_y2', 0)/1000:.1f}K", 
         f"${data.get('cf_y2', 0)/1000:.1f}K", f"${data.get('cumulative_y2', 0)/1000:.1f}K"],
        ["Year 3", f"${data.get('revenue_y3', 0)/1000:.1f}K", f"${data.get('expenses_y3', 0)/1000:.1f}K", 
         f"${data.get('cf_y3', 0)/1000:.1f}K", f"${data.get('cumulative_y3', 0)/1000:.1f}K"],
        ["Year 4", f"${data.get('revenue_y4', 0)/1000:.1f}K", f"${data.get('expenses_y4', 0)/1000:.1f}K", 
         f"${data.get('cf_y4', 0)/1000:.1f}K", f"${data.get('cumulative_y4', 0)/1000:.1f}K"],
        ["Year 5", f"${data.get('revenue_y5', 0)/1000:.1f}K", f"${data.get('expenses_y5', 0)/1000:.1f}K", 
         f"${data.get('cf_y5', 0)/1000:.1f}K", f"${data.get('cumulative_y5', 0)/1000:.1f}K"]
    ]
    
    table = Table(cf_data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (4, 0), colors.HexColor(BRAND_COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (4, 0), colors.white),
        ('ALIGN', (0, 0), (4, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (4, 0), DEFAULT_FONT+'-Bold'),
        ('FONTSIZE', (0, 0), (4, 0), 10),
        ('BOTTOMPADDING', (0, 0), (4, 0), 8),
        ('BACKGROUND', (0, 1), (4, -1), colors.HexColor(BRAND_COLORS["secondary"])),
        ('TEXTCOLOR', (0, 1), (4, -1), colors.HexColor(BRAND_COLORS["text"])),
        ('ALIGN', (1, 1), (4, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BRAND_COLORS["muted"])),
    ]))
    
    story.append(Spacer(1, 0.25*inch))
    story.append(table)
    story.append(PageBreak())
    
    # Slide 5: Assumptions
    show_export_progress("Creating assumptions slide...", 0.9)
    story.append(Paragraph("Key Assumptions", styles["Heading1_Brand"]))
    story.append(Spacer(1, 0.25*inch))
    
    # Add assumptions table
    assumption_data = [["Category", "Assumption", "Value"]]
    
    for category, items in assumptions.items():
        for name, value in items.items():
            # Format value based on type
            if isinstance(value, float):
                if 0 <= value <= 1:  # Likely a percentage
                    formatted_value = f"{value:.1%}"
                else:
                    formatted_value = f"{value:,.2f}"
            else:
                formatted_value = str(value)
                
            assumption_data.append([category, name, formatted_value])
    
    table = Table(assumption_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.HexColor(BRAND_COLORS["primary"])),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.white),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), DEFAULT_FONT+'-Bold'),
        ('FONTSIZE', (0, 0), (2, 0), 10),
        ('BOTTOMPADDING', (0, 0), (2, 0), 8),
        ('BACKGROUND', (0, 1), (2, -1), colors.HexColor(BRAND_COLORS["secondary"])),
        ('TEXTCOLOR', (0, 1), (2, -1), colors.HexColor(BRAND_COLORS["text"])),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BRAND_COLORS["muted"])),
    ]))
    
    story.append(table)
    
    # Build the PDF with custom header and footer
    show_export_progress("Finalizing PDF document...", 0.95)
    doc.build(story, onFirstPage=create_branded_header, onLaterPages=create_branded_header)
    
    # Get PDF from buffer
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    show_export_progress("Export complete!", 1.0)
    return pdf_bytes

@st.cache_data
def export_excel_summary(
    data: Dict[str, Any],
    charts_data: Dict[str, pd.DataFrame]
) -> bytes:
    """
    Generate a one-page Excel summary with key metrics and source data.
    
    Parameters:
    -----------
    data : Dict[str, Any]
        Dictionary containing financial data
    charts_data : Dict[str, pd.DataFrame]
        Dictionary containing source data for charts
    
    Returns:
    --------
    bytes
        Excel file as bytes
    """
    show_export_progress("Initializing Excel export...", 0.1)
    
    # Create Excel buffer
    buffer = io.BytesIO()
    
    # Create Excel workbook
    workbook = xlsxwriter.Workbook(buffer)
    
    # Create summary worksheet
    show_export_progress("Creating summary worksheet...", 0.3)
    summary = workbook.add_worksheet("Summary")
    
    # Define formats
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 16,
        'font_color': BRAND_COLORS["primary"],
        'align': 'center',
        'valign': 'vcenter',
        'border': 0
    })
    
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'font_color': 'white',
        'bg_color': BRAND_COLORS["primary"],
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'font_size': 10,
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    number_format = workbook.add_format({
        'font_size': 10,
        'align': 'right',
        'valign': 'vcenter',
        'border': 1,
        'num_format': '#,##0'
    })
    
    currency_format = workbook.add_format({
        'font_size': 10,
        'align': 'right',
        'valign': 'vcenter',
        'border': 1,
        'num_format': '$#,##0'
    })
    
    percent_format = workbook.add_format({
        'font_size': 10,
        'align': 'right',
        'valign': 'vcenter',
        'border': 1,
        'num_format': '0.0%'
    })
    
    highlight_format = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'font_color': BRAND_COLORS["primary"],
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    # Set column widths
    summary.set_column('A:A', 15)
    summary.set_column('B:G', 12)
    
    # Add title
    summary.merge_range('A1:G1', 'FINANCIAL MODEL SUMMARY', title_format)
    summary.set_row(0, 30)
    
    # Add key metrics section
    show_export_progress("Adding key metrics...", 0.4)
    summary.merge_range('A3:C3', 'KEY METRICS', header_format)
    summary.merge_range('D3:G3', 'REVENUE BREAKDOWN', header_format)
    
    # Add key metrics data
    metrics = [
        ["IRR", data.get('irr', 0), percent_format],
        ["MOIC", data.get('moic', 0), number_format],
        ["Payback Period", data.get('payback', 0), number_format],
        ["5-Year Revenue", data.get('total_revenue', 0), currency_format],
        ["5-Year Profit", data.get('total_profit', 0), currency_format]
    ]
    
    for i, (label, value, fmt) in enumerate(metrics):
        summary.write(3+i, 0, label, cell_format)
        summary.write(3+i, 1, value, fmt)
    
    # Add revenue breakdown
    channels = data.get('channels', {})
    summary.write(3, 3, 'Channel', cell_format)
    summary.write(3, 4, 'Revenue', header_format)
    summary.write(3, 5, 'Margin', header_format)
    summary.write(3, 6, '% of Total', header_format)
    
    row = 4
    for channel, values in channels.items():
        summary.write(row, 3, channel, cell_format)
        summary.write(row, 4, values.get('revenue', 0), currency_format)
        summary.write(row, 5, values.get('margin', 0), percent_format)
        summary.write(row, 6, values.get('percent', 0), percent_format)
        row += 1
    
    # Add annual projections
    show_export_progress("Adding annual projections...", 0.6)
    summary.merge_range('A10:G10', 'ANNUAL PROJECTIONS', header_format)
    
    # Headers
    projection_headers = ['Year', 'Revenue', 'Growth', 'Expenses', 'Profit', 'Margin', 'Cumulative']
    for i, header in enumerate(projection_headers):
        summary.write(10, i, header, header_format)
    
    # Data
    for year in range(1, 6):
        summary.write(10+year, 0, f"Year {year}", cell_format)
        summary.write(10+year, 1, data.get(f'revenue_y{year}', 0), currency_format)
        
        if year > 1:
            summary.write(10+year, 2, data.get(f'growth_y{year}', 0), percent_format)
        else:
            summary.write(10+year, 2, "Base", cell_format)
            
        summary.write(10+year, 3, data.get(f'expenses_y{year}', 0), currency_format)
        summary.write(10+year, 4, data.get(f'profit_y{year}', 0), currency_format)
        summary.write(10+year, 5, data.get(f'margin_y{year}', 0), percent_format)
        summary.write(10+year, 6, data.get(f'cumulative_y{year}', 0), currency_format)
    
    # Add assumptions section
    show_export_progress("Adding assumptions...", 0.7)
    summary.merge_range('A18:G18', 'KEY ASSUMPTIONS', header_format)
    
    # Headers
    summary.write(18, 0, 'Category', header_format)
    summary.write(18, 1, 'Assumption', header_format)
    summary.merge_range('C19:D19', 'Value', header_format)
    summary.write(18, 4, 'Category', header_format)
    summary.write(18, 5, 'Assumption', header_format)
    summary.write(18, 6, 'Value', header_format)
    
    # Data
    assumptions = data.get('assumptions', {})
    left_row = 19
    right_row = 19
    
    for category, items in assumptions.items():
        for name, value in items.items():
            # Format value based on type
            if isinstance(value, float):
                if 0 <= value <= 1:  # Likely a percentage
                    fmt = percent_format
                else:
                    fmt = number_format
            else:
                fmt = cell_format
                
            # Alternate between left and right columns
            if left_row < right_row + 3:  # Keep left side from getting too far ahead
                summary.write(left_row, 0, category, cell_format)
                summary.write(left_row, 1, name, cell_format)
                summary.merge_range(f'C{left_row+1}:D{left_row+1}', value, fmt)
                left_row += 1
            else:
                summary.write(right_row, 4, category, cell_format)
                summary.write(right_row, 5, name, cell_format)
                summary.write(right_row, 6, value, fmt)
                right_row += 1
    
    # Add chart data worksheets
    show_export_progress("Adding chart data worksheets...", 0.8)
    for name, df in charts_data.items():
        # Create worksheet
        chart_sheet = workbook.add_worksheet(name[:31])  # Excel limits sheet names to 31 chars
        
        # Write headers
        for col_num, col_name in enumerate(df.columns):
            chart_sheet.write(0, col_num, col_name, header_format)
            
        # Write data
        for row_num, row_data in enumerate(df.values):
            for col_num, cell_value in enumerate(row_data):
                # Format based on data type
                if isinstance(cell_value, (int, float)):
                    if col_num == 0:  # First column often contains labels
                        chart_sheet.write(row_num + 1, col_num, cell_value, cell_format)
                    elif 0 <= cell_value <= 1:  # Likely a percentage
                        chart_sheet.write(row_num + 1, col_num, cell_value, percent_format)
                    elif cell_value >= 1000:  # Likely a currency value
                        chart_sheet.write(row_num + 1, col_num, cell_value, currency_format)
                    else:
                        chart_sheet.write(row_num + 1, col_num, cell_value, number_format)
                else:
                    chart_sheet.write(row_num + 1, col_num, cell_value, cell_format)
    
    # Set print area and options for summary sheet
    show_export_progress("Setting print options...", 0.9)
    summary.set_landscape()
    summary.fit_to_pages(1, 1)
    summary.set_print_area('A1:G30')
    summary.set_h_pagebreaks([30])
    
    # Close workbook
    workbook.close()
    
    # Get Excel from buffer
    buffer.seek(0)
    excel_bytes = buffer.getvalue()
    buffer.close()
    
    show_export_progress("Export complete!", 1.0)
    return excel_bytes

@st.cache_data
def export_investment_memo(
    title: str,
    data: Dict[str, Any],
    charts: Dict[str, Any],
    assumptions: Dict[str, Any],
    risks: List[Dict[str, str]]
) -> bytes:
    """
    Generate an investment memo as PDF with embedded charts.
    
    Parameters:
    -----------
    title : str
        Title of the investment memo
    data : Dict[str, Any]
        Dictionary containing financial data
    charts : Dict[str, Any]
        Dictionary containing chart configurations
    assumptions : Dict[str, Any]
        Dictionary containing model assumptions
    risks : List[Dict[str, str]]
        List of risk dictionaries with 'title' and 'description' keys
    
    Returns:
    --------
    bytes
        PDF file as bytes
    """
    show_export_progress("Initializing investment memo export...", 0.1)
    
    # Generate executive summary
    show_export_progress("Generating executive summary...", 0.2)
    exec_summary = f"""
    # Executive Summary
    
    This investment memo presents a financial analysis for **{data.get('company_name', 'the company')}**. 
    The model projects a **{data.get('irr', 0):.1%} IRR** and a **{data.get('moic', 0):.2f}x MOIC** 
    with a payback period of **{data.get('payback', 0):.1f} years**.
    
    Key highlights:
    
    * 5-year revenue projection of **${data.get('total_revenue', 0)/1000000:.1f}M**
    * Average annual growth rate of **{data.get('avg_growth', 0):.1%}**
    * Contribution margin of **{data.get('avg_margin', 0):.1%}**
    
    The investment thesis is supported by strong unit economics and a clear path to profitability.
    """
    
    # Generate markdown for the memo
    show_export_progress("Building investment memo content...", 0.3)
    markdown_content = f"""
    # {title}
    
    {exec_summary}
    
    ## Financial Projections
    
    The financial model projects the following key metrics over a 5-year period:
    
    | Year | Revenue | Growth | Cash Flow | Cumulative |
    |------|---------|--------|-----------|------------|
    | Year 1 | ${data.get('revenue_y1', 0)/1000:.1f}K | Base | ${data.get('cf_y1', 0)/1000:.1f}K | ${data.get('cumulative_y1', 0)/1000:.1f}K |
    | Year 2 | ${data.get('revenue_y2', 0)/1000:.1f}K | {data.get('growth_y2', 0):.1%} | ${data.get('cf_y2', 0)/1000:.1f}K | ${data.get('cumulative_y2', 0)/1000:.1f}K |
    | Year 3 | ${data.get('revenue_y3', 0)/1000:.1f}K | {data.get('growth_y3', 0):.1%} | ${data.get('cf_y3', 0)/1000:.1f}K | ${data.get('cumulative_y3', 0)/1000:.1f}K |
    | Year 4 | ${data.get('revenue_y4', 0)/1000:.1f}K | {data.get('growth_y4', 0):.1%} | ${data.get('cf_y4', 0)/1000:.1f}K | ${data.get('cumulative_y4', 0)/1000:.1f}K |
    | Year 5 | ${data.get('revenue_y5', 0)/1000:.1f}K | {data.get('growth_y5', 0):.1%} | ${data.get('cf_y5', 0)/1000:.1f}K | ${data.get('cumulative_y5', 0)/1000:.1f}K |
    
    ## Channel Analysis
    
    The revenue model is based on the following channel mix:
    
    """
    
    # Add channel breakdown
    channels = data.get('channels', {})
    for channel, values in channels.items():
        markdown_content += f"* **{channel}**: ${values.get('revenue', 0)/1000:.1f}K revenue, {values.get('margin', 0):.1%} margin, {values.get('percent', 0):.1%} of total\n"
    
    # Add key assumptions section
    markdown_content += "\n## Key Assumptions\n\n"
    
    for category, items in assumptions.items():
        markdown_content += f"### {category}\n\n"
        for name, value in items.items():
            # Format value based on type
            if isinstance(value, float):
                if 0 <= value <= 1:  # Likely a percentage
                    formatted_value = f"{value:.1%}"
                else:
                    formatted_value = f"{value:,.2f}"
            else:
                formatted_value = str(value)
                
            markdown_content += f"* **{name}**: {formatted_value}\n"
        
        markdown_content += "\n"
    
    # Add risks section
    markdown_content += "## Risks and Mitigations\n\n"
    
    for risk in risks:
        markdown_content += f"### {risk.get('title', 'Risk')}\n\n"
        markdown_content += f"{risk.get('description', '')}\n\n"
        if 'mitigation' in risk:
            markdown_content += f"**Mitigation**: {risk.get('mitigation', '')}\n\n"
    
    # Convert markdown to HTML
    show_export_progress("Converting markdown to HTML...", 0.5)
    html_content = markdown.markdown(markdown_content, extensions=['tables'])
    
    # Add CSS styling
    css = f"""
    body {{
        font-family: Helvetica, Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }}
    h1, h2, h3 {{
        color: {BRAND_COLORS["primary"]};
    }}
    h1 {{
        border-bottom: 2px solid {BRAND_COLORS["primary"]};
        padding-bottom: 10px;
    }}
    h2 {{
        border-bottom: 1px solid {BRAND_COLORS["muted"]};
        padding-bottom: 5px;
        margin-top: 30px;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
    }}
    th, td {{
        padding: 12px;
        border: 1px solid #ddd;
        text-align: left;
    }}
    th {{
        background-color: {BRAND_COLORS["primary"]};
        color: white;
    }}
    tr:nth-child(even) {{
        background-color: #f9f9f9;
    }}
    strong {{
        color: {BRAND_COLORS["primary"]};
    }}
    """
    
    # Create a temporary HTML file
    show_export_progress("Creating PDF document...", 0.7)
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
        html_file = f.name
        f.write(f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>{css}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """.encode('utf-8'))
    
    # Convert HTML to PDF
    html = HTML(filename=html_file)
    css_string = CSS(string=css)
    
    # Create PDF buffer
    buffer = io.BytesIO()
    html.write_pdf(buffer, stylesheets=[css_string])
    
    # Clean up temporary file
    os.unlink(html_file)
    
    # Get PDF from buffer
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    show_export_progress("Export complete!", 1.0)
    return pdf_bytes

def share_link(
    state: Dict[str, Any],
    expiry_hours: int = 24,
    include_qr: bool = True
) -> Dict[str, Any]:
    """
    Generate a shareable link with the current model state.
    
    Parameters:
    -----------
    state : Dict[str, Any]
        Dictionary containing the current model state
    expiry_hours : int, optional
        Number of hours the link should be valid
    include_qr : bool, optional
        Whether to include a QR code
    
    Returns:
    --------
    Dict[str, Any]
        Dictionary with link, QR code image (if requested), and expiry time
    """
    show_export_progress("Generating shareable link...", 0.3)
    
    # Create a unique ID for the state
    state_id = str(uuid.uuid4())
    
    # Create expiry time
    expiry_time = datetime.now() + timedelta(hours=expiry_hours)
    expiry_str = expiry_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Add metadata to state
    state_with_meta = {
        "data": state,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expiry_str,
        "id": state_id
    }
    
    # Serialize and compress state
    state_json = json.dumps(state_with_meta)
    state_bytes = state_json.encode('utf-8')
    
    # Create a hash of the state for verification
    state_hash = hashlib.sha256(state_bytes).hexdigest()
    
    # Store state in session for retrieval (in a real app, this would go to a database)
    if "shared_states" not in st.session_state:
        st.session_state.shared_states = {}
    
    st.session_state.shared_states[state_id] = {
        "data": state,
        "expires_at": expiry_time,
        "hash": state_hash
    }
    
    # Create shareable link (in a real app, this would be a proper URL)
    # For demo purposes, we'll just create a fake URL with the state ID
    base_url = "https://financial-model.streamlit.app/share"
    share_url = f"{base_url}?id={state_id}&hash={state_hash[:10]}"
    
    result = {
        "url": share_url,
        "expires_at": expiry_str,
    }
    
    # Generate QR code if requested
    if include_qr:
        show_export_progress("Generating QR code...", 0.7)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(share_url)
        qr.make(fit=True)
        
        # Create QR code image with custom styling
        qr_img = qr.make_image(fill_color=BRAND_COLORS["primary"], back_color="white")
        
        # Add logo to QR code (if available)
        try:
            if os.path.exists(LOGO_PATH):
                logo = Image.open(LOGO_PATH)
                logo = logo.resize((qr_img.size[0] // 4, qr_img.size[1] // 4))
                
                # Calculate position to place logo in center
                pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
                
                # Create a white background for the logo
                logo_bg = Image.new("RGBA", logo.size, "white")
                qr_img.paste(logo_bg, pos)
                qr_img.paste(logo, pos)
        except:
            pass  # Skip logo if there's an error
        
        # Convert image to bytes
        img_buffer = io.BytesIO()
        qr_img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        img_bytes = img_buffer.getvalue()
        img_buffer.close()
        
        # Add image to result
        result["qr_code"] = img_bytes
    
    show_export_progress("Share link generated!", 1.0)
    return result

# Example usage
if __name__ == "__main__":
    st.title("Export Functionality Demo")
    
    # Sample data for demonstration
    sample_data = {
        "company_name": "Sample Winery",
        "irr": 0.22,
        "moic": 2.5,
        "payback": 3.2,
        "total_revenue": 12500000,
        "avg_growth": 0.15,
        "avg_margin": 0.65,
        "revenue_y1": 1500000,
        "revenue_y2": 2000000,
        "revenue_y3": 2500000,
        "revenue_y4": 3000000,
        "revenue_y5": 3500000,
        "growth_y2": 0.33,
        "growth_y3": 0.25,
        "growth_y4": 0.20,
        "growth_y5": 0.17,
        "expenses_y1": 1200000,
        "expenses_y2": 1500000,
        "expenses_y3": 1800000,
        "expenses_y4": 2100000,
        "expenses_y5": 2400000,
        "cf_y1": 300000,
        "cf_y2": 500000,
        "cf_y3": 700000,
        "cf_y4": 900000,
        "cf_y5": 1100000,
        "cumulative_y1": 300000,
        "cumulative_y2": 800000,
        "cumulative_y3": 1500000,
        "cumulative_y4": 2400000,
        "cumulative_y5": 3500000,
        "channels": {
            "DTC": {"revenue": 5000000, "margin": 0.75, "percent": 0.4},
            "Wholesale": {"revenue": 6250000, "margin": 0.55, "percent": 0.5},
            "Tasting Room": {"revenue": 1250000, "margin": 0.80, "percent": 0.1}
        },
        "assumptions": {
            "Revenue": {
                "Annual Growth Rate": 0.15,
                "DTC Price": 40,
                "Wholesale Price": 20,
                "Tasting Room Price": 35
            },
            "Costs": {
                "COGS per Bottle": 8,
                "Marketing % of Revenue": 0.12,
                "Overhead": 250000
            }
        }
    }
    
    sample_charts = {
        "revenue": {
            "labels": ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"],
            "series": [[1500000, 2000000, 2500000, 3000000, 3500000]],
            "min": 0,
            "max": 4000000
        },
        "channel_mix": {
            "labels": ["DTC", "Wholesale", "Tasting Room"],
            "values": [40, 50, 10]
        },
        "cash_flow": {
            "labels": ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"],
            "series": [[300000, 500000, 700000, 900000, 1100000]],
            "min": 0,
            "max": 1200000
        }
    }
    
    sample_charts_data = {
        "Revenue": pd.DataFrame({
            "Year": ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"],
            "Revenue": [1500000, 2000000, 2500000, 3000000, 3500000],
            "Growth": [0, 0.33, 0.25, 0.2, 0.17]
        }),
        "Channel Mix": pd.DataFrame({
            "Channel": ["DTC", "Wholesale", "Tasting Room"],
            "Revenue": [5000000, 6250000, 1250000],
            "Margin": [0.75, 0.55, 0.8],
            "Percent": [0.4, 0.5, 0.1]
        })
    }
    
    sample_risks = [
        {
            "title": "Market Competition",
            "description": "Increasing competition in the premium wine segment could pressure prices and margins.",
            "mitigation": "Focus on building brand loyalty and direct customer relationships."
        },
        {
            "title": "Weather and Climate",
            "description": "Unpredictable weather patterns could impact grape yield and quality.",
            "mitigation": "Diversify vineyard locations and maintain inventory buffers."
        }
    ]
    
    # Demo buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Pitch Deck"):
            pdf_bytes = export_pitch_deck(
                "Sample Winery Financial Model",
                sample_data,
                sample_charts,
                sample_data["assumptions"]
            )
            
            show_export_success(
                "Pitch deck exported successfully!",
                file_data=pdf_bytes,
                file_name="Sample_Winery_Pitch_Deck.pdf"
            )
    
    with col2:
        if st.button("Export Excel Summary"):
            excel_bytes = export_excel_summary(
                sample_data,
                sample_charts_data
            )
            
            show_export_success(
                "Excel summary exported successfully!",
                file_data=excel_bytes,
                file_name="Sample_Winery_Financial_Summary.xlsx"
            )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Investment Memo"):
            pdf_bytes = export_investment_memo(
                "Sample Winery Investment Opportunity",
                sample_data,
                sample_charts,
                sample_data["assumptions"],
                sample_risks
            )
            
            show_export_success(
                "Investment memo exported successfully!",
                file_data=pdf_bytes,
                file_name="Sample_Winery_Investment_Memo.pdf"
            )
    
    with col2:
        if st.button("Generate Share Link"):
            result = share_link(
                sample_data,
                expiry_hours=24,
                include_qr=True
            )
            
            show_export_success("Share link generated successfully!")
            
            st.text_input("Share URL", result["url"])
            st.caption(f"Link expires: {result['expires_at']}")
            
            if "qr_code" in result:
                st.image(result["qr_code"], caption="Scan to view on mobile", width=200)
