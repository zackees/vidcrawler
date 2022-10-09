# vidcrawler

Crawls major videos sites like YouTube/Rumble/Bitchute/Brighteon for video content and outputs a json feed of all the videos that were found.

## Platform Unit Tests

[![Actions Status](https://github.com/zackees/vidcrawler/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_macos.yml)
[![Actions Status](https://github.com/zackees/vidcrawler/workflows/Win_Tests/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_win.yml)
[![Actions Status](https://github.com/zackees/vidcrawler/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_ubuntu.yml)

## API

#### Command line

`vidcrawler --input_crawl_json "fetch_list.json" --output_json "out_list.json"`

#### Python

```
import json
from vidcrawler import crawl_video_sites

crawl_list = [
    ["channel name", "source", "channel_id"]
]
output = crawl_video_sites(crawl_list)
print(json.dumps(output))
```

"source" and "channel_id" are used to generate the video-platform-specific urls to fetch data. The "channel name"
is echo'd back in the generated json feeds, but doesn't not affect the fetching process in any way.

## Testing

Install vidcrawler and then the command `vidcralwer_test` will become available.

```
$ pip install vidcrawler
$ vidcrawler_test
```


#### Example input `fetch_list.json`

```
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

```
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
      ...
  }
]
```

# Releases
  * 1.0.9: Fixes crawler for rumble and minor fixes + linting fixes.
  * 1.0.8: Readme correction.
  * 1.0.7: Fixes Odysee scraper by including image/webp thumbnail format.
  * 1.0.4: Fixes local_now() to be local timezone aware.
  * 1.0.3: Bump
  * 1.0.2: Updates testing
  * 1.0.1: improves command line
  * 1.0.0: Initial release
