# -*- coding: utf-8 -*-
# Author: firstep <https://github.com/firstep>
# Created: 2025-07-08
# LyricMix.bundle - Mian Module
from core import update_metadata, set_music_api
from netease_musicapi import NeteaseMusicApi
from external_api import ExternalApi

@handler('/lyric-mix', "LyricMix")
def Main():
  con = MediaContainer()
  return con

external_api = None
music_api = None

def Start():
    HTTP.CacheTime = 3600
    global external_api
    external_api = ExternalApi()

    global music_api
    # TODO: multiple music API support
    # For now, we only support Netease Music API
    music_api = NeteaseMusicApi()
    music_api.set_secret(Prefs['NETEASE_SECRET'])
    set_music_api(music_api)

    Log.Info('LyricMix agent started')
    Plugin.Nice(15)

def ValidatePrefs():
    music_api.set_secret(Prefs['NETEASE_SECRET'])
    return True

class LyricMixAgent(Agent.Album):
    name = 'LyricMix'
    languages = [Locale.Language.NoLanguage]
    primary_provider = False
    contributes_to = ['com.plexapp.agents.lastfm', 'tv.plex.agents.music', 'org.musicbrainz.agents.music']
    
    def search(self, results, media, lang, manual=False):
        results.Append(MetadataSearchResult(id = 'null', score = 100))

    def update(self, metadata, media, lang, force=False):
        if not music_api.enabled():
            Log.Error('Netease Music API is not enabled, please check your settings.')
            return
        update_metadata(metadata, media, lang, force)


