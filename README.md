# vidcrawler

Crawls major videos sites like YouTube/Rumble/Bitchute/Brighteon for video content and outputs a json feed of all the videos that were found.

## Platform Unit Tests

[![MacOS_Tests](https://github.com/zackees/vidcrawler/actions/workflows/test_macos.yml/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_macos.yml)
[![Win_Tests](https://github.com/zackees/vidcrawler/actions/workflows/test_win.yml/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_win.yml)
[![Ubuntu_Tests](https://github.com/zackees/vidcrawler/actions/workflows/test_ubuntu.yml/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_ubuntu.yml)

## Scraper Tests

[![Scaper_Youtube](https://github.com/zackees/vidcrawler/actions/workflows/test_youtube.yml/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_youtube.yml)
[![Actions Status](https://github.com/zackees/vidcrawler/workflows/Scaper_Rumble/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_rumble.yml)
[![Scaper_Brighteon](https://github.com/zackees/vidcrawler/actions/workflows/test_brighteon.yml/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_brighteon.yml)
[![Actions Status](https://github.com/zackees/vidcrawler/workflows/Scraper_Gabtv/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_gabtv.yml)
[![Actions Status](https://github.com/zackees/vidcrawler/workflows/Scraper_Spotify/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_spotify.yml)

Note that bitchute doesn't like the github runner's IP and will fail with a 403 forbidden.
[![Actions Status](https://github.com/zackees/vidcrawler/workflows/Scaper_Bitchute/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_bitchute.yml)

## API

#### Command line

`vidcrawler --input_crawl_json "fetch_list.json" --output_json "out_list.json"`

#### Python

```python
import json
from vidcrawler import crawl_video_sites
crawl_list = [
    [
        "Computing Forever",  # Can be whatever you want.
        "bitchute",  # Must be "youtube", "rumble", "bitchute" (and others).
        "hybm74uihjkf"  # The channel id on the service.
    ]
]
output = crawl_video_sites(crawl_list)
print(json.dumps(output))
```

"source" and "channel_id" are used to generate the video-platform-specific urls to fetch data. The "channel name"
is echo'd back in the generated json feeds, but doesn't not affect the fetching process in any way.

## Testing

Install vidcrawler and then the command `vidcralwer_test` will become available.

```bash
> pip install vidcrawler
> vidcrawler_test
```

# youtube-pull-channel

This new command will a channel and all of it's files as mp3s. Great for transcribing and putting into an LLM.


#### Example input `fetch_list.json`

```json
[
    [
        "Health Ranger Report",
        "brighteon",
        "hrreport"
    ],
    [
        "Sydney Watson",
        "youtube",
        "UCSFy-1JrpZf0tFlRZfo-Rvw"
    ],
    [
        "Computing Forever",
        "bitchute",
        "hybm74uihjkf"
    ],
    [
        "ThePeteSantilliShow",
        "rumble",
        "ThePeteSantilliShow"
    ],
    [
        "Macroaggressions",
        "odysee",
        "Macroaggressions"
    ]
]
```

#### Example Output:

```json
[
  {
    "channel_name": "ThePeteSantilliShow",
    "title": "The damage this caused is now being totaled up",
    "date_published": "2022-05-17T05:00:11+00:00",
    "date_lastupdated": "2022-05-17T05:17:18.540084",
    "channel_url": "https://www.youtube.com/channel/UCXIJgqnII2ZOINSWNOGFThA",
    "source": "youtube.com",
    "url": "https://www.youtube.com/watch?v=bwqBudCzDrQ",
    "duration": 254,
    "description": "",
    "img_src": "https://i3.ytimg.com/vi/bwqBudCzDrQ/hqdefault.jpg",
    "iframe_src": "https://youtube.com/embed/bwqBudCzDrQ",
    "views": 1429
  },
  {
     "channel_name": "ThePeteSantilliShow",
     "title": "..."
  }
]
```

# Releases
  * 1.0.37: Misc fixes.
  * 1.0.36: Fixed youtube, rumble and brighteon parsers. Bitchute is still broken and now has rate limits.
  * 1.0.35: Added `update_yt_dlp()` to allow the client to update the downloader.
  * 1.0.34: Upgraded `open-webdriver` to version `1.5.0` to avoid `yt-dlp` urllib incompatibility.
  * 1.0.28: youtube_pull now takes in --channel-name and --output, like the other pullers
  * 1.0.27: Fixed polluting path space from multiple added static-ffmpeg
  * 1.0.24: Added `rumble-pull-channel`
  * 1.0.21: Misc fixes
  * 1.0.16: Make the library downloading more robust.
  * 1.0.15: Improve cleaning filepaths for brighteon_bot
  * 1.0.13: New `brighteon-pull-channel` command
  * 1.0.11: Improves `youtube-pull-channel`
  * 1.0.10: Adds `youtube-pull-channel` which pulls all files down as mp3s for a channel.
  * 1.0.9: Fixes crawler for rumble and minor fixes + linting fixes.
  * 1.0.8: Readme correction.
  * 1.0.7: Fixes Odysee scraper by including image/webp thumbnail format.
  * 1.0.4: Fixes local_now() to be local timezone aware.
  * 1.0.3: Bump
  * 1.0.2: Updates testing
  * 1.0.1: improves command line
  * 1.0.0: Initial release
