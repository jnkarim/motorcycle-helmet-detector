"""
📄 PROFESSIONAL FINE/CASE PDF GENERATOR
Generates official traffic violation documents
Based on Bangladesh Traffic Authority format
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import os

class TrafficFinePDF:
    """Generate professional traffic fine PDF"""
    
    def __init__(self, output_folder="fines"):
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        
    def generate_fine(self, violation_data):
        """
        Generate a professional traffic fine PDF
        
        Parameters:
        violation_data = {
            'trace_no': '019123',
            'case_id': '1007429286',
            'accused_person': 'Mihaj',
            'father_spouse': 'soleman',
            'cell_number': '01858051852',
            'address': 'Mohammadpur',
            'vehicle_reg_no': 'Dhaka Metro LA 45-6093',
            'offence': 'Driving Without Helmet',
            'section': '122',
            'seized_docs': 'T/T',
            'occurrence_date': '2025-06-29 12:00',
            'payment_last_date': '2025-07-20',
            'witness': 'ali rab',
            'fine_amount': '1,000.00',
            'officer_id': '9623252925',
            'officer_name': 'Traffic Officer',
            'division': 'Tejgaon',
            'location': 'AURANGAZEB ROAD, BLOCK#A, MOHAMMADPUR',
            'plate_image_path': 'violations/plate_xxx.jpg'
        }
        """
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"FINE_{violation_data.get('case_id', 'UNKNOWN')}_{timestamp}.pdf"
        filepath = os.path.join(self.output_folder, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Container for elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#DC143C'),
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=6
        )
        
        label_style = ParagraphStyle(
            'Label',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Bold'
        )
        
        value_style = ParagraphStyle(
            'Value',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000')
        )
        
        # === HEADER ===
        elements.append(Paragraph("DHAKA METROPOLITAN POLICE POST", title_style))
        elements.append(Paragraph(
            f"Officer ID Number: {violation_data.get('officer_id', 'N/A')}", 
            header_style
        ))
        elements.append(Paragraph(
            f"Div: {violation_data.get('division', 'N/A')} - TRAFFIC", 
            header_style
        ))
        elements.append(Paragraph(
            violation_data.get('location', ''), 
            header_style
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        elements.append(Paragraph("The Road Transport ACT 2018", header_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Separator line
        elements.append(Paragraph("_" * 80, header_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # === CASE DETAILS TABLE ===
        case_data = [
            ["Trace No.:", violation_data.get('trace_no', 'N/A')],
            ["Case ID:", violation_data.get('case_id', 'N/A')],
            ["Accused Person:", violation_data.get('accused_person', 'N/A')],
            ["Father/Spouse:", violation_data.get('father_spouse', 'N/A')],
            ["Cell Number:", violation_data.get('cell_number', 'N/A')],
            ["Address of Owner/Driver:", violation_data.get('address', 'N/A')],
        ]
        
        case_table = Table(case_data, colWidths=[2*inch, 4*inch])
        case_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(case_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # === VEHICLE & OFFENCE ===
        vehicle_data = [
            ["Vehicle Reg. No.:", violation_data.get('vehicle_reg_no', 'N/A')],
            ["Offence/Offences:", violation_data.get('offence', 'N/A')],
            ["Section:", f"Section {violation_data.get('section', 'N/A')}"],
            ["Seized Docs:", violation_data.get('seized_docs', 'N/A')],
        ]
        
        vehicle_table = Table(vehicle_data, colWidths=[2*inch, 4*inch])
        vehicle_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(vehicle_table)
        elements.append(Spacer(1, 0.15*inch))
        
        # === DATE & WITNESS ===
        date_data = [
            ["Occurrence Date & Time:", violation_data.get('occurrence_date', 'N/A')],
            ["Last Date of Payment:", violation_data.get('payment_last_date', 'N/A')],
            ["Witness:", violation_data.get('witness', 'N/A')],
        ]
        
        date_table = Table(date_data, colWidths=[2*inch, 4*inch])
        date_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(date_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # === FINE AMOUNT (HIGHLIGHTED) ===
        fine_data = [
            ["Total Fine Amount TK:", violation_data.get('fine_amount', '1,000.00')]
        ]
        
        fine_table = Table(fine_data, colWidths=[2*inch, 4*inch])
        fine_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#DC143C')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#DC143C')),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(fine_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # === PLATE IMAGE (if available) ===
        if violation_data.get('plate_image_path') and os.path.exists(violation_data['plate_image_path']):
            try:
                elements.append(Paragraph("Vehicle License Plate:", label_style))
                elements.append(Spacer(1, 0.1*inch))
                
                plate_img = Image(violation_data['plate_image_path'], width=4*inch, height=1.5*inch)
                elements.append(plate_img)
                elements.append(Spacer(1, 0.2*inch))
            except:
                pass
        
        # === SIGNATURE SECTION ===
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph("_" * 80, header_style))
        elements.append(Spacer(1, 0.1*inch))
        
        sig_data = [
            ["", ""],
            ["Signature of the Recording", ""],
            ["Officer / Complainant", ""]
        ]
        
        sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
        sig_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(sig_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # === FOOTER ===
        footer_text = """
        <para alignment="center" fontSize="7" textColor="#666666">
        PLEASE MAKE A PHOTOCOPY OF THE RECEIPT<br/>
        AN PRINT MAY DISAPPEAR AFTER A WEEK<br/>
        <br/>
        Generated by Traffic AI System<br/>
        Date: {date}
        </para>
        """.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        elements.append(Paragraph(footer_text, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        
        return filepath

# Usage example
def generate_sample_fine():
    """Generate a sample fine for testing"""
    pdf_gen = TrafficFinePDF()
    
    sample_data = {
        'trace_no': '019123',
        'case_id': '1007429286',
        'accused_person': 'Mihaj',
        'father_spouse': 'soleman',
        'cell_number': '01858051852',
        'address': 'Mohammadpur',
        'vehicle_reg_no': 'Dhaka Metro LA 45-6093',
        'offence': 'Driving Without Helmet',
        'section': '122',
        'seized_docs': 'T/T',
        'occurrence_date': '2025-06-29 12:00',
        'payment_last_date': '2025-07-20',
        'witness': 'ali rab',
        'fine_amount': '1,000.00',
        'officer_id': '9623252925',
        'officer_name': 'Traffic Officer',
        'division': 'Tejgaon',
        'location': 'AURANGAZEB ROAD, BLOCK#A, MOHAMMADPUR'
    }
    
    filepath = pdf_gen.generate_fine(sample_data)
    print(f"✅ Fine generated: {filepath}")
    return filepath