# https://stackoverflow.com/questions/52455774/googletrans-stopped-working-with-error-nonetype-object-has-no-attribute-group
# NO: poetry add googletrans
# YES: poetry add googletrans==4.0.0-rc1

from __future__ import annotations

import re
import html
import urllib.request
import urllib.parse

# from googletrans import Translator

from ..utilities import get_default_resultset
from ..utilities import log_debug

from ..registry import ability


def translate(
    text: str,
    dest: str = "es",
    src: str = "auto"
) -> str:
    """
    Translates texts using the Google Translate API.

    Args:
        input_text (str): The text to translate.
        target_lang (str, optional): The language to translate the text to. Defaults to "auto".
        source_lang (str, optional): The language of the text to translate. Defaults to "auto".

    Returns:
        str: The translated text.
    """
    gta_url = f"http://translate.google.com/m?tl={dest}&" + \
              f"sl={src}&q={urllib.parse.quote(text)}"
    headers = {
        'User-Agent': "Mozilla/4.0 (compatible;MSIE 6.0;Windows NT 5.1;SV1;.NET" +
        " CLR 1.1.4322;.NET CLR 2.0.50727;.NET CLR 3.0.04506.30)"
    }
    request = urllib.request.Request(gta_url, headers=headers)
    with urllib.request.urlopen(request).read() as res_alloc:
        re_result = re.findall(
            r'(?s)class="(?:t0|result-container)">(.*?)<',
            res_alloc.decode("utf-8")
        )
    return "" if len(re_result) == 0 else html.unescape(re_result[0])


def lang_translate(
    input_text: str,
    target_lang: str = 'en',
    source_lang: str = 'auto'
) -> dict:
    response = get_default_resultset()
    if not response['error']:
        # Translate text to target language
        try:
            log_debug(f"Translator.translate to: {target_lang}")
            response["output_text"] = translate(
                text=input_text,
                dest=target_lang,
                src=source_lang
            )
            log_debug(
                "Text translated: " +
                response["output_text"]
            )
        except Exception as err:
            response['error'] = True
            response['error_msg'] = f"ERROR [GLT-020]: {str(err)}"
    return response


@ability(
    name="translator",
    description="Translates text to a target language",
    parameters=[
        {
            "name": "input_text",
            "description": "Text to be translated",
            "type": "str",
            "required": True,
        },
        {
            "name": "target_lang",
            "description": "Target language. Default: spanish",
            "type": "str",
            "required": False,
        },
        {
            "name": "source_lang",
            "description": "Source language. Default: auto detect",
            "type": "str",
            "required": False,
        },
    ],
    output_type="list[str]",
)
async def translator(
    agent,
    task_id: str,
    input_text: str,
    target_lang: str = 'es',
    source_lang: str = 'auto'
) -> str:
    """Translates text to a target language

    Args:
        input_text (str): text to be translated
        target_lang (str): target language
        source_lang (str): source language

    Returns:
        str: translated text or error message.
    """
    translation_result = lang_translate(
        input_text,
        target_lang,
        source_lang,
    )
    if translation_result["error"]:
        result = translation_result["error_msg"]
    else:
        result = translation_result["output_text"]
    return result
