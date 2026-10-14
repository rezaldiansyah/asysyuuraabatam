import os
import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
import models

logger = logging.getLogger(__name__)

DEFAULT_LETTERHEAD = {
    "nama_yayasan": "YAYASAN ASY-SYUURAA BATAM",
    "nama_unit": "SEKOLAH ISLAM TERPADU ASY-SYUURAA",
    "keterangan_legal": "NPSN: - • Akreditasi A • Berdiri Sejak 2005",
    "alamat": "Komplek Asy-Syuuraa, Sungai Langkai, Kec. Sagulung, Kota Batam, Kepulauan Riau 29437",
    "telepon": "(0778) 391234",
    "whatsapp": "0812-7000-0000",
    "email": "sekretariat@asy-syuuraabatam.or.id",
    "website": "https://asy-syuuraabatam.or.id",
    "logo_url": "",
    "line_color": "#059669",
    "layout_style": "left_logo",  # 'left_logo' or 'centered'
}


def get_letterhead_config(db: Session, unit_id: Optional[int] = None) -> Dict[str, Any]:
    """Retrieve centralized letterhead configuration from PageContent."""
    config = dict(DEFAULT_LETTERHEAD)
    try:
        content_row = db.query(models.PageContent).filter(
            models.PageContent.section_key == "settings_letterhead"
        ).first()

        if content_row:
            if content_row.content_json:
                try:
                    data = json.loads(content_row.content_json)
                    if isinstance(data, dict):
                        config.update(data)
                except Exception as e:
                    logger.warning(f"Failed to parse letterhead content_json: {e}")

            if content_row.image_url and not config.get("logo_url"):
                config["logo_url"] = content_row.image_url

        # Unit-specific override if available
        if unit_id:
            unit_row = db.query(models.PageContent).filter(
                models.PageContent.section_key == f"settings_letterhead_unit_{unit_id}"
            ).first()
            if unit_row and unit_row.content_json:
                try:
                    u_data = json.loads(unit_row.content_json)
                    if isinstance(u_data, dict):
                        config.update(u_data)
                except Exception:
                    pass
    except Exception as e:
        logger.error(f"Error fetching letterhead settings: {e}")

    return config


def get_letterhead_flowables(
    db: Session,
    unit_id: Optional[int] = None,
    scope: Optional[str] = None,
    custom_sub_title: Optional[str] = None,
    printable_width: float = 515.0
) -> List[Any]:
    """
    Generate unified ReportLab Flowables for standard institutional Kop Surat.
    Accepts printable width (default 515pt for A4 with 40pt margins).
    """
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    config = get_letterhead_config(db, unit_id=unit_id)
    styles = getSampleStyleSheet()

    color_hex = config.get("line_color", "#059669")
    try:
        primary_color = colors.HexColor(color_hex)
    except Exception:
        primary_color = colors.HexColor("#059669")

    # Typography Styles
    title_style = ParagraphStyle(
        'KopTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15,
        alignment=1,  # Center
        textColor=colors.HexColor('#0F172A')
    )
    sub_title_style = ParagraphStyle(
        'KopSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        alignment=1,  # Center
        textColor=primary_color
    )
    legal_style = ParagraphStyle(
        'KopLegal',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        alignment=1,
        textColor=colors.HexColor('#475569')
    )
    contact_style = ParagraphStyle(
        'KopContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        alignment=1,
        textColor=colors.HexColor('#475569')
    )

    flowables = []

    # Texts
    nama_yayasan = (config.get("nama_yayasan") or DEFAULT_LETTERHEAD["nama_yayasan"]).strip().upper()
    
    # Sub title: custom or unit or configured
    if custom_sub_title:
        nama_unit = custom_sub_title.strip().upper()
    else:
        nama_unit = (config.get("nama_unit") or DEFAULT_LETTERHEAD["nama_unit"]).strip().upper()

    keterangan_legal = (config.get("keterangan_legal") or "").strip()
    alamat = (config.get("alamat") or DEFAULT_LETTERHEAD["alamat"]).strip()

    # Build contact string
    contacts = []
    if config.get("telepon"):
        contacts.append(f"Telp: {config['telepon']}")
    if config.get("whatsapp"):
        contacts.append(f"WA: {config['whatsapp']}")
    if config.get("email"):
        contacts.append(f"Email: {config['email']}")
    if config.get("website"):
        contacts.append(f"Web: {config['website']}")

    contact_str = " • ".join(contacts)

    # Paragraph elements for text column
    kop_paragraphs = [
        Paragraph(nama_yayasan, title_style),
        Paragraph(nama_unit, sub_title_style),
    ]
    if keterangan_legal:
        kop_paragraphs.append(Paragraph(keterangan_legal, legal_style))
    kop_paragraphs.append(Paragraph(alamat, contact_style))
    if contact_str:
        kop_paragraphs.append(Paragraph(contact_str, contact_style))

    # Try resolving logo image
    logo_flowable = None
    logo_url = config.get("logo_url") or ""

    if logo_url:
        try:
            # Case 1: Local file path in uploads
            from main import UPLOAD_DIR
            local_candidate = None

            if "/uploads/" in logo_url:
                fname = logo_url.split("/uploads/")[-1]
                p = os.path.join(UPLOAD_DIR, fname)
                if os.path.exists(p):
                    local_candidate = p
            elif os.path.exists(logo_url):
                local_candidate = logo_url

            if local_candidate and os.path.exists(local_candidate):
                logo_flowable = RLImage(local_candidate, width=54, height=54)
            elif logo_url.startswith("http://") or logo_url.startswith("https://"):
                # Attempt fast load with timeout
                import urllib.request
                import io
                req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=2.5) as resp:
                    img_data = io.BytesIO(resp.read())
                    logo_flowable = RLImage(img_data, width=54, height=54)
        except Exception as e:
            logger.warning(f"Could not load letterhead logo from {logo_url}: {e}")
            logo_flowable = None

    # Render layout: With Logo or Text Only
    if logo_flowable:
        logo_col_w = 60
        text_col_w = printable_width - logo_col_w
        kop_table = Table([[logo_flowable, kop_paragraphs]], colWidths=[logo_col_w, text_col_w])
        kop_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        flowables.append(kop_table)
    else:
        # Text only centered
        for p in kop_paragraphs:
            flowables.append(p)

    flowables.append(Spacer(1, 4))
    # Double line typical of formal Indonesian institutional letterheads
    flowables.append(HRFlowable(width="100%", thickness=2.0, color=primary_color, spaceBefore=2, spaceAfter=1.5))
    flowables.append(HRFlowable(width="100%", thickness=0.6, color=primary_color, spaceBefore=0, spaceAfter=10))

    return flowables
