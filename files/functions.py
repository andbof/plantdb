from django.core.exceptions import ObjectDoesNotExist
from files.models import *
from hashlib import sha1
from os import path, remove
from fcntl import flock, LOCK_EX
from plantdb import settings
from StringIO import StringIO
import PIL.Image

class FileType:
    GENERAL = 1
    IMAGE  = 2

THUMBNAIL_SIZE    = (64, 64)
THUMBNAIL_QUALITY = 90

def hash_file(f):
    fsha = sha1()
    f.seek(0, 0)
    for chunk in iter(lambda: f.read(1024), ''):
        fsha.update(chunk)
    return fsha.hexdigest()

def make_thumbnail(filepath, name=None):
    with open(filepath, 'rb') as f:
        flock(f, LOCK_EX)
        imthumb = PIL.Image.open(f)
        imthumb.thumbnail((THUMBNAIL_SIZE), PIL.Image.ANTIALIAS)
        tf = StringIO()
        imthumb.save(tf, 'JPEG', quality=THUMBNAIL_QUALITY)
        tf.flush()
        digest = hash_file(tf)
        thumbpath = path.join(settings.MEDIA_ROOT, digest)
        tf.seek(0, 0)
        with open(thumbpath, 'wb+') as f:
            for chunk in iter(lambda: tf.read(1024), ''):
                f.write(chunk)
            size = f.tell()

    if name is None:
        name = 'thumbnail.jpeg'
    else:
        name = path.splitext(path.basename(name))[0] + '-thumbnail.jpeg'

    thumbnail = Image(
            name    = name,
            sha1sum = digest,
            size    = size,
            mime    = 'image/jpeg',
    )
    thumbnail.save()
    return thumbnail

def handle_uploaded_file(inf, filetype):
    if filetype not in [FileType.GENERAL, FileType.IMAGE]:
        raise ValueError
    sha = sha1()
    for chunk in inf.chunks():
        sha.update(chunk)
    digest   = sha.hexdigest()

    filepath = path.join(settings.MEDIA_ROOT, digest)

    rewrite = False
    byteswritten = 0
    if path.exists(filepath):
        with open(filepath, 'rb') as f:
            flock(f, LOCK_EX)
            if not digest == hash_file(f):
                rewrite = True
            f.seek(0, 2)
            byteswritten = f.tell()

    if (not path.exists(filepath)) or (rewrite):
        with open(filepath, 'wb+') as f:
            flock(f, LOCK_EX)
            for chunk in inf.chunks():
                f.write(chunk)
            byteswritten = f.tell()
            f.close()

    # I don't know if we can trust the supplied size; lets double check it.
    if byteswritten != inf.size:
        try:
            os.remove(filepath)
        finally:
            raise ValueError(u'Supplied size (%u bytes) differs from size of file when written to disk (%u bytes)' % (inf.size, byteswritten))

    # A file might be uploaded twice with different filenames. We won't create a second File()
    # or Image() objects pointing to the same file on disk as we won't know which of the two
    # objects we should return in download() (and their file names might differ).
    if filetype == FileType.GENERAL:
        try:
            newfile = File.objects.get(sha1sum=digest)
        except ObjectDoesNotExist:
            newfile = File(
                    name    = inf.name,
                    sha1sum = digest,
                    size    = inf.size,
                    mime    = inf.content_type,
            )
            newfile.save()
    else:
        try:
            newfile = Image.objects.get(sha1sum=digest)
        except ObjectDoesNotExist:
            newfile = Image(
                    name      = inf.name,
                    sha1sum   = digest,
                    size      = inf.size,
                    mime      = inf.content_type,
                    thumbnail = make_thumbnail(filepath, inf.name)
            )
            newfile.save()

    return newfile

def store_file(f, name, mime):
    digest = hash_file(f)
    filepath = path.join(settings.MEDIA_ROOT, digest)

    rewrite = False
    if path.exists(filepath):
        with open(filepath, 'rb') as o:
            flock(o, LOCK_EX)
            if not digest == hash_file(o):
                rewrite = True

    f.seek(0, 0)
    if (not path.exists(filepath)) or (rewrite):
        with open(filepath, 'wb+') as o:
            flock(o, LOCK_EX)
            for chunk in iter(lambda: f.read(1024), ''):
                o.write(chunk)
            size = o.tell()
            o.close()

    try:
        newfile = File.objects.get(sha1sum=digest)
    except ObjectDoesNotExist:
        newfile = File(
                name    = name,
                sha1sum = digest,
                size    = size,
                mime    = mime,
        )
        newfile.save()

    return digest
