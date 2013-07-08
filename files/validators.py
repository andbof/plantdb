import re

def sha1validator(sha1str):
    if len(sha1str) != 40:
        raise ValidationError(u'%s is not exactly 40 bytes long: not a valid SHA1 hex sum' % sha1str)
    if not re.match('^[0-9a-f]+$', sha1str, flags=re.IGNORECASE):
        raise ValidationError(u'%s contains non-hex characters' % sha1str)
    return True
