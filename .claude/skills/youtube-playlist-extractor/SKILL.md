---
name: youtube-playlist-extractor
description: Use when extracting video titles and URLs from YouTube playlists, when user needs metadata beyond just video IDs, or when handling Unicode characters and HTML entities in YouTube content
---

# YouTube Playlist Extractor

## Overview

Extract complete metadata (titles + URLs) from YouTube playlists using curl and Python JSON parsing. Core principle: YouTube embeds video data in ytInitialData JSON object, allowing extraction without API keys or yt-dlp.

## When to Use

- User provides YouTube playlist URL and asks for video titles
- Need both URLs AND titles (not just video IDs)
- Batch processing multiple playlists with metadata
- User mentions "video titles", "video names", or "metadata"

**Don't use for:**
- Simple URL-only extraction (curl + grep is sufficient)
- Downloading videos (use yt-dlp)
- Playlist info requiring authentication

## Quick Reference

| Task | Approach |
|------|----------|
| URLs only | `curl + grep '"videoId"' + sort -u` |
| URLs + titles | `curl + Python JSON parsing of ytInitialData` |
| Parse JSON | `re.search(r'var ytInitialData = ({.*?});')` then `json.loads()` |
| Deduplication | Track `seen_ids` set in Python |

## Implementation

```python
import re
import json

# Fetch playlist HTML
# curl -s "https://www.youtube.com/playlist?list=PLAYLIST_ID" > /tmp/playlist.html

with open('/tmp/playlist.html', 'r') as f:
    content = f.read()

# Extract ytInitialData JSON object from the page
match = re.search(r'var ytInitialData = ({.*?});', content, re.DOTALL)
if not match:
    print("Could not find ytInitialData in page")
    exit(1)

data = json.loads(match.group(1))

# Navigate to playlist video items
contents = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])

video_data = []
seen_ids = set()

for tab in contents:
    tab_content = tab.get('tabRenderer', {}).get('content', {})
    section_contents = tab_content.get('sectionListRenderer', {}).get('contents', [])

    for section in section_contents:
        item_section = section.get('itemSectionRenderer', {}).get('contents', [])

        for item in item_section:
            playlist_items = item.get('playlistVideoListRenderer', {}).get('contents', [])

            for video in playlist_items:
                renderer = video.get('playlistVideoRenderer', {})
                video_id = renderer.get('videoId')
                title_runs = renderer.get('title', {}).get('runs', [])

                if video_id and title_runs and video_id not in seen_ids:
                    title = title_runs[0].get('text', '')
                    if title and len(title) > 15:
                        seen_ids.add(video_id)
                        video_data.append((video_id, title))

# Output
for video_id, title in video_data:
    print(f"{title}")
    print(f"https://www.youtube.com/watch?v={video_id}")
    print()
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using regex to match videoId + title | **CRITICAL**: Regex with `.*?` pairs wrong titles with video IDs. Must parse ytInitialData JSON |
| Using WebFetch for playlists | WebFetch may fail or truncate - use curl directly |
| Trying yt-dlp first | No need for heavy tools - curl + Python works |
| Not deduplicating | Use `seen_ids` set to track processed video IDs |
| Not filtering short titles | Filter titles with `len(title) > 15` to skip UI elements |

## Pattern Variations

**Multiple playlists**: Process each with same pattern, combine results

**CSV output**: Change print to `f'"{title}",https://www.youtube.com/watch?v={video_id}'`

**JSON output**: Build list of dicts: `{"title": title, "url": f"https://...{video_id}"}`
