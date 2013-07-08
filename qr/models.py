from django.db import models
from validators import *

# All sizes should be in mm

FONTS         = [
        'Courier',              'Courier-Bold',         'Courier-BoldOblique',
        'Courier-Oblique',      'Helvetica',            'Helvetica-Bold',
        'Helvetica-BoldOblique','Helvetica-Oblique',    'Symbol',
        'Times-Bold',           'Times-BoldItalic',     'Times-Italic',
        'Times-Roman',          'ZapfDingbats'
]
FONT_SIZES    = range(4,32)
#LABEL_CHOICES = ['QR', 'QR+tag', 'cultivar+species+QR', 'cultivar+species+QR+tag']

class CoordField(models.CharField):
    description = "CharField that stores a positive coordinate pair, e.g. (0,0)"
    max_length  = 11
    default_validators = [coordvalidator]
    def formfield(self, **kwargs):
        defaults = {
            'error_messages': {
                'invalid': (u'Enter only one positive coordinate pair, such as "(0,0)".'),
            }
        }
        defaults.update(kwargs)
        return super(models.CharField, self).formfield(**defaults)

class FontField(models.CharField):
    description = "CharField that only stores valid PDF font names"
    max_length  = 21
    choices     = zip(FONTS, FONTS)

class FontSizeField(models.PositiveIntegerField):
    description = "PositiveIntegerField that stores a valid font size"
    choices     = zip(FONT_SIZES, FONT_SIZES)
