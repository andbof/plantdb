from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from files.functions import store_file
from models import *
from forms import *

from functions import validate_params, generate_qr_from_layout

@login_required
def render_qr_list(request):
    return render_to_response('qr.html', {
        'qrform': QRForm()
    }, context_instance=RequestContext(request));

@login_required
def generate_qr(request):
    if not request.POST:
        return render_qr_list(request)
    else:
        layout = request.POST.get('layout', None)
        duplex = request.POST.get('duplex', None)
        if not validate_params(layout, duplex):
            return HttpResponseBadRequest()

        pdf = generate_qr_from_layout(layout, duplex)

        sha = store_file(pdf, 'qrlabels.pdf', 'application/pdf')

        pdf.close()
        return HttpResponseRedirect(reverse('download', args=(sha,)))
