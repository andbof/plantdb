from Crypto.Random.random import randint
from django.core.exceptions import ObjectDoesNotExist
from tempfilelock import TempfileLock
from models import Tag

tagchar_to_num = {
    '0': 0,  '1': 1,  '2': 2,  '3': 3,  '4': 4,  '5': 5,  '6': 6,  '7': 7,  '8': 8,
    '9': 9,  'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15, 'g': 16, 'h': 17,
    'i': 18, 'j': 19, 'k': 20, 'l': 21, 'm': 22, 'n': 23, 'o': 24, 'p': 25, 'q': 26,
    'r': 27, 's': 28, 't': 29, 'u': 30, 'v': 31, 'w': 32, 'x': 33, 'y': 34, 'z': 35,
}

tagnum_to_char = {
     0: '0',  1: '1',  2: '2',  3: '3',  4: '4',  5: '5',  6: '6',  7: '7',  8: '8',
     9: '9', 10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f', 16: 'g', 17: 'h',
    18: 'i', 19: 'j', 20: 'k', 21: 'l', 22: 'm', 23: 'n', 24: 'o', 25: 'p', 26: 'q',
    27: 'r', 28: 's', 29: 't', 30: 'u', 31: 'v', 32: 'w', 33: 'x', 34: 'y', 35: 'z',
}

min_tagnum = 0
max_tagnum = 2176782335     # 2**36 - 1; len(tagchar_to_num) == len(tagnum_to_char) == 36

assert(len(tagchar_to_num) == 36)
assert(len(tagnum_to_char) == 36)
assert(max_tagnum == len(tagchar_to_num)**6 - 1)

# Used for locking create_tag() as the server might be forking
taglock = TempfileLock()

def generate_unique_tagnum():
    # Must be run within taglock.lock() and taglock.unlock()
    if Tag.objects.count() >= max_tagnum:
        raise RuntimeError(u'Maximum number of tags (%u) exceeded' % max_tagnum)
    while True:
        tagnum = randint(min_tagnum, max_tagnum)
        try:
            Tag.objects.get(tagnum=tagnum)
        except ObjectDoesNotExist:
            break
    return tagnum

def create_tag(tagnum=None):
    taglock.lock()
    if tagnum is None:
        tagnum = generate_unique_tagnum()
    t = Tag(
        tagnum = tagnum,
        tag    = tagnum_to_tag(tagnum),
    )
    t.save()
    taglock.unlock()
    return t

def create_tag_if_not_found(tagnum):
    taglock.lock()
    try:
        Tag.objects.get(tagnum=tagnum)
    except ObjectDoesNotExist:
        t = Tag(
                tagnum = tagnum,
                tag    = tagnum_to_tag(tagnum),
        )
        t.save()
    taglock.unlock()

def tag_to_tagnum(tag):
    if (len(tag) != 6) or (not tag.isalnum()):
        raise ValueError(u'tag %s is not a valid tag' % tag)
    tag = tag.lower()
    tagnum = 0
    for n in reversed(range(len(tag))):
        c = tag[n]
        tagnum += tagchar_to_num[c] * 36**(5 - n)
    return tagnum

def tagnum_to_tag(tagnum):
    if (tagnum < min_tagnum) or (tagnum > max_tagnum):
        raise ValueError(u'tagnum %u out of range of %u..%u' % (tagnum, min_tagnum, max_tagnum))
    tagl = []
    for n in reversed(range(6)):
        tagl.insert(0, tagnum_to_char[tagnum % 36])
        tagnum /= 36
    return u''.join( map(lambda x: str(x), tagl) )

def associate_tag(tag, target):
    tag.target = target
