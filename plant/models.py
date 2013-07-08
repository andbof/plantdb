from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.validators import MaxValueValidator, RegexValidator
from files.models import *
from validators import *

class CharNullField(models.CharField):
    description = "CharField that stores NULL but returns ''"
    def to_python(self, value):         # catches value right after getting it from the database
       if isinstance(value, models.CharField):  # overrides None with the empty string before passing it to Django
              return value
       if value is None:
              return ""
       else:
              return value
    def get_db_prep_value(self, value, connection, prepared):   # catches value right before sending to database from Django
       if value=="":                                            # overrides the empty string with None
            return None
       else:
            return value

class Tag(models.Model):
    tagnum       = models.PositiveIntegerField(unique=True, primary_key=True, validators=[MaxValueValidator(2176782335)])   # 2176782336 == 36^6
    tag          = models.SlugField(unique=True, max_length=6, validators=[RegexValidator(regex='^[A-Za-z0-9]+$')])
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id    = models.PositiveIntegerField(blank=True, null=True)
    target       = generic.GenericForeignKey('content_type', 'object_id')
    created      = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.tag + " -> " + unicode(self.target)

class Genus(models.Model):
    latin   = models.CharField(max_length=48)
    english = models.CharField(max_length=64, blank=True, null=True)
    swedish = models.CharField(max_length=64, blank=True, null=True)
    wpurl   = models.URLField(blank=True)
    image   = models.ForeignKey(Image, blank=True, null=True, related_name='+')
    images  = models.ManyToManyField(Image, blank=True, null=True, related_name='images_for_genus')
    files   = models.ManyToManyField(File, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return unicode(self.latin)

class Species(models.Model):
    genus   = models.ForeignKey(Genus)
    latin   = models.CharField(max_length=48)
    english = models.CharField(max_length=64, blank=True)
    swedish = models.CharField(max_length=64, blank=True)
    wpurl   = models.URLField(blank=True)
    image   = models.ForeignKey(Image, blank=True, null=True, related_name='+')
    images  = models.ManyToManyField(Image, blank=True, null=True, related_name='images_for_species')
    files   = models.ManyToManyField(File, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    def get_common_name(self):
        if self.swedish:
            return unicode(self.swedish)
        elif self.english:
            return unicode(self.english)
        elif self.latin:
            return unicode(self.latin)
        else:
            raise ValueError
    def __unicode__(self):
        return unicode(self.genus) + " " + unicode(self.latin)

class Cultivar(models.Model):
    species = models.ForeignKey(Species)
    latin   = models.CharField(max_length=64, blank=True)
    english = models.CharField(max_length=64, blank=True)
    swedish = models.CharField(max_length=64, blank=True)
    wpurl   = models.URLField(blank=True)
    image   = models.ForeignKey(Image, blank=True, null=True, related_name='+')
    images  = models.ManyToManyField(Image, blank=True, null=True, related_name='images_for_cultivar')
    files   = models.ManyToManyField(File, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        if self.swedish:
            return unicode(self.swedish)
        elif self.english:
            return unicode(self.english)
        elif self.latin:
            return unicode(self.latin)
        else:
            raise ValueError
    def get_long_name(self):
        return "%s '%s'" % (self.species.get_common_name(), self)

class Vendor(models.Model):
    name     = CharNullField(max_length=64, unique=True)
    location = models.CharField(max_length=64, blank=True)
    url      = models.URLField(blank=True)
    image    = models.ForeignKey(Image, blank=True, null=True, related_name='+')
    images   = models.ManyToManyField(Image, blank=True, null=True, related_name='images_for_vendor')
    files    = models.ManyToManyField(File, blank=True, null=True)
    created  = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.name

class Seed(models.Model):
    cultivar  = models.ForeignKey(Cultivar)
    vendor    = models.ForeignKey(Vendor, blank=True, null=True)
    barcode   = models.CharField(max_length=13, blank=True, null=True, validators=[barcodevalidator])
    parent    = models.ForeignKey('Plant', blank=True, null=True, related_name='child_seed')
    harvested = models.DateTimeField(blank=True, null=True)
    image     = models.ForeignKey(Image, blank=True, null=True, related_name='+')
    images    = models.ManyToManyField(Image, blank=True, null=True, related_name='images_for_seed')
    files     = models.ManyToManyField(File, blank=True, null=True)
    created   = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return unicode(self.cultivar)

class Plant(models.Model):
    cultivar = models.ForeignKey(Cultivar)
    seed     = models.ForeignKey(Seed, blank=True, null=True, related_name='child_plant')
    vendor   = models.ForeignKey(Vendor, blank=True, null=True)
    name     = CharNullField(max_length=64, blank=True, null=True, unique=True)
    planted  = models.DateTimeField(blank=True, null=True)
    death    = models.DateTimeField(blank=True, null=True)
    image    = models.ForeignKey(Image, blank=True, null=True, related_name='+')
    images   = models.ManyToManyField(Image, blank=True, null=True, related_name='images_for_plant')
    files    = models.ManyToManyField(File, blank=True, null=True)
    created  = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return unicode(self.cultivar)
