import deepl
import os
from flask import current_app


def translate(text, source_lang, dest_lang):
    auth_key = os.getenv('deepl_api_key')
    if not auth_key:
        current_app.logger.info('Could not authenticate the api key')

    translator = deepl.Translator(auth_key)

    return translator.translate_text(
        text, source_lang=source_lang, target_lang=dest_lang
    ).text
