import re

def barcodevalidator(barcode):
    if len(barcode) > 13:       # 13 is the length of the longest EAN barcode, which is longer than UPC
        raise ValidationError(u'%s is too long to be a barcode (13 characters max)' % barcode)
    if not barcode.isdigit():
        raise ValidationError(u'%s contains non-numeric characters' % barcode)
    # FIXME: Check digits, other things
    # https://en.wikipedia.org/wiki/Universal_Product_Code
