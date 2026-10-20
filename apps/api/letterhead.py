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
    "keterangan_legal": "SK Men Kum No: AHU-0001606.AH.01.05 Tahun 2023",
    "alamat": "Kavling Lama RT 03, RW 10 Kel. Sagulung Kota, Kec. Sagulung, Kota Batam, Kepulauan Riau 29439",
    "telepon": "(0778) 4091272",
    "whatsapp": "",
    "email": "kabid.asysyuuraa@gmail.com",
    "website": "https://asy-syuuraabatam.or.id",
    "logo_url": "",
    "logo_size": 75,
    "font_family": "times",  # 'times' or 'arial'/'helvetica'
    "line_color": "#059669",
    "layout_style": "left_logo",  # 'left_logo' or 'centered'
    "custom_lines": []
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
    Supports:
    - Custom lines (dynamic line-by-line configuration)
    - Font Family (Times New Roman or Arial/Helvetica)
    - Scalable Logo Size (default 75pt)
    - Clean contact strings without dummy numbers
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

    # Font Family selection
    font_choice = (config.get("font_family") or "times").lower()
    if "time" in font_choice:
        font_bold = "Times-Bold"
        font_regular = "Times-Roman"
        font_italic = "Times-Italic"
    else:
        font_bold = "Helvetica-Bold"
        font_regular = "Helvetica"
        font_italic = "Helvetica-Oblique"

    flowables = []
    kop_paragraphs = []

    # Check if custom_lines are configured
    custom_lines = config.get("custom_lines") or []
    if isinstance(custom_lines, list) and len(custom_lines) > 0:
        for idx, line in enumerate(custom_lines):
            txt = (line.get("text") or "").strip()
            if not txt:
                continue

            # Override sub title if specific unit requested and this is line 2
            if idx == 1 and custom_sub_title:
                txt = custom_sub_title.strip().upper()

            f_size = float(line.get("font_size", 10))
            is_bold = bool(line.get("bold", False))
            is_italic = bool(line.get("italic", False))
            
            c_hex = line.get("color")
            if not c_hex:
                c_hex = color_hex if idx == 1 else "#0F172A"
            try:
                line_color = colors.HexColor(c_hex)
            except Exception:
                line_color = colors.HexColor("#0F172A")

            if is_bold and is_italic:
                chosen_font = font_bold  # fallback
            elif is_bold:
                chosen_font = font_bold
            elif is_italic:
                chosen_font = font_italic
            else:
                chosen_font = font_regular

            align_val = 1 if line.get("align", "center") == "center" else (0 if line.get("align") == "left" else 2)

            p_style = ParagraphStyle(
                f'KopCustomLine_{idx}',
                parent=styles['Normal'],
                fontName=chosen_font,
                fontSize=f_size,
                leading=f_size * 1.25,
                alignment=align_val,
                textColor=line_color,
                spaceAfter=2
            )
            kop_paragraphs.append(Paragraph(txt, p_style))
    else:
        # Standard format
        title_style = ParagraphStyle(
            'KopTitle',
            parent=styles['Normal'],
            fontName=font_bold,
            fontSize=13,
            leading=16,
            alignment=1,
            textColor=colors.HexColor('#0F172A')
        )
        sub_title_style = ParagraphStyle(
            'KopSubTitle',
            parent=styles['Normal'],
            fontName=font_bold,
            fontSize=11.5,
            leading=15,
            alignment=1,
            textColor=primary_color
        )
        legal_style = ParagraphStyle(
            'KopLegal',
            parent=styles['Normal'],
            fontName=font_italic,
            fontSize=8,
            leading=11,
            alignment=1,
            textColor=colors.HexColor('#475569')
        )
        contact_style = ParagraphStyle(
            'KopContact',
            parent=styles['Normal'],
            fontName=font_regular,
            fontSize=8,
            leading=11,
            alignment=1,
            textColor=colors.HexColor('#475569')
        )

        nama_yayasan = (config.get("nama_yayasan") or DEFAULT_LETTERHEAD["nama_yayasan"]).strip().upper()
        if custom_sub_title:
            nama_unit = custom_sub_title.strip().upper()
        else:
            nama_unit = (config.get("nama_unit") or DEFAULT_LETTERHEAD["nama_unit"]).strip().upper()

        keterangan_legal = (config.get("keterangan_legal") or "").strip()
        alamat = (config.get("alamat") or DEFAULT_LETTERHEAD["alamat"]).strip()

        # Build contact string without fake/dummy numbers
        contacts = []
        if config.get("telepon") and config["telepon"].strip():
            contacts.append(f"Telp: {config['telepon'].strip()}")
        if config.get("whatsapp") and config["whatsapp"].strip() and config["whatsapp"].strip() != "0812-7000-0000":
            contacts.append(f"WA: {config['whatsapp'].strip()}")
        if config.get("email") and config["email"].strip():
            contacts.append(f"Email: {config['email'].strip()}")
        if config.get("website") and config["website"].strip():
            contacts.append(f"Web: {config['website'].strip()}")

        contact_str = " • ".join(contacts)

        kop_paragraphs.append(Paragraph(nama_yayasan, title_style))
        kop_paragraphs.append(Paragraph(nama_unit, sub_title_style))
        if keterangan_legal:
            kop_paragraphs.append(Paragraph(keterangan_legal, legal_style))
        if alamat:
            kop_paragraphs.append(Paragraph(alamat, contact_style))
        if contact_str:
            kop_paragraphs.append(Paragraph(contact_str, contact_style))

    # Resolve logo image & size
    logo_flowable = None
    logo_url = config.get("logo_url") or ""
    try:
        logo_size = float(config.get("logo_size", 75))
        if logo_size < 40 or logo_size > 140:
            logo_size = 75
    except Exception:
        logo_size = 75

    if logo_url:
        try:
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
                logo_flowable = RLImage(local_candidate, width=logo_size, height=logo_size)
            elif logo_url.startswith("http://") or logo_url.startswith("https://"):
                import urllib.request
                import io
                req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    img_data = io.BytesIO(resp.read())
                    logo_flowable = RLImage(img_data, width=logo_size, height=logo_size)
        except Exception as e:
            logger.warning(f"Could not load letterhead logo from {logo_url}: {e}")
            logo_flowable = None

    # Render layout: With Logo or Text Only
    if logo_flowable:
        logo_col_w = logo_size + 14
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
        for p in kop_paragraphs:
            flowables.append(p)

    flowables.append(Spacer(1, 4))
    # Double line typical of formal Indonesian institutional letterheads
    flowables.append(HRFlowable(width="100%", thickness=2.2, color=primary_color, spaceBefore=2, spaceAfter=1.5))
    flowables.append(HRFlowable(width="100%", thickness=0.7, color=primary_color, spaceBefore=0, spaceAfter=10))

    return flowables

