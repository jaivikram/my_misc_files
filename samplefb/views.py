from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import urllib
import simplejson
import facebook
from settings import *
import logging
logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger('fb')

def getFBO(request):
    fb = facebook.Facebook(api_key=KEY, secret_key=SECRET)
    fb.session_key = request.session['session_key']
    fb.uid = request.session['uid']
    return fb

def sendme(request):
    return HttpResponseRedirect("http://www.facebook.com/login.php?"\
                                    "return_session=true&fbconnect=true&"\
                                    "next=%sfb/return/&v=1.0&api_key=%s&"\
                                    "display=page" % (BASE_URL, KEY)
                                )
def returnme(request):
    response = simplejson.loads(urllib.unquote(request.GET['session']))
    request.session['session_key'] = response['session_key']
    request.session['uid'] = response['uid']
    fb = getFBO(request)
    #log.info(str(response))
    try:
        userinfo  = fb.users.getInfo([fb.uid], ['name', 'birthday'])
        #log.info(str(userinfo))
    except:
        log.exception('')
    stream_perm_url = fb.get_ext_perm_url('read_stream', next='%sfb/offlineaccess/' % BASE_URL)
    return HttpResponseRedirect(stream_perm_url)

def offlineaccess(request):
    fb = getFBO(request)
    offline_access_url = fb.get_ext_perm_url('offline_access', next='%sfb/show/' % BASE_URL)
    return HttpResponseRedirect(offline_access_url)
    
def show(request):
    try:
        fb = getFBO(request)
        log.info(str(fb.stream.get(viewer_id=fb.uid)))
    except:
        log.exception('')
    return HttpResponse('done')
