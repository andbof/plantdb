from django.db import models
from validators import *

class File(models.Model):
    name      = models.CharField(max_length=128)
    sha1sum   = models.CharField(max_length=40, validators=[sha1validator])
    size      = models.IntegerField()
    mime      = models.CharField(max_length=48)
    created   = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name

# We don't make Image() a child of File() as Django will then create a File()
# object for every Image() created. Don't know if it can be fixed, it
# would be nice to not re-declare every field here.
class Image(models.Model):
    name      = models.CharField(max_length=128)
    sha1sum   = models.CharField(max_length=40, validators=[sha1validator])
    size      = models.IntegerField()
    mime      = models.CharField(max_length=48)
    thumbnail = models.ForeignKey('Image', blank=True, null=True, related_name='thumbnail_for_image')
    created   = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name
