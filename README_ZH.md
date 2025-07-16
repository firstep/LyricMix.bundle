<p align="center"><a href="https://github.com/firstep/LyricMix.bundle" target="_blank"><img src="https://raw.githubusercontent.com/firstep/LyricMix.bundle/main/Contents/Resources/attribution.png" alt="LyricMix"></a></p>

# LyricMix.bundle

一个 Plex 音乐歌词扩展。

-----

### 安装与配置

**1. 传统代理 (Legacy Agent: Last.fm)**

1.  在 Plex 设置中，请按以下路径启用 LyricMix：
    `设置 (Settings)` \> `代理 (Agents)` \> `专辑 (Albums)` \> `Last.fm` \> 勾选并启用 `LyricMix`。
2.  **配置 LyricMix 插件**：
    点击 `LyricMix` 旁的齿轮图标，填入所需的音乐站点 Cookie。

**2. Plex 音乐代理 (Plex Music Agent)**

鉴于新的 Plex 音乐代理不再直接支持二级插件提供信息，本扩展通过 Webhook 实现新专辑的歌词整理。
(更多讨论请参考：[Plex 官方论坛](https://forums.plex.tv/t/how-to-add-or-customize-secondary-agents-e-g-for-lyrics-in-the-new-plex-music-agent))

1.  **配置 LyricMix 插件**：
    请先按照上方“传统代理”部分的说明，进入 `LyricMix` 的设置界面，填入所需的音乐站点 Cookie。
2.  **启用 Webhooks 功能**：
    前往 `设置 (Settings)` \> `网络 (Network)` \> 启用 `Webhooks`。
3.  **添加 Webhook URL**：
    添加新的 Webhook，URL 设置为：`http://127.0.0.1:32400/lyric-mix/webhook?X-Plex-Token={你的PLEX服务器Token}`

-----

### 附加功能

**手动刷新专辑歌词**

您可以访问以下 URL 来手动刷新指定专辑的歌词：
`http://{你的Plex服务器IP或域名}:{你的Plex端口}/lyric-mix/albums/{album_id}/refresh?X-Plex-Token={your_plex_token}`

-----

### 参考项目

本项目部分功能借鉴以下开源项目：

  * [jitwxs/163MusicLyrics](https://github.com/jitwxs/163MusicLyrics)
  * [beata/zhconv](https://github.com/beata/zhconv)

-----