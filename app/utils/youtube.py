import re


def get_youtube_id(url):
    """
    Extract the YouTube video ID from any common YouTube URL form.
    Returns the ID string, or None if it can't be parsed.

    Handles:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - URLs with extra query params
    """
    if not url:
        return None

    # Remove whitespace
    url = url.strip()

    patterns = [
        r"(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
        r"(?:m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_youtube_thumbnail(url):
    """
    Return the best-available thumbnail URL for a YouTube video.
    YouTube serves multiple qualities; maxresdefault is HD when available.
    """
    video_id = get_youtube_id(url)
    if not video_id:
        return None
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"