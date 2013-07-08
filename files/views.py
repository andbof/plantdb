from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseNotFound
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from plantdb import settings
from plant.models import *
from plant.functions import get_target
from files.functions import FileType, handle_uploaded_file
from files.forms import *
from files.validators import sha1validator
from os import path

@login_required
def upload(request, filetype):
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        target_type = request.POST['target_type']
        target_id   = request.POST['target_id']
        if form.is_valid() and target_type.isalpha() and target_id.isdigit():
            try:
                target = get_target(target_type, target_id)
            except ObjectDoesNotExist:
                return HttpResponseBadRequest('Target id does not exist')

            fil = handle_uploaded_file(request.FILES['filedata'], filetype)
            if filetype == FileType.IMAGE:
                target.images.add(fil)
                if not target.image:
                    target.image = fil
            else:
                target.files.add(fil)
            target.save()

            referer = request.META.get('HTTP_REFERER', '/')
            return HttpResponseRedirect(referer)
        else:
            return HttpResponseBadRequest('File upload form not valid')
    else:
        return HttpResponseNotAllowed(['POST'])

def download(request, sha):
    if not sha1validator(sha):
        return HttpResponseNotFound()
    try:
        imagetarget = Image.objects.get(sha1sum=sha)
    except ObjectDoesNotExist:
        try:
            filetarget = File.objects.get(sha1sum=sha)
        except ObjectDoesNotExist:
            return HttpResponseNotFound()
        else:
            filepath = path.join(settings.MEDIA_ROOT, filetarget.sha1sum)
            wrapper  = FileWrapper(file(filepath, 'rb'))
            response = HttpResponse(wrapper, content_type=filetarget.mime)
            response['Content-Disposition'] = 'attachment; filename=' + filetarget.name
            response['Content-Length'] = filetarget.size
    else:
        filepath = path.join(settings.MEDIA_ROOT, imagetarget.sha1sum)
        wrapper  = FileWrapper(file(filepath, 'rb'))
        response = HttpResponse(wrapper, content_type=imagetarget.mime)
        response['Content-Length'] = imagetarget.size

    return response
