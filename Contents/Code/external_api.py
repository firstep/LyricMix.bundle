# -*- coding: utf-8 -*-
# Author: firstep <https://github.com/firstep>
# Created: 2025-07-08
# LyricMix.bundle - External API Module
from core import update_metadata, music_api_enabled

class ExternalApi(Object):
    def __init__(self):
        Route.Connect('/lyric-mix/webhook', self.webhook_handler, method='POST')
        Route.Connect('/lyric-mix/albums/{album_id}/refresh', self.refresh_album_handler, method='GET')
        Route.Connect('/lyric-mix/artists/{artist_id}/refresh', self.refresh_artist_handler, method='GET')
        Log.Info('External service initialized')

    def refresh_album_handler(self, album_id):
        if not album_id:
            return "No album id found"
        
        return self.refresh_album(album_id, 'album')

    def refresh_artist_handler(self, artist_id):
        if not artist_id:
            return "No artist id found"
        
        return self.refresh_album(artist_id, 'artist')

    def webhook_handler(self):
        payload_str = self.extract_payload()
        if not payload_str:
            return "No payload found"
        
        payload = JSON.ObjectFromString(payload_str)
        if "event" in payload and payload["event"] != "library.new":
            Log.Warn('[webhook_handler] unsupported event: %s', payload["event"])
            return 'Unsupported event'
        metadata = payload.get("Metadata")
        if not metadata:
            Log.Warn('[webhook_handler] no metadata in payload')
            return 'No metadata found'
        
        # Check if the metadata type is 'album'
        if not metadata.get('type') == 'album' and not metadata.get('type') == 'artist':
            Log.Info('[webhook_handler] unsupported metadata type: %s, payload:%s', metadata.get('type'), payload_str)
            return 'Unsupported metadata type'
        
        return self.refresh_album(metadata['ratingKey'], metadata.get('type'))

    def refresh_album(self, matadata_id, metadata_type='album'):
        try:
            if not music_api_enabled():
                Log.Warn('[refresh_album] music API is not enabled')
                return 'Music API is not enabled, please check your settings.'
            cls = getattr(Framework.api.agentkit.Media, '_class_named')('Album' if metadata_type == 'album' else 'Artist')
            if not cls:
                Log.Warn('[refresh_album] unsupported metadata class, matadata_id: %s', matadata_id)
                return 'Unsupported metadata class'
            matadata = Framework.api.agentkit.Media.TreeForDatabaseID(
                matadata_id,
                level_names=getattr(cls, '_level_names'),
                parent_id=None,
                level_attribute_keys=getattr(cls, '_level_attribute_keys')
            )
            if not matadata:
                Log.Warn('[refresh_album] no matadata found for id: %s', matadata_id)
                return 'No matadata found for id %s' % matadata_id
            
            Log.Debug('[refresh_album] refreshing matadata: %s, title: %s, parentTitle: %s', matadata.id, matadata.title, matadata.parentTitle)
            if metadata_type == 'album':
                update_metadata(None, matadata, Locale.Language.NoLanguage, force=True)
            else:
                artist = matadata.title
                for album in matadata.children:
                    album.parentTitle = artist
                    update_metadata(None, album, Locale.Language.NoLanguage, force=True)
            
            return 'Successfully refreshed metadata %s' % matadata_id
        except Exception as e:
            import traceback
            Log.Error('[refresh_album] Error refreshing album %s: %s\n%s', matadata_id, e, traceback.format_exc())
            return 'Error refreshing album, error message: %s' % e

    def extract_payload(self):
        content_type = Request.Headers.get('Content-Type', '').strip()
        if not content_type.startswith("multipart/form-data"):
            Log.Warn('[extract_payload] unsupported content type: %s', content_type)
            return None
        if not 'boundary=' in content_type:
            Log.Warn('[extract_payload] no boundary in content type: %s', content_type)
            return None
        
        boundary = content_type.split('boundary=',1)[1].strip().strip('"')
        if not boundary:
            Log.Warn('[extract_payload] empty boundary: %s', boundary)
            return None
        footer_length = len(boundary) + (6 if Request.Body.endswith("\r\n") else 4)
        parts = Request.Body[:-footer_length].split("--" + boundary + "\r\n")
        for part in parts:
            if not part: continue
            eoh = part.find("\r\n\r\n")
            if eoh == -1:
                Log.Warn("multipart/form-data missing headers")
                continue
            part_header = part[:eoh].strip()
            if not part_header.startswith("Content-Disposition: form-data; name=\"payload\""):
                Log.Warn('[extract_payload] unsupported part header: %s', part_header)
                continue
            return part[eoh + 4:-2]
        return None