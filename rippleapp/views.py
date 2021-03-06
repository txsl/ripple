# Create your views here.
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import redirect, render, render_to_response
from django.template import RequestContext
from ripple.settings import FB_KEY
from fb_friends import getFriends
from django.views.decorators.cache import cache_page

from models import *

import json
import facebook
import time
import pprint
import re

def index(request):
	return render_to_response('index.html', {'FB_ID':FB_KEY}, context_instance=RequestContext(request))
@cache_page(60 * 60)
def login(request):
	if request.is_ajax():
		print request.POST
        token = request.POST.get('token')
        uid = request.POST.get('fbid')
        print token
        data = json.dumps(getFriends(token, uid))
        mimetype = 'application/json'
        return HttpResponse(data, mimetype) 
@cache_page(60 * 60)
def get_artist_events(request):
    if request.is_ajax():
        name = request.POST.get('name')
        if not Artist.objects.filter(name = name):
            art = Artist(name = name)
            art.GetMusicBrainz()
            art.GetSoundcloud()
            art.GetLastEvents()
            art.GetFacebookID()
        else:
            art = Artist.objects.filter(name = name)[0]
        data = json.dumps(art.last_events)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype) 
@cache_page(60 * 60)
def get_artist_song(request):
    if request.is_ajax():
        name = request.POST.get('name')
        art = Artist(name = name)
        art.GetMusicBrainz()
        print art
        mimetype = 'application/json'
        try:
            art.GetSoundcloud()
            print art
            data = json.dumps(art.soundcloud_url)
            return HttpResponse(data, mimetype) 
        except:
            data = ''
            return HttpResponse(data, mimetype) 

def search(request):
    if request.is_ajax():
        mimetype = 'application/json'
        query = request.POST.get('query')
        print query, type(query), request
        data = ''
        return HttpResponse(data, mimetype) 



# All this stuff to allow verbatim
from django import template
 
register = template.Library()
 
 
class VerbatimNode(template.Node):
 
    def __init__(self, text):
        self.text = text
    
    def render(self, context):
        return self.text
 
 
@register.tag
def verbatim(parser, token):
    text = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == 'endverbatim':
            break
        if token.token_type == template.TOKEN_VAR:
            text.append('{{')
        elif token.token_type == template.TOKEN_BLOCK:
            text.append('{%')
        text.append(token.contents)
        if token.token_type == template.TOKEN_VAR:
            text.append('}}')
        elif token.token_type == template.TOKEN_BLOCK:
            text.append('%}')
    return VerbatimNode(''.join(text))