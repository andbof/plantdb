from models import *

get_object_by_string = {
        'cultivar': Cultivar.objects.get,
        'genus':    Genus.objects.get,
        'plant':    Plant.objects.get,
        'seed':     Seed.objects.get,
        'species':  Species.objects.get,
        'vendor':   Vendor.objects.get,
}

get_string_by_object = {
        Cultivar: 'cultivar',
        Genus:    'genus',
        Plant:    'plant',
        Seed:     'seed',
        Species:  'species',
        Tag:      'tag',
}

def get_target(target_type, target_id):
    if (not target_type.isalpha()) or (not target_id.isdigit()):
        raise ValueError
    target_type = target_type.lower()
    if not target_type in get_object_by_string.keys():
        raise ValueError
    target = get_object_by_string[target_type](id=target_id)
    return target

def get_tag_target(tag):
    if tag.content_type.name == 'tag':
        return get_tag_target(tag.target)
    else:
        return tag.target


