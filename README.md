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

## Testing

``
$ vidcrawler_test
```


#### Example input fetch list

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