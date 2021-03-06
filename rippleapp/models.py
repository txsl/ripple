from django.db import models
from picklefield.fields import PickledObjectField
from django.contrib.auth.models import User

import facebook
import soundcloud 
import musicbrainzngs as mbrainz
import requests

# Create your models here.
SOUNDCLOUD_CLIENT_ID  = 'b61d4560984dc7c38d3fc0fcb123cffc'
SOUNDCLOUD_CLIENT_SECRET = '271f398a01752aa7e5d4b6dbcfd8f87f'


def getLastFM(method, query):

	baseURL = "http://ws.audioscrobbler.com/2.0/?method="
	api_key = "&api_key=8717be831cfce83e52144bf79ff1c942&format=json"
	api_secret = '37f4a5667d5b106784a1f0e37a628249'
	r = requests.get(baseURL+method+query+api_key)
	if r.status_code != 200:
		return None
	return r.json()


class ripple(models.Model):

	name = models.CharField(max_length = 256)
	data = PickledObjectField(default = None)

	class Meta:
		abstract = True

	def __unicode__(self):
		return self.name


class Artist(ripple):
	musicbrainz_id = models.CharField(max_length = 3072)
	lastfm_id = models.CharField(max_length = 3072)
	soundcloud_id = models.CharField(max_length = 3072)
	soundcloud_url = models.CharField(max_length = 3072)
	fb_like_id = models.CharField(max_length = 3072)
	fb_page_id = models.CharField(max_length = 3072)
	social_media = PickledObjectField()
	last_events = PickledObjectField()
	aliases = PickledObjectField()
	mbrainz_cache = PickledObjectField()

	def GetMusicBrainz(self):
		mbrainz.set_useragent("Example music app", "0.1", "http://example.com/music")
		result = mbrainz.search_artists(self.name)['artist-list'][0]
		# for result in results:
		#   if int(result['ext:score']) > 75:
		#       break
		#print result
		self.musicbrainz_id = result['id']
		self.mbrainz_cache = mbrainz.get_artist_by_id(self.musicbrainz_id, ['artist-rels', 'url-rels'])['artist']
		if 'url-relation-list' in self.mbrainz_cache:
			self.social_media = self.mbrainz_cache.pop('url-relation-list')
		if 'artist-relation-list' in self.mbrainz_cache:
			self.aliases = self.mbrainz_cache.pop('artist-relation-list')

	def GetSoundcloud(self):

		for item in self.social_media:
			print item
			if item['type'] == 'soundcloud':
				sc = soundcloud.Client(client_id = SOUNDCLOUD_CLIENT_ID)
				self.soundcloud_url = item['target']
				self.soundcloud_id = sc.get('/resolve', url = item['target']).id
				break
		if not self.soundcloud_id:
			print 'no soundcloud id'
			client = soundcloud.Client(client_id = SOUNDCLOUD_CLIENT_ID)
			results = client.get('/users', q = self.name)
			for SoundcloudUser in results:
				if SoundcloudUser.track_count != 0:
					if self.name.lower() in SoundcloudUser.username.lower() or self.name.replace(" ","").lower() in SoundcloudUser.username.lower():
						self.soundcloud_id = SoundcloudUser.id
						self.soundcloud_url = SoundcloudUser.permalink_url
			print self.soundcloud_id, self.soundcloud_url
			
		# url = (item for item in self.social_media if item['type'] == 'soundcloud').next()['target']
				# self.soundcloud_id = sc.get('/resolve', url = url).id

	def GetLastEvents(self):
		if not self.musicbrainz_id:
			self.GetMusicBrainz()

		print getLastFM('artist.getevents', '&mbid='+self.musicbrainz_id)

		try:
			self.last_events = getLastFM('artist.getevents', '&mbid='+self.musicbrainz_id)['events']['event']
			if type(self.last_events) != list:
				self.last_events = [self.last_events]

			for event in self.last_events:
				event.pop('image')
				event.pop('attendance')
				event.pop('tickets')
				event.pop('reviews')

				event_obj, created = Event.objects.get_or_create(lastfm_id = event['id'], data = event)
				print event_obj, created
				self.data = self
				self.save()
				event_obj.artists.add(self)
				event_obj.save()

		except KeyError:
			self.last_events = {}

	def GetFacebookID(self):
		if not self.fb_page_id:
			self.GetMusicBrainz()	
		try:
			graph_url = (item for item in self.social_media if 'facebook' in item['target']).next()['target'].replace('www', 'graph')
			print graph_url
			self.fb_page_id = requests.get(graph_url).json()['id']
			print self.fb_page_id
		except:
			self.fb_page_id = '0'


class Event(ripple):
	lastfm_id = models.CharField(max_length = 1024)
	fb_id = models.CharField(max_length = 1024, blank = True, null = True)
	artists = models.ManyToManyField(Artist, related_name = 'events')



class fbUser(ripple):
	f_uid = models.IntegerField(db_index = True)
	music_likes = PickledObjectField()
	music_plays = PickledObjectField()
	friends_ids = PickledObjectField()









