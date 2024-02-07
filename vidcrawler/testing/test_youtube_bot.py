# pylint: disable=all

import os
import unittest

from vidcrawler.youtube_bot import fetch_all_sources



TEST_HTML = """
<ytd-rich-item-renderer class="style-scope ytd-rich-grid-row" items-per-row="3" is-slim-grid=""><!--css-build:shady--><!--css-build:shady--><div id="content" class="style-scope ytd-rich-item-renderer"><ytd-rich-grid-media class="style-scope ytd-rich-item-renderer" lockup="true" mini-mode=""><!--css-build:shady--><!--css-build:shady--><div id="dismissible" class="style-scope ytd-rich-grid-media"><div id="thumbnail" class="style-scope ytd-rich-grid-media"><ytd-thumbnail rich-grid-thumbnail="" use-hovered-property="" width="9999" class="style-scope ytd-rich-grid-media" size="large" loaded=""><!--css-build:shady--><!--css-build:shady--><a id="thumbnail" class="yt-simple-endpoint inline-block style-scope ytd-thumbnail" aria-hidden="true" tabindex="-1" rel="null" href="/watch?v=ikuJY1dhX4E">
  <yt-image alt="" ftl-eligible="" notify-on-loaded="" notify-on-unloaded="" class="style-scope ytd-thumbnail"><img alt="" style="background-color: transparent;" class="yt-core-image yt-core-image--fill-parent-height yt-core-image--fill-parent-width yt-core-image--content-mode-scale-aspect-fill yt-core-image--loaded" src="https://i.ytimg.com/vi/ikuJY1dhX4E/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&amp;rs=AOn4CLC8-ndq0eCdfT9vPbygFo5mffR6RA"></yt-image>
  
  <div id="overlays" class="style-scope ytd-thumbnail"><ytd-thumbnail-overlay-time-status-renderer class="style-scope ytd-thumbnail" overlay-style="DEFAULT"><!--css-build:shady--><!--css-build:shady--><ytd-badge-supported-renderer is-thumbnail-badge="" class="style-scope ytd-thumbnail-overlay-time-status-renderer" system-icons=""><!--css-build:shady--><!--css-build:shady--><dom-repeat id="repeat" as="badge" class="style-scope ytd-badge-supported-renderer"><template is="dom-repeat"></template></dom-repeat></ytd-badge-supported-renderer><div id="time-status" class="style-scope ytd-thumbnail-overlay-time-status-renderer"><yt-icon size="16" class="style-scope ytd-thumbnail-overlay-time-status-renderer" disable-upgrade="" hidden=""></yt-icon><span id="text" class="style-scope ytd-thumbnail-overlay-time-status-renderer" aria-label="16 minutes, 33 seconds">
    16:33
  </span></div></ytd-thumbnail-overlay-time-status-renderer><ytd-thumbnail-overlay-now-playing-renderer class="style-scope ytd-thumbnail"><!--css-build:shady--><!--css-build:shady--><span id="overlay-text" class="style-scope ytd-thumbnail-overlay-now-playing-renderer">Now playing</span>
<ytd-thumbnail-overlay-equalizer class="style-scope ytd-thumbnail-overlay-now-playing-renderer"><!--css-build:shady--><!--css-build:shady--><svg xmlns="http://www.w3.org/2000/svg" id="equalizer" viewBox="0 0 55 95" class="style-scope ytd-thumbnail-overlay-equalizer">
  <g class="style-scope ytd-thumbnail-overlay-equalizer">
    <rect class="bar style-scope ytd-thumbnail-overlay-equalizer" x="0"></rect>
    <rect class="bar style-scope ytd-thumbnail-overlay-equalizer" x="20"></rect>
    <rect class="bar style-scope ytd-thumbnail-overlay-equalizer" x="40"></rect>
  </g>
</svg>
</ytd-thumbnail-overlay-equalizer>
</ytd-thumbnail-overlay-now-playing-renderer></div>
  <div id="mouseover-overlay" class="style-scope ytd-thumbnail"></div>
  <div id="hover-overlays" class="style-scope ytd-thumbnail"></div>
</a>
</ytd-thumbnail><ytd-playlist-thumbnail is-double-stack="" use-hovered-property="" width="9999" class="style-scope ytd-rich-grid-media" thumbnail-size="medium" enable-web-modern-collections-v2="" size="large" hidden=""><!--css-build:shady--><!--css-build:shady--><yt-collections-stack class="collections-stack-wiz style-scope ytd-playlist-thumbnail"><div><div class="collections-stack-wiz__collection-stack2" style=""></div><div class="collections-stack-wiz__collection-stack1 collections-stack-wiz__collection-stack1--medium" style=""></div></div></yt-collections-stack>
<a id="thumbnail" class="yt-simple-endpoint style-scope ytd-playlist-thumbnail" tabindex="-1" aria-hidden="true" href="/watch?v=ikuJY1dhX4E">
  <div id="playlist-thumbnails" class="style-scope ytd-playlist-thumbnail"></div>
  <yt-formatted-string id="length" class="style-scope ytd-playlist-thumbnail" aria-label="16 minutes, 33 seconds">16:33</yt-formatted-string>
  <div id="overlays" class="style-scope ytd-playlist-thumbnail"><ytd-thumbnail-overlay-time-status-renderer class="style-scope ytd-playlist-thumbnail" overlay-style="DEFAULT"><!--css-build:shady--><!--css-build:shady--><ytd-badge-supported-renderer is-thumbnail-badge="" class="style-scope ytd-thumbnail-overlay-time-status-renderer" system-icons=""><!--css-build:shady--><!--css-build:shady--><dom-repeat id="repeat" as="badge" class="style-scope ytd-badge-supported-renderer"><template is="dom-repeat"></template></dom-repeat></ytd-badge-supported-renderer><div id="time-status" class="style-scope ytd-thumbnail-overlay-time-status-renderer"><yt-icon size="16" class="style-scope ytd-thumbnail-overlay-time-status-renderer" disable-upgrade="" hidden=""></yt-icon><span id="text" class="style-scope ytd-thumbnail-overlay-time-status-renderer" aria-label="16 minutes, 33 seconds">
    16:33
  </span></div></ytd-thumbnail-overlay-time-status-renderer><ytd-thumbnail-overlay-now-playing-renderer class="style-scope ytd-playlist-thumbnail"><!--css-build:shady--><!--css-build:shady--><span id="overlay-text" class="style-scope ytd-thumbnail-overlay-now-playing-renderer">Now playing</span>
<ytd-thumbnail-overlay-equalizer class="style-scope ytd-thumbnail-overlay-now-playing-renderer"><!--css-build:shady--><!--css-build:shady--><svg xmlns="http://www.w3.org/2000/svg" id="equalizer" viewBox="0 0 55 95" class="style-scope ytd-thumbnail-overlay-equalizer">
  <g class="style-scope ytd-thumbnail-overlay-equalizer">
    <rect class="bar style-scope ytd-thumbnail-overlay-equalizer" x="0"></rect>
    <rect class="bar style-scope ytd-thumbnail-overlay-equalizer" x="20"></rect>
    <rect class="bar style-scope ytd-thumbnail-overlay-equalizer" x="40"></rect>
  </g>
</svg>
</ytd-thumbnail-overlay-equalizer>
</ytd-thumbnail-overlay-now-playing-renderer></div>
  <div id="hover-overlays" class="style-scope ytd-playlist-thumbnail"></div>
</a>
</ytd-playlist-thumbnail></div><div id="thumbnail-underlay" class="style-scope ytd-rich-grid-media" hidden=""></div><div id="details" class="style-scope ytd-rich-grid-media"><a id="avatar-link" class="yt-simple-endpoint style-scope ytd-rich-grid-media" tabindex="-1" title="undefined" hidden=""><yt-img-shadow id="avatar" width="48" class="style-scope ytd-rich-grid-media no-transition"><!--css-build:shady--><!--css-build:shady--><img id="img" draggable="false" class="style-scope yt-img-shadow" alt="" width="48"></yt-img-shadow></a><div id="meta" class="style-scope ytd-rich-grid-media"><h3 class="style-scope ytd-rich-grid-media"><ytd-badge-supported-renderer class="top-badge style-scope ytd-rich-grid-media" collection-truncate="" disable-upgrade="" hidden=""></ytd-badge-supported-renderer><a id="video-title-link" class="yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media" aria-label="Storage Problems at Big Banks by The Morgan Report 2,130 views 4 days ago 16 minutes" title="Storage Problems at Big Banks" href="/watch?v=ikuJY1dhX4E"><yt-formatted-string id="video-title" class="style-scope ytd-rich-grid-media" aria-label="Storage Problems at Big Banks by The Morgan Report 2,130 views 4 days ago 16 minutes">Storage Problems at Big Banks</yt-formatted-string></a></h3><ytd-video-meta-block class="grid style-scope ytd-rich-grid-media byline-separated" rich-meta="" amsterdam-post-mvp="" mini-mode=""><!--css-build:shady--><!--css-build:shady-->
<div id="metadata" class="style-scope ytd-video-meta-block">
  <div id="byline-container" class="style-scope ytd-video-meta-block" hidden="">
    <ytd-channel-name id="channel-name" class=" style-scope ytd-video-meta-block style-scope ytd-video-meta-block"><!--css-build:shady--><!--css-build:shady--><div id="container" class="style-scope ytd-channel-name">
  <div id="text-container" class="style-scope ytd-channel-name">
    <yt-formatted-string id="text" link-inherit-color="" title="" class="style-scope ytd-channel-name" is-empty="" ellipsis-truncate="" ellipsis-truncate-styling=""><!--css-build:shady--><!--css-build:shady--><yt-attributed-string class="style-scope yt-formatted-string"></yt-attributed-string></yt-formatted-string>
  </div>
  <tp-yt-paper-tooltip fit-to-visible-bounds="" class="style-scope ytd-channel-name" role="tooltip" tabindex="-1"><!--css-build:shady--><div id="tooltip" class="hidden style-scope tp-yt-paper-tooltip" style-target="tooltip">
  
    
  
</div>
</tp-yt-paper-tooltip>
</div>
<ytd-badge-supported-renderer class="style-scope ytd-channel-name" disable-upgrade="" hidden="">
</ytd-badge-supported-renderer>
</ytd-channel-name>
    <div id="separator" class="style-scope ytd-video-meta-block">•</div>
    <yt-formatted-string id="video-info" class="style-scope ytd-video-meta-block" is-empty="" hidden=""><!--css-build:shady--><!--css-build:shady--><yt-attributed-string class="style-scope yt-formatted-string"></yt-attributed-string></yt-formatted-string>
  </div>
  <div id="metadata-line" class="style-scope ytd-video-meta-block">
    
    <ytd-badge-supported-renderer class="inline-metadata-badge style-scope ytd-video-meta-block" hidden="" system-icons=""><!--css-build:shady--><!--css-build:shady--><dom-repeat id="repeat" as="badge" class="style-scope ytd-badge-supported-renderer"><template is="dom-repeat"></template></dom-repeat></ytd-badge-supported-renderer>
    <div id="separator" class="style-scope ytd-video-meta-block" hidden="">•</div>
    
      <span class="inline-metadata-item style-scope ytd-video-meta-block">2.1K views</span>
    
      <span class="inline-metadata-item style-scope ytd-video-meta-block">4 days ago</span>
    <dom-repeat strip-whitespace="" class="style-scope ytd-video-meta-block"><template is="dom-repeat"></template></dom-repeat>
  </div>
</div>
<div id="additional-metadata-line" class="style-scope ytd-video-meta-block">
  <dom-repeat class="style-scope ytd-video-meta-block"><template is="dom-repeat"></template></dom-repeat>
</div>

</ytd-video-meta-block><ytd-badge-supported-renderer class="video-badge style-scope ytd-rich-grid-media" disable-upgrade="" hidden=""></ytd-badge-supported-renderer><ytd-badge-supported-renderer class="title-badge style-scope ytd-rich-grid-media" disable-upgrade="" hidden=""></ytd-badge-supported-renderer><yt-formatted-string id="view-more" link-inherit-color="" class="style-scope ytd-rich-grid-media" is-empty="" hidden=""><!--css-build:shady--><!--css-build:shady--><yt-attributed-string class="style-scope yt-formatted-string"></yt-attributed-string></yt-formatted-string><div id="buttons" class="style-scope ytd-rich-grid-media"></div></div><div id="menu" class="style-scope ytd-rich-grid-media"><ytd-menu-renderer class="style-scope ytd-rich-grid-media" safe-area=""><!--css-build:shady--><!--css-build:shady--><div id="top-level-buttons-computed" class="top-level-buttons style-scope ytd-menu-renderer"></div><div id="flexible-item-buttons" class="style-scope ytd-menu-renderer"></div><yt-icon-button id="button" class="dropdown-trigger style-scope ytd-menu-renderer" style-target="button"><!--css-build:shady--><!--css-build:shady--><button id="button" class="style-scope yt-icon-button" aria-label="Action menu"><yt-icon class="style-scope ytd-menu-renderer"><!--css-build:shady--><!--css-build:shady--><yt-icon-shape class="style-scope yt-icon"><icon-shape class="yt-spec-icon-shape"><div style="width: 100%; height: 100%; fill: currentcolor;"><svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24" viewBox="0 0 24 24" width="24" focusable="false" style="pointer-events: none; display: block; width: 100%; height: 100%;"><path d="M12 16.5c.83 0 1.5.67 1.5 1.5s-.67 1.5-1.5 1.5-1.5-.67-1.5-1.5.67-1.5 1.5-1.5zM10.5 12c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5-.67-1.5-1.5-1.5-1.5.67-1.5 1.5zm0-6c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5-.67-1.5-1.5-1.5-1.5.67-1.5 1.5z"></path></svg></div></icon-shape></yt-icon-shape></yt-icon></button><yt-interaction id="interaction" class="circular style-scope yt-icon-button"><!--css-build:shady--><!--css-build:shady--><div class="stroke style-scope yt-interaction"></div><div class="fill style-scope yt-interaction"></div></yt-interaction></yt-icon-button><yt-button-shape id="button-shape" version="modern" class="style-scope ytd-menu-renderer" disable-upgrade="" hidden=""></yt-button-shape></ytd-menu-renderer></div></div><div id="attached-survey" class="style-scope ytd-rich-grid-media"></div></div><div id="dismissed" class="style-scope ytd-rich-grid-media"><div id="dismissed-content" class="style-scope ytd-rich-grid-media"></div></div><yt-interaction id="interaction" class="extended style-scope ytd-rich-grid-media"><!--css-build:shady--><!--css-build:shady--><div class="stroke style-scope yt-interaction"></div><div class="fill style-scope yt-interaction"></div></yt-interaction></ytd-rich-grid-media></div>
</ytd-rich-item-renderer>
"""


URL_SILVERGURU = "https://www.youtube.com/@silverguru/videos"


class YouTubeBotTester(unittest.TestCase):
    def test_one(self) -> None:
        # vids = fetch_all_vids(URL_SILVERGURU)
        sources: list[str] = fetch_all_sources(URL_SILVERGURU)
        self.assertGreater(len(sources), 0)


if __name__ == "__main__":
    unittest.main()
