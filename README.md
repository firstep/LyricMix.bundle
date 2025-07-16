<p align="center"><a href="https://github.com/firstep/LyricMix.bundle" target="_blank"><img src="https://raw.githubusercontent.com/firstep/LyricMix.bundle/main/Contents/Resources/attribution.png" alt="LyricMix"></a></p>

# LyricMix.bundle

A Plex Music Lyrics Extension. [中文](https://github.com/firstep/LyricMix.bundle/blob/main/README_ZH.md)

-----

### Configuration

**1. For Legacy Agent (Last.fm)**

1.  In Plex Settings, enable LyricMix by following this path:
    `Settings` \> `Agents` \> `Albums` \> `Last.fm` \> Check and enable `LyricMix`.
2.  **Configure LyricMix Plugin**:
    Click the gear icon next to `LyricMix` and fill in the required music site Cookies.

**2. For Plex Music Agent**

As the new Plex Music Agent no longer directly supports secondary plugins for metadata, this extension utilizes Webhooks to manage lyrics for new albums.
(For further discussion, refer to: [Plex Forum](https://forums.plex.tv/t/how-to-add-or-customize-secondary-agents-e-g-for-lyrics-in-the-new-plex-music-agent))

1.  **Configure LyricMix Plugin**:
    Please first configure the required music site Cookies by accessing `LyricMix`'s settings as described in the "Legacy Agent" section above.
2.  **Enable Webhooks**:
    Go to `Settings` \> `Network` \> Enable `Webhooks`.
3.  **Add Webhook URL**:
    Add a new Webhook with the URL: `http://127.0.0.1:32400/lyric-mix/webhook?X-Plex-Token={your_plex_token}`

-----

### Additional Features

**Manually Refresh Album Lyrics**

You can manually trigger a lyrics refresh for a specific album by visiting this URL:
`http://{your_plex_server_ip_or_domain}:{your_plex_port}/lyric-mix/albums/{album_id}/refresh?X-Plex-Token={your_plex_token}`

-----

### References

This project incorporates functionalities from the following open-source projects:

  * [jitwxs/163MusicLyrics](https://github.com/jitwxs/163MusicLyrics)
  * [beata/zhconv](https://github.com/beata/zhconv)

-----