from PyQRNative import *
from PIL.Image import BILINEAR, BICUBIC, ANTIALIAS, NEAREST
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait, A4
from reportlab.lib.units import cm, mm
from StringIO import StringIO
from plant.tag import create_tag
import time
from datetime import datetime

QR_TYPE      = 4
QR_ECC       = QRErrorCorrectLevel.H
TAG_FONT     = 'Courier-Bold'
TAG_FONT_PT  = 8
FOOT_FONT    = 'Helvetica'
FOOT_FONT_PT = 8
TOP_YMARGIN  = 0.75*cm

LAYOUTS      = {
        'Long sticks':
            {'qr_size': 2*cm, 'qr_lxmargin': 1*cm,    'qr_rxmargin': 1*cm,    'qr_ymargin': 5.0*cm, 'created': True,  'paired': False},
        'Sticky labels 70x37mm':
            {'qr_size': 2.5*cm, 'qr_lxmargin': 0.50*cm, 'qr_rxmargin': 0.50*cm, 'qr_ymargin': 1.2*cm, 'created': False, 'paired': False},
        'Sticky labels 70x37mm (paired)':
            {'qr_size': 2.5*cm, 'qr_lxmargin': 0.50*cm, 'qr_rxmargin': 0.50*cm, 'qr_ymargin': 1.2*cm, 'created': False, 'paired': True},
#        'Verbose labels ?x?mm':
#            {'qr_size': 0,    'qr_lxmargin': 0,       'qr_ymargin': 0},
}
LAYOUT_LIST  = LAYOUTS.keys()
DUPLEX_LIST  = ['No', 'Short side']

# Typ tre cm verkar vara en rimlig storlek, bade med tanke
# pa vad som far plats i verkligheten och analyserna gjorda pa
# http://www.qrstuff.com/blog/2011/01/18/what-size-should-a-qr-code-be
# Lamplig fontstorlek for taggarna verkar vara 8pt Helvetica

def validate_params(layout, duplex):
    if (layout is None) or (layout not in LAYOUT_LIST):
        return False
    if (duplex is None) or (duplex not in DUPLEX_LIST):
        return False
    if (layout == 'Verbose labels ?x?mm'):
        raise NotImplementedError
    return True

def generate_new_qrimage():
    tag = create_tag()
    qr = QRCode(QR_TYPE, QR_ECC)
    qr.addData('https://YOUR_DOMAIN/' + str(tag.tag))
    qr.make()
    return (qr.makeImage(), tag.tag)

def generate_qr_from_layout(layout, duplex, pagesize=A4):
    if duplex == 'Long side':
        raise NotImplementedError('only short page duplex implemented')

    now = datetime.now()
    qr_size     = LAYOUTS[layout]['qr_size']
    qr_lxmargin = LAYOUTS[layout]['qr_lxmargin']
    qr_rxmargin = LAYOUTS[layout]['qr_rxmargin']
    qr_ymargin  = LAYOUTS[layout]['qr_ymargin']
    created     = LAYOUTS[layout]['created']
    paired      = LAYOUTS[layout]['paired']
    x = pagesize[0] - (qr_size + qr_lxmargin)
    y = pagesize[1] - (qr_size + TOP_YMARGIN)

    # Validate parameters; this is mostly for debugging
    if (qr_size < 1) or (qr_lxmargin < 1) or (qr_rxmargin < 1) or (qr_ymargin < 1):
        raise ValueError(u'Internal error: One of qr size, qr x margin or qr y margin is zero.')

    # Generate QR codes with positions
    qrimgs = []
    while y >= 0:
        xnum = 0;
        while x > 0:
            xnum += 1
            if (not paired) or (xnum % 2 != 0):
                (qrimg, tag) = generate_new_qrimage()
            qrimgs.append({'image': qrimg, 'tag': tag, 'x': x, 'y': y})
            x -= (qr_size + qr_rxmargin + qr_lxmargin)
        x  = pagesize[0] - (qr_size + qr_lxmargin)
        y -= (qr_size + qr_ymargin)

    f = StringIO();
    pdf = canvas.Canvas(f, pagesize=portrait(pagesize), pageCompression=0)
    # Plot QR codes on first side
    pdf.setFont(TAG_FONT, TAG_FONT_PT)
    for qrimg in qrimgs:
        x = qrimg['x']
        y = qrimg['y']
        # drawImage() seems to crash on PIL objects so we use drawInlineImage() instead, even though it's deprecated.
        # PyQRNative draws a white margin around the QR code, making it about one eigth smaller than the required size.
        pdf.drawInlineImage(qrimg['image'], x, y+(qr_size*0.0625), width=qr_size, height=qr_size, preserveAspectRatio=True)
        pdf.drawCentredString(x + (qr_size/2), y + 0.05*cm, qrimg['tag'])
    if created:
        pdf.setFont(FOOT_FONT, FOOT_FONT_PT)
        pdf.drawString(cm, cm, 'Created on %s' % str(now))
    pdf.showPage()

    if duplex != 'No':
        pdf.setFont(TAG_FONT, TAG_FONT_PT)
        pdf.setPageRotation(180)
        for qrimg in qrimgs:
            x = portrait(pagesize)[0] - qrimg['x'] - qr_size
            y = qrimg['y']
            pdf.drawInlineImage(qrimg['image'], x, y+(qr_size*0.0625), width=qr_size, height=qr_size, preserveAspectRatio=True)
            pdf.drawCentredString(x + (qr_size/2), y + 0.05*cm, qrimg['tag'])
        if created:
            pdf.setFont(FOOT_FONT, FOOT_FONT_PT)
            pdf.drawRightString(portrait(pagesize)[0] - cm, cm, 'Created on %s' % str(now))
        pdf.showPage()

    pdf.save()
    return f

