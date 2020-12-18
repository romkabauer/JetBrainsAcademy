import reverso_api
import itertools
import sys


def get_lang_abb(target_lang):
    try:
        return {
            "all": "all",
            "arabic": "ar",
            "german": "de",
            "english": "en",
            "spanish": "es",
            "french": "fr",
            "hebrew": "he",
            "japanese": "ja",
            "dutch": "nl",
            "polish": "pl",
            "portuguese": "pt",
            "romanian": "ro",
            "russian": "ru",
            "turkish": "tr"
        }[target_lang]
    except KeyError:
        raise KeyError


def get_full_lang(lang_abbreviation):
    try:
        return {
            "fr": "French",
            "en": "English",
            "ar": "Arabic",
            "de": "German",
            "es": "Spanish",
            "ja": "Japanese",
            "ru": "Russian",
            "nl": "Dutch",
            "pl": "Polish",
            "pt": "Portuguese",
            "ro": "Romanian",
            "he": "Hebrew",
            "tr": "Turkish"
        }[lang_abbreviation]
    except KeyError:
        return ""


def get_translation_context(reverso_api_response, top_words, top_examples):
    context = {"words": [], "examples": []}
    for translation in itertools.islice(reverso_api_response.get_translations(), 0, top_words):
        context["words"].append(translation.translation)
    for example in itertools.islice(reverso_api_response.get_examples(), 0, top_examples):
        context["examples"].append((example[0].text, example[1].text))
    return context


def prettify_output(translation_context, target_lang):
    output = f'\n{get_full_lang(target_lang)} Translations:'
    if len(translation_context["words"]) != 0:
        for word in translation_context["words"]:
            output += f'\n{word}'
    else:
        raise ValueError
    output += f'\n\n{get_full_lang(target_lang)} Examples:'
    for example in translation_context["examples"]:
        output += f'\n{example[0]}:\n{example[1]}\n'
    return output


def fetch_translation(source_lang, target_lang, word_to_translate, top_words, top_examples):
    try:
        translation = reverso_api.context.ReversoContextAPI(word_to_translate,
                                                            "",
                                                            source_lang,
                                                            target_lang)
    except Exception:
        raise Exception
    try:
        return prettify_output(get_translation_context(translation, top_words, top_examples), target_lang)
    except ValueError:
        raise ValueError


def write_to_file(info_to_write, name):
    f = open(name, 'a+')
    f.write(info_to_write)
    f.close()


def translate(source_lang, target_lang, word_to_translate):
    try:
        if target_lang != "all":
            write_to_file(fetch_translation(source_lang, target_lang, word_to_translate, 5, 10), word_to_translate + '.txt')
            f = open(word_to_translate + '.txt', "r")
            print(f.read())
        else:
            langs = ['ar', 'de', 'en', 'es', 'fr', 'he', 'ja', 'nl', 'pl', 'pt', 'ro', 'ru', 'tr']
            langs.remove(source_lang)
            output = ''
            for lang in langs:
                output += fetch_translation(source_lang, lang, word_to_translate, 1, 1)
            write_to_file(output, word_to_translate + '.txt')
            f = open(word_to_translate + '.txt', "r")
            print(f.read())
    except ValueError:
        print(f"Sorry, unable to find {word_to_translate}")
    except Exception:
        print("Something wrong with your internet connection")


if __name__ == "__main__":
    args = sys.argv
    try:
        source_lang = get_lang_abb(args[1].lower())
    except KeyError:
        print(f"Sorry, the program doesn't support {args[1]}")
        source_lang = NameError
    try:
        target_lang = get_lang_abb(args[2].lower())
    except KeyError:
        print(f"Sorry, the program doesn't support {args[2]}")
        target_lang = NameError
    try:
        word_to_translate = args[3].lower()
        translate(source_lang, target_lang, word_to_translate)
    except IndexError:
        print('Please enter 3 arguments: source language, target language(or all), word to translate.')
    except NameError:
        pass

