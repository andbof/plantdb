from plant.models import *
from django.contrib import admin

class GenusAdmin(admin.ModelAdmin):
    filter_horizontal = ('images','files')

class SpeciesAdmin(admin.ModelAdmin):
    filter_horizontal = ('images','files')

class CultivarAdmin(admin.ModelAdmin):
    filter_horizontal = ('images','files')

class VendorAdmin(admin.ModelAdmin):
    filter_horizontal = ('images','files')

class SeedAdmin(admin.ModelAdmin):
    filter_horizontal = ('images','files')

class PlantAdmin(admin.ModelAdmin):
    filter_horizontal = ('images','files')

admin.site.register(Tag)
admin.site.register(Genus,    GenusAdmin)
admin.site.register(Species,  SpeciesAdmin)
admin.site.register(Cultivar, CultivarAdmin)
admin.site.register(Vendor,   VendorAdmin)
admin.site.register(Seed,     SeedAdmin)
admin.site.register(Plant,    PlantAdmin)
