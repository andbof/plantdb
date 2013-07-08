import re
from datetime import datetime
from django.http import HttpResponseServerError, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from models import *
from tag import tag_to_tagnum, create_tag_if_not_found
from functions import *
from files.forms import *
from plantdb import settings

TAG_DELTA_MAX = 30
TAG_CHILD_WAIT = 10

def index(request):
    return render_to_response( 'index.html', {
        'plants': Plant.objects.order_by('-planted', '-created'),
        'seeds': Seed.objects.order_by('-harvested', '-created'),
        'vendors': Vendor.objects.order_by('name'),
        'mediaprefix': settings.MEDIA_URL,
    })

def render_tag(request, tag):
    t = get_object_or_404(Tag, tagnum=tag_to_tagnum(tag))
    if t.target is None:
        prev_tag_tag   = request.session.get('previous_tag_tag',  None)
        prev_tag_time  = request.session.get('previous_tag_time', None)
        if (prev_tag_tag is None) or (prev_tag_time is None):
            return render_to_response('tagnotarget.html', {'tag': t})
        if (not prev_tag_tag.isalnum()):
            return HttpResponseServerError(u'Invalid session previous_tag_tag')
        try:
            prev_tag = Tag.objects.get(tag=prev_tag_tag)
        except ObjectDoesNotExist:
            # Tag has probably been deleted since the user visited it, that's totally ok.
            return render_to_response('tagnotarget.html', {'tag': t})
        delta_tag = (datetime.now() - prev_tag_time).seconds
        if delta_tag > TAG_DELTA_MAX:
            return render_to_response('tagnotarget.html', {'tag': t})
        parent = get_tag_target(prev_tag)
        return render_to_response('tagnotarget.html', {
            'tag': t,
            'user': request.user,
            'parent': parent,
            'parent_type': get_string_by_object[type(parent)],
            'tag_delta_max': TAG_DELTA_MAX,
            'tag_child_wait': TAG_CHILD_WAIT,
        })
    elif t.content_type.name == 'file':
        return HttpResponseServerError(u'tag -> file not implemented')
    elif t.content_type.name == 'genus':
        return HttpResponseServerError(u'tag -> genus not implemented')
    elif t.content_type.name == 'species':
        return HttpResponseServerError(u'tag -> species not implemented')
    elif t.content_type.name == 'vendor':
        return HttpResponseServerError(u'tag -> vendor not implemented')
    elif t.content_type.name == 'seed':
        request.session['previous_tag_tag']  = t.tag
        request.session['previous_tag_time'] = datetime.now()
        return render_seed(request, t.target)
    elif t.content_type.name == 'plant':
        request.session['previous_tag_tag']  = t.tag
        request.session['previous_tag_time'] = datetime.now()
        return render_plant(request, t.target)
    elif t.content_type.name == 'tag':
        request.session['previous_tag_tag']  = t.tag
        request.session['previous_tag_time'] = datetime.now()
        return get_tag(request, t.target.tag)
    else:
        return HttpResponseServerError(u'Tag %u has an invalid target' % t.tagnum)

def render_plant_by_num(request, num):
    plant = get_object_or_404(Plant, id=num)
    return render_plant(request, plant)

def render_plant(request, plant, extradata=None):
    data = extradata if extradata is not None else {}
    data['plant']       = plant
    data['user']        = request.user
    data['imageform']   = ImageForm(initial = {'target_id': plant.id, 'target_type': 'plant'})
    data['fileform']    =  FileForm(initial = {'target_id': plant.id, 'target_type': 'plant'})
    data['mediaprefix'] = settings.MEDIA_URL
    if request.session.get('newplant'):
        del request.session['newplant']
        data['newplant'] = 1
    return render_to_response('plant.html', data, context_instance=RequestContext(request))

def render_seed_by_num(request, num):
    seed = get_object_or_404(Seed, id=num)
    return render_seed(request, seed)

def render_seed(request, seed, extradata=None):
    data = extradata if extradata is not None else {}
    data['seed']        = seed
    data['user']        = request.user
    data['imageform']   = ImageForm(initial = {'target_id': seed.id, 'target_type': 'seed'})
    data['fileform']    =  FileForm(initial = {'target_id': seed.id, 'target_type': 'seed'})
    data['mediaprefix'] = settings.MEDIA_URL
    if request.session.get('newseed'):
        del request.session['newseed']
        data['newseed'] = 1
    return render_to_response('seed.html', data, context_instance=RequestContext(request))

def render_vendor_by_num(request, num):
    vendor = get_object_or_404(Vendor, id=num)
    return render_vendor(request, vendor)

def render_vendor(request, vendor):
    p = Plant.objects.filter(vendor=vendor).order_by('-planted', '-created')
    s = Seed.objects.filter(vendor=vendor).order_by('-harvested', '-created')
    ps = Plant.objects.filter(seed__vendor=vendor).order_by('-planted', '-created')
    return render_to_response('vendor.html', {
        'vendor': vendor,
        'vendor_seeds': s,
	'vendor_seedplants': ps,
        'vendor_plants': p,
    })

@login_required
def associate_qr(request):
    if request.method == 'POST':
        target_type = request.POST.__getitem__('target_type').lower()
        if not target_type.isalpha():
            return HttpResponseBadRequest()
        target_id   = request.POST.__getitem__('target_id').lower()
        if not target_id.isdigit():
            return HttpResponseBadRequest()

        try:
            if target_type == u'plant':
                renderer = render_plant
                target = Plant.objects.get(id=target_id)
            elif target_type == u'seed':
                renderer = render_seed
                target = Seed.objects.get(id=target_id)
            else:
                return HttpResponseBadRequest(u'target_type should be "plant" or "seed"')
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(u'Invalid target_id supplied')

        qrcode = request.POST.__getitem__('qr').lower()
        qrcode = re.sub(r'^(http(?:s)?\:\/\/)?([a-z0-9_&\.-]+\/)+', '', qrcode, 0)   # Remove any URL prefix (i.e. http://foo.bar/quz/) in qrcode
        if not ( (len(qrcode) == 6) and (qrcode.isalnum()) ):
            return renderer(request, target, {'tag_failed_verification': 1})
        tagnum = tag_to_tagnum(qrcode)

        # Ensure tag exists (without any nasty race conditions)
        create_tag_if_not_found(tagnum)
        tag = Tag.objects.get(tagnum=tagnum)
        if (tag.target):
            return renderer(request, target, {'tag_already_associated': 1})

        tag.target = target
        tag.save()
        return renderer(request, target, {'tag_associated_ok': 1})

    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def make_child(request, parent_type, parent_id, tag):
    try:
        parent    = get_target(parent_type, parent_id)
        child_tag = Tag.objects.get(tag=tag)
    except:
        return HttpResponseNotFound()
    if type(parent) == Plant:
        child = Seed(
                cultivar  = parent.cultivar,
                parent    = parent,
                harvested = datetime.now(),
        )
        child.save()
        child_tag.target = child
        child_tag.save()
        request.session['newseed'] = 1
        return HttpResponseRedirect(reverse('seed', args=(child.id,)))
    elif type(parent) == Seed:
        child = Plant(
                cultivar = parent.cultivar,
                seed     = parent,
                planted  = datetime.now(),
        )
        child.save()
        child_tag.target = child
        child_tag.save()
        request.session['newplant'] = 1
        return HttpResponseRedirect(reverse('plant', args=(child.id,)))
    else:
        return HttpResponseBadRequest()
