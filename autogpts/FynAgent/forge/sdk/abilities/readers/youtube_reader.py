from __future__ import annotations
import json

from langchain.document_loaders import YoutubeLoader

from ..registry import ability


def get_youtube_transcription(youtube_url: str, languages: list = None):
    if not languages:
        languages = ['en', 'es']
    loader = YoutubeLoader.from_youtube_url(
        youtube_url,
        add_video_info=True,
        language=languages
    )
    return loader.load()


@ability(
    name="youtube_transcription",
    description="Get youtube videos transcription",
    parameters=[
        {
            "name": "url",
            "description": "Youtube video URL",
            "type": "str",
            "required": True,
        },
        {
            "name": "languages",
            "description": "List of languages. Default: ['en', 'es']",
            "type": "list",
            "required": False,
        },
    ],
    output_type="list[str]",
)
async def youtube_transcription(
    agent,
    task_id: str,
    url: str,
    languages: list = None
) -> str:
    """Get youtube videos transcription

    Args:
        url (str): Youtube video URL
        languages (list): List of languages. Default: ['en', 'es']

    Returns:
        str: content of all PDF files.
    """
    results = json.dumps(
        get_youtube_transcription(url, languages),
        ensure_ascii=False,
        indent=4
    )
    return results
