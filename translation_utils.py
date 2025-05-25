import re

char_map = {
    'ا': 'a', 'أ': 'a', 'إ': 'i', 'آ': 'aa',
    'ب': 'b', 'ت': 't', 'ث': 'th',
    'ج': 'j', 'ح': 'h', 'خ': 'kh',
    'د': 'd', 'ذ': 'dh', 'ر': 'r',
    'ز': 'z', 'س': 's', 'ش': 'sh',
    'ص': 's', 'ض': 'd', 'ط': 't',
    'ظ': 'z', 'ع': "'", 'غ': 'gh',
    'ف': 'f', 'ق': 'q', 'ك': 'k',
    'ل': 'l', 'م': 'm', 'ن': 'n',
    'ه': 'h', 'و': 'u',   # ← WAS 'w', but 'u' gives better results for place names
    'ي': 'i', 'ى': 'a',
    'ئ': 'i', 'ؤ': 'u', 'ء': "'", 'ة': 'a',
    'ﻻ': 'la', ' ': ' '
}

overrides_map = {
    'نابلس': 'Nablus'
}

def capitalize_name(name):
    return ' '.join(word.capitalize() for word in name.split())

def transliterate_arabic_name(text):
    if text in overrides_map:
        return overrides_map[text]
    translit = ''.join(char_map.get(c, c) for c in text)
    translit = re.sub(r"'+", "'", translit)  # collapse multiple apostrophes
    translit = re.sub(r'\s+', ' ', translit).strip()
    return capitalize_name(translit)

