import io
import qrcode
import hashlib
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER

"""
PDF Certificate Generator for Vehicle Registration
Uses ReportLab to create professional vehicle registration certificates with QR codes
SECURITY: QR code contains all verification data + cryptographic hash
"""

from django.conf import settings
SECRET_SALT = settings.TMO_VERIFICATION_SECRET

def generate_verification_hash(vehicle):
    """
    Generate cryptographic hash for certificate verification
    This prevents forgery as it requires access to the original database
    """
    hash_input = (
        f"{vehicle.id}"
        f"{vehicle.chassis_number}"
        f"{vehicle.engine_number}"
        f"{vehicle.verified_at.isoformat()}"
        f"{vehicle.verified_by.officer_id}"
        "k9mP2xQ7nR4tL8wE"
    )
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]


def generate_qr_code(vehicle):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    verification_hash = generate_verification_hash(vehicle)
    
    # Encode a URL so phone opens browser instead of calling/texting
    base_url = getattr(settings, 'TMO_VERIFY_BASE_URL', 'http://127.0.0.1:8000')
    verification_url = (
        f"{base_url}/users/verify/"
        f"?certificate_number=VRC-{vehicle.id:06d}"
        f"&verification_hash={verification_hash}"
    )
    
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def generate_vehicle_certificate_pdf(vehicle, output_path):
    """
    Generate a professional vehicle registration certificate PDF
    
    Args: Vehicle model instance
    output_path (str): Path where PDF will be saved
    
    Returns:
        str: Path to generated PDF
    """
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Header - Government of Nepal
    gov_header = Paragraph(
        "<b>GOVERNMENT OF NEPAL</b><br/>TRANSPORT MANAGEMENT OFFICE",
        title_style
    )
    elements.append(gov_header)
    elements.append(Spacer(1, 12))
    
    # Certificate Title
    cert_title = Paragraph(
        "<b>VEHICLE REGISTRATION CERTIFICATE</b>",
        ParagraphStyle(
            'CertTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#d32f2f'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
    )
    elements.append(cert_title)
    elements.append(Spacer(1, 6))
    
    # Generate verification hash for display
    verification_hash = generate_verification_hash(vehicle)
    
    # Certificate Number and Date with Hash
    cert_info = Paragraph(
        f"<b>Certificate No:</b> VRC-{vehicle.id:06d} | "
        f"<b>Issue Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>"
        f"<b>Verification Hash:</b> {verification_hash}",
        ParagraphStyle(
            'CertInfo',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#555555')
        )
    )
    elements.append(cert_info)
    elements.append(Spacer(1, 20))
    
    # VEHICLE INFORMATION SECTION
    elements.append(Paragraph("<b>VEHICLE INFORMATION</b>", header_style))
    
    vehicle_data = [
        ['Permanent Plate Number:', vehicle.permanent_plate_number or 'N/A'],
        ['Chassis Number:', vehicle.chassis_number],
        ['Engine Number:', vehicle.engine_number],
        ['Make & Model:', f"{vehicle.make} {vehicle.model}"],
        ['Year of Manufacture:', str(vehicle.year)],
        ['Color:', vehicle.color],
        ['Vehicle Type:', vehicle.get_vehicle_type_display()],
        ['Fuel Type:', vehicle.get_fuel_type_display()],
        ['Engine Capacity:', f"{vehicle.engine_cc} CC"],
        ['Seating Capacity:', str(vehicle.seating_capacity)],
    ]
    
    vehicle_table = Table(vehicle_data, colWidths=[2.5*inch, 4*inch])
    vehicle_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1565c0')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(vehicle_table)
    elements.append(Spacer(1, 15))
    
    # OWNER INFORMATION SECTION
    elements.append(Paragraph("<b>REGISTERED OWNER</b>", header_style))
    
    owner = vehicle.current_owner
    owner_data = [
        ['Full Name:', owner.full_name],
        ['Email:', owner.user.email],
        ['Phone Number:', owner.phone],
        ['Address:', owner.address],
        ['Date of Birth:', owner.dob.strftime('%B %d, %Y')],
    ]
    
    owner_table = Table(owner_data, colWidths=[2.5*inch, 4*inch])
    owner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3e5f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6a1b9a')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(owner_table)
    elements.append(Spacer(1, 15))
    
    # SHOWROOM INFORMATION SECTION
    elements.append(Paragraph("<b>REGISTERED BY</b>", header_style))
    
    showroom = vehicle.showroom
    showroom_data = [
        ['Showroom Name:', showroom.showroom_name],
        ['Registration Number:', showroom.registration_number],
        ['Address:', showroom.address],
        ['Contact:', showroom.phone],
    ]
    
    showroom_table = Table(showroom_data, colWidths=[2.5*inch, 4*inch])
    showroom_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3e0')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#e65100')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(showroom_table)
    elements.append(Spacer(1, 15))
    
    # VERIFICATION INFORMATION SECTION
    elements.append(Paragraph("<b>VERIFICATION DETAILS</b>", header_style))
    
    verification_data = [
        ['Verified By:', f"{vehicle.verified_by.full_name} (Officer ID: {vehicle.verified_by.officer_id})"],
        ['Verification Date:', vehicle.verified_at.strftime('%B %d, %Y at %I:%M %p')],
        ['Status:', 'VERIFIED ✓'],
        ['Remarks:', vehicle.verification_remarks or 'No remarks'],
    ]
    
    verification_table = Table(verification_data, colWidths=[2.5*inch, 4*inch])
    verification_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f5e9')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2e7d32')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(verification_table)
    elements.append(Spacer(1, 20))
    
    # QR CODE SECTION
    # Generate QR code with all verification data
    qr_buffer = generate_qr_code(vehicle)
    
    # Create QR code image
    qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
    
    # QR Code table with enhanced instructions
    qr_table = Table(
        [[qr_image, Paragraph(
            "<b>Scan QR Code to Verify Certificate</b><br/><br/>"
            "Scan with your phone camera to instantly verify this certificate online.<br/><br/>"
            "<b>Manual verification:</b><br/>"
            f"Certificate: <b>VRC-{vehicle.id:06d}</b><br/>"
            f"Hash: <b>{verification_hash}</b>",
            ParagraphStyle(
                'QRText',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#555555')
            )
        )]],
        colWidths=[2.2*inch, 4.3*inch]
    )
    qr_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fafafa')),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(qr_table)
    elements.append(Spacer(1, 20))
    
    # AUTHORIZATION SECTION
    elements.append(Paragraph("<b>OFFICIAL AUTHORIZATION</b>", header_style))
    
    # Authorization info
    auth_table_data = [
        ['Authorized by:', vehicle.verified_by.full_name],
        ['Officer ID:', vehicle.verified_by.officer_id],
        ['Department:', vehicle.verified_by.department],
        ['Date:', vehicle.verified_at.strftime('%B %d, %Y')],
    ]
    
    auth_table = Table(auth_table_data, colWidths=[2*inch, 4.5*inch])
    auth_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(auth_table)
    elements.append(Spacer(1, 15))
    
    # Officer signature
    if hasattr(vehicle.verified_by, 'signature_image') and vehicle.verified_by.signature_image:
        sig_table = Table(
            [[
                Paragraph("<b>Officer Signature:</b>", styles['Normal']),
                Image(vehicle.verified_by.signature_image.path, width=1.5*inch, height=0.6*inch)
            ]],
            colWidths=[2*inch, 2.5*inch]
        )
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(sig_table)
    else:
        # Show placeholder line if no signature uploaded
        elements.append(Paragraph(
            "<b>Officer Signature:</b> ________________________________",
            styles['Normal']
        ))
    
    # FOOTER
    footer = Paragraph(
        "<i>This is an official document issued by the Transport Management Office, Government of Nepal. "
        f"Any tampering or forgery of this certificate is a punishable offense under the law. "
        f"Verification Hash: {verification_hash}</i>",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#888888'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
    )
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    return output_path
