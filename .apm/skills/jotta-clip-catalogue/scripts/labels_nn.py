#!/usr/bin/env python3
"""Nynorsk renderings for subtitle cues.

LYD_NN: AudioSet labels (lowercase) -> nynorsk, for the [lyd: ...] cues.
AudioSet has 527 classes; this maps the ones that actually occur in travel/
transport/nature footage. Unmapped labels pass through in English — the scripts
that use this report them, and Claude should translate and EXTEND THIS MAP
rather than patch downstream files.

LANG_NN: whisper language codes -> norske språknamn, for the "[På engelsk] ..."
prefix on non-Norwegian speech.
"""

LYD_NN = {
    # transport
    "vehicle": "køyretøy", "car": "bil", "car passing by": "bil som passerer",
    "bus": "buss", "truck": "lastebil", "motorcycle": "motorsykkel",
    "bicycle": "sykkel", "skateboard": "rullebrett",
    "train": "tog", "rail transport": "jernbane",
    "railroad car, train wagon": "togvogn", "train horn": "toghorn",
    "train whistle": "togfløyte", "train wheels squealing": "hjulskrik",
    "subway, metro, underground": "t-bane",
    "aircraft": "fly", "fixed-wing aircraft, airplane": "fly",
    "helicopter": "helikopter", "propeller, airscrew": "propell",
    "jet engine": "jetmotor",
    "boat, water vehicle": "båt", "ship": "skip",
    "motorboat, speedboat": "motorbåt", "sailboat, sailing ship": "seglbåt",
    "engine": "motor", "idling": "tomgang",
    "accelerating, revving, vroom": "akselerasjon",
    "engine starting": "motorstart", "air brake": "trykkluftbrems",
    "air horn, truck horn": "trykklufthorn",
    "vehicle horn, car horn, honking": "bilhorn", "car alarm": "bilalarm",
    "traffic noise, roadway noise": "trafikkstøy", "race car, auto racing": "racerbil",
    "skidding": "hjulspinn", "tire squeal": "dekkskrik",
    # vêr og natur
    "rain": "regn", "rain on surface": "regn mot flate", "raindrop": "regndropar",
    "thunder": "tore", "thunderstorm": "torevêr",
    "wind": "vind", "wind noise (microphone)": "vindsus i mikrofonen",
    "rustling leaves": "lauvras",
    "water": "vatn", "stream": "bekk", "waterfall": "foss",
    "ocean": "hav", "waves, surf": "bølgjer", "gurgling": "klukking",
    "rumble": "buldring",
    # dyr
    "bird": "fugl", "bird vocalization, bird call, bird song": "fuglesong",
    "pigeon, dove": "due", "crow": "kråke", "gull, seagull": "måse",
    "duck": "and", "goose": "gås", "dog": "hund", "bark": "bjeffing",
    "cat": "katt", "insect": "insekt", "sheep": "sau", "cattle, bovinae": "kyr",
    # folk og rom
    "speech": "tale", "conversation": "samtale", "chatter": "prat",
    "crowd": "folkemengd", "hubbub, speech noise, speech babble": "summing av folk",
    "children playing": "barneleik", "laughter": "lått", "applause": "applaus",
    "cheering": "jubel", "clapping": "klapping",
    "walk, footsteps": "fotsteg", "run": "spring",
    "door": "dør", "sliding door": "skyvedør", "knock": "banking",
    "bell": "bjølle", "church bell": "kyrkjeklokke", "bicycle bell": "sykkelbjølle",
    "siren": "sirene", "music": "musikk", "silence": "stille",
    "beep, bleep": "pip", "click": "klikk", "squeak": "knirk",
    "rattle": "skrangling", "whoosh, swoosh, swish": "sus", "hiss": "vising",
    "camera": "kamera", "typing": "tasting",
}

LANG_NN = {
    "en": "engelsk", "sv": "svensk", "da": "dansk", "de": "tysk",
    "fr": "fransk", "es": "spansk", "it": "italiensk", "nl": "nederlandsk",
    "pl": "polsk", "ru": "russisk", "uk": "ukrainsk", "fi": "finsk",
    "is": "islandsk", "fo": "færøysk", "zh": "kinesisk", "ja": "japansk",
    "ko": "koreansk", "ar": "arabisk", "pt": "portugisisk", "tr": "tyrkisk",
    "hi": "hindi", "jw": "javanesisk", "jv": "javanesisk",
}

_unmapped: set = set()


def lyd_label(label: str) -> str:
    """AudioSet label -> nynorsk (lowercased fallback, recorded as unmapped)."""
    key = label.lower()
    if key in LYD_NN:
        return LYD_NN[key]
    _unmapped.add(label)
    return key


def unmapped() -> list:
    return sorted(_unmapped)
