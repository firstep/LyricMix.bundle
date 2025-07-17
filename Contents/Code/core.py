# -*- coding: utf-8 -*-
# Author: firstep <https://github.com/firstep>
# Created: 2025-07-08
# LyricMix.bundle - Core Module
import json
from io import open
from collections import defaultdict

import utils

class MusicApiBase(object):
    def search(self, artist=None, album=None, track=None):
        raise NotImplementedError("search() must be implemented by subclass")

    def album_info(self, album_id):
        raise NotImplementedError("album_info() must be implemented by subclass")

    def lyrics(self, track_id):
        raise NotImplementedError("lyrics() must be implemented by subclass")
    
    def set_secret(self, secret, key=None):
        raise NotImplementedError("set_secret() must be implemented by subclass")
    
    def enabled(self):
        raise NotImplementedError("enabled() must be implemented by subclass")

music_api = None

def set_music_api(api):
    global music_api
    music_api = api

def search(artist, album=None, track=None):
    if album:
        try:
            if album:
                album = utils.extract_chinese_name(utils.ch_t2s(album))
                Log.Debug('[search] Search album: %s', album)

            albums = music_api.search(artist, album) # type: ignore
            foundAlbumCount = len(albums)
            Log.Debug('[search] Found %d albums for artist %s', foundAlbumCount, artist)
            for item in albums:
                score = utils.levenshtein_score(album, item['name'])
                if (foundAlbumCount > 1 and score < 85) or (foundAlbumCount == 1 and score < 50):
                    Log.Debug('[search] Album %s score is too low[%d], skip, expected is %s', item['name'], score, album)
                    continue
                
                albuminfo = music_api.album_info(item["idStr"]) # type: ignore
                if albuminfo and albuminfo['songs']:
                    return albuminfo['songs']
                else:
                    return []
        except Exception as e:
            import traceback
            Log.Error('[search] Error searching album %s by artist %s: %s\n%s', album, artist, e, traceback.format_exc())
            return []
    if track:
        try:
            return music_api.search(artist, track=track) # type: ignore
        except Exception as e:
            import traceback
            Log.Error('[search] Error searching track %s by artist %s: %s\n%s', track, artist, e, traceback.format_exc())
            return []
    
    Log.Warn('[search] Search params not valid, artist: %s, album: %s, track: %s', artist, album, track)
    return []

def add_lyric(metadata, album, track, song, valid_keys, track_key):
    Log.Debug('[add_lyric] Track %s ready to add lyric', track.title)

    track_name = utils.ch_t2s(track.title)
    if utils.levenshtein_score(track_name, song['name']) > 85:
        try:
            Log.Debug('[add_lyric] Track %s add lyric', track.title)
            (has, lyricfile) = utils.has_local_lyric(track)
            Log.Debug('[add_lyric] Track %s has local lyric: %s, file: %s', track_name, has, lyricfile)
            if has:
                if metadata:
                    metadata.tracks[track_key].lyrics[lyricfile] = Proxy.LocalFile(lyricfile, format='lrc')
                    valid_keys[track_key].append(lyricfile)
                return True

            lyric = music_api.lyrics(song['id']) # type: ignore
            if lyric and lyric.get('lrc', {}).get('lyric'):
                lyric_str = lyric['lrc']['lyric']

                with open(lyricfile, 'w+', encoding='utf8') as f:
                            f.write(lyric_str)
                            f.close()
                if metadata:
                    metadata.tracks[track_key].lyrics[lyricfile] = Proxy.LocalFile(lyricfile, format='lrc')
                    valid_keys[track_key].append(lyricfile)
                return True
            else:
                Log.Warn('[add_lyric] No lyric found for %s, lyric data:%s', track_name, json.dumps(lyric, ensure_ascii=False))
                return False
        except Exception as e:
            import traceback
            Log.Error('[add_lyric] Error adding lyric for track %s: %s\n%s', track_name, e, traceback.format_exc())
            return False
    else:
        Log.Debug('[add_lyric] Track %s score is too low, skip, expected is %s', track_name, song['name'])
    return False

def update_metadata(metadata, media, lang, force=False):
    """Update metadata for the given media item."""
    Log.Info("[update_metadata] Update %s - %s ", media.parentTitle, media.title)
    valid_keys = defaultdict(list)
    valid_track_keys = []
    added_ref = [False]

    # Only search if this is a new addition, the album was released within the past six months, or this is a manual refresh.
    if media.refreshed_at == None or Datetime.Now() - Datetime.ParseDate(media.originally_available_at or '1900') < Datetime.Delta(days=180) or force:
        songs = search(media.parentTitle, media.title)
        if songs is None or len(songs) == 0:
            Log.Info('[update_metadata] No songs found for %s', media.title)
            return
        
        def set_added():
            added_ref[0] = True

        @parallelize
        def match_lyrics():
            for index, track in enumerate(media.children):
                @task
                def match_lyric(index=index, track=track):
                    track_key = track.id or index
                    valid_keys[track_key] = []
                    valid_track_keys.append(track_key)

                    if metadata and len(metadata.tracks[track_key].lyrics) > 0 and not force:
                        Log.Info('%s already has lyrics, we won\'t search again', track.title)
                    else:
                        for song in songs:
                            if add_lyric(metadata, media.title, track, song, valid_keys, track_key):
                                set_added()

    if not metadata:
        if added_ref[0]:
            # If we are not updating metadata, we still need to refresh the metadata.
            req = Core.networking.http_request('http://%s:32400/library/metadata/%s/refresh' % ("127.0.0.1", media.id), method='PUT', cacheTime=0, immediate=True)
            Log.Debug('[update_metadata] Metadata refresh request sent for %s, response: %s', media.id, req.content)
        else:
            Log.Info('[update_metadata] No lyrics added for %s' % media.title)
        return

    # Make sure we validate lyric keys.
    for key in valid_keys.keys():
        metadata.tracks[key].lyrics.validate_keys(valid_keys[key])

    metadata.tracks.validate_keys(valid_track_keys)