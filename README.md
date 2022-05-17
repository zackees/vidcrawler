# vidcrawler

Crawls major videos sites like YouTube/Rumble/Bitchute/Brighteon for video content and reports what it finds.

## Platform Unit Tests

[![Actions Status](https://github.com/zackees/vidcrawler/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_macos.yml)
[![Actions Status](https://github.com/zackees/vidcrawler/workflows/Win_Tests/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_win.yml)
[![Actions Status](https://github.com/zackees/vidcrawler/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/vidcrawler/actions/workflows/test_ubuntu.yml)

## API

#### Command line

`vidcrawler --input_crawl_json "fetch_list.json" --output_json "out_list.json"`

#### Python

```
from vidcrawler import crawl_video_sites

crawl_list = [
    ["channel name", "source", "channel_id"]
]
output = crawl_video_sites(crawl_list)

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

# Releases

  * 1.0.3: Bump
  * 1.0.2: Updates testing
  * 1.0.1: improves command line
  * 1.0.0: Initial release