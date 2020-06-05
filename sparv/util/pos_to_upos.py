"""Map different POS (or MSD) tags to simple Universal Depenendy POS (UPOS) tags.

http://universaldependencies.org/u/pos/all.html
"""

# Fallback POS
FALLBACK = "X"

# UD = {
#     "ADJ": "adjective",
#     "ADV": "adverb",
#     "INTJ": "interjection",
#     "NOUN": "noun",
#     "PROPN": "proper noun",
#     "VERB": "verb",
#     "ADP": "adposition",
#     "AUX": "auxiliary verb",
#     "CONJ": "coordinating conjunction",
#     "DET": "determiner",
#     "NUM": "numeral",
#     "PART": "particle",
#     "PRON": "pronoun",
#     "SCONJ": "subordinating conjunction",
#     "PUNCT": "punctuation",
#     "SYM": "symbol",
#     "X": "other"}


def convert_to_upos(pos, lang, tagset):
    """Map POS tags to Universal Depenendy POS tags."""
    if (lang, tagset) in CONVERTERS:
        lang_convert = CONVERTERS[(lang, tagset)]
        return lang_convert(pos)
    else:
        return ""


################################################################################
# SUC POS
################################################################################

def _swe_SUC_convert(pos):
    """Convert SUC tags to UPOS."""
    pos_dict = {
        "NN": "NOUN",
        "PM": "PROPN",
        "VB": "VERB",  # "AUX" ?
        "IE": "PART",
        "PC": "VERB",  # No ADJ?
        "PL": "PART",  # No ADV, ADP?
        "PN": "PRON",
        "PS": "DET",  # No PRON?
        "HP": "PRON",
        "HS": "DET",  # No PRON?
        "DT": "DET",
        "HD": "DET",
        "JJ": "ADJ",
        "AB": "ADV",
        "HA": "ADV",
        "KN": "CONJ",
        "SN": "SCONJ",
        "PP": "ADP",
        "RG": "NUM",
        "RO": "ADJ",  # No NUM?
        "IN": "INTJ",
        "UO": "X",  # Could be any PoS, most probably a noun /ljo
        "MAD": "PUNCT",
        "MID": "PUNCT",
        "PAD": "PUNCT"
    }
    return pos_dict.get(pos, FALLBACK)


################################################################################
# EAGLES/FreeLing
################################################################################

EAGLES_DICT = {
    "A": "ADJ",
    "CC": "CONJ",
    "CS": "SCONJ",
    "D": "DET",
    "F": "PUNCT",
    "I": "INTJ",
    "NC": "NOUN",
    "NP": "PROPN",
    "P": "PRON",
    "R": "ADV",
    "S": "ADP",
    "VM": "VERB",
    "VA": "AUX",
    "VS": "VERB",
    "VV": "VERB",
    "W": "NUM",
    "Z": "NUM",
    "Y": "X",
    "X": "X"
}


def _EAGLES_convert(pos):
    """Convert EAGLES tags to UPOS."""
    if pos[0] in "NVC":
        return EAGLES_DICT.get(pos[0:2], FALLBACK)
    else:
        return EAGLES_DICT.get(pos[0], FALLBACK)


def _rus_FreeLing_convert(pos):
    """Convert Russian FreeLing tags to UPOS."""
    pos_dict = {
        "A": "ADJ",
        "B": "ADP",
        "C": "CONJ",
        "D": "ADV",
        "E": "PRON",
        "J": "INTJ",
        "M": "X",
        "NC": "NOUN",
        "NP": "PROPN",
        "P": "ADV",
        "Y": "NUM",
        "R": "ADV",
        "T": "PART",
        "Q": "VERB",
        "Z": "NUM",
        "V": "VERB",
        "F": "PUNCT",
        "W": "NUM",
    }
    return pos_dict.get(pos[0], FALLBACK)


def _eng_Penn_convert(pos):
    """Convert from Penn Treebank tagset (with FreeLing modifications)."""
    # https://freeling-user-manual.readthedocs.io/en/latest/tagsets/tagset-en/
    # https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    pos_dict = {
        "CC": "CONJ",
        "DT": "DET",
        "EX": "PRON",
        "I": "INTJ",
        "IN": "ADP",
        "JJ": "ADJ",
        "JJR": "ADJ",
        "JJS": "ADJ",
        "MD": "VERB",
        "PDT": "DET",
        "POS": "ADP",
        "PRP": "PRON",
        "PRP$": "PRON",
        "RB": "ADV",
        "RBR": "ADV",
        "RBS": "ADV",
        "RP": "PART",
        "TO": "PART",
        "UH": "INTJ",
        "VB": "VERB",
        "VBD": "VERB",
        "VBG": "VERB",
        "VBN": "VERB",
        "VBP": "VERB",
        "VBZ": "VERB",
        "W": "NUM",
        "WDT": "DET",
        "WP": "PRON",
        "WP$": "PRON",
        "WRB": "ADV",
        "CD": "NUM",
        "FW": "X",
        "LS": "X",
        "SYM": "SYM"
    }
    if pos in ["NN", "NNS"]:
        return "NOUN"
    if pos.startswith("N"):
        return "PROPN"
    if pos == "FW":  # Foreign word in Penn Treebank tagset
        return "X"
    if pos.startswith("F"):
        return "PUNCT"
    if pos.startswith("Z"):
        return "NUM"
    return pos_dict.get(pos, FALLBACK)


################################################################################
# TreeTagger
################################################################################


def _bul_BulTreeBank_convert(pos):
    pos_dict = {
        # http://bultreebank.org/wp-content/uploads/2017/06/BTB-TR03.pdf
        "Nc": "NOUN",
        "Np": "PROPN",
        "A": "ADJ",
        "H": "PROPN",
        "P": "PRON",
        "M": "NUM",
        "Vp": "VERB",
        "Vn": "VERB",
        "Vx": "AUX",
        "Vy": "AUX",
        "Vi": "AUX",
        "D": "ADV",
        "Cc": "CONJ",
        "Cs": "SCONJ",
        "T": "PART",
        "R": "ADP",
        "I": "INTJ"
    }
    if pos[0] in ["N", "V", "C"]:
        return pos_dict.get(pos[0:2], FALLBACK)
    if pos.startswith("PT"):
        return "PUNCT"
    else:
        return pos_dict.get(pos[0], FALLBACK)


def _est_TreeTagger_convert(pos):
    pos_dict = {
        # http://www.cl.ut.ee/korpused/morfliides/seletus
        "S": "NOUN",
        "V": "VERB",
        "A": "ADJ",
        "G": "ADJ",
        "P": "PRON",
        "D": "ADV",
        "K": "ADP",
        "J. crd": "CONJ",
        "J. sub": "SCONJ",
        "N": "NUM",
        "I": "INTJ",
        "Y": "X",  # abbreviation
        "X": "ADV",
        "Z": "PUNCT",
        "T": "X"  # foreign
    }
    if "." in pos:
        pos = pos.split(".")[0]
        if pos == "J":
            return pos_dict.get(pos, FALLBACK)
        return pos_dict.get(pos.split(".")[0])
    else:
        return pos_dict.get(pos, FALLBACK)


def _fin_FinnTreeBank_convert(pos):
    pos_dict = {
        # http://www.ling.helsinki.fi/kieliteknologia/tutkimus/treebank/sources/FinnTreeBankManual.pdf
        # http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/finnish-tags.txt
        "Abbr": "X",  # abbreviation
        "Adp": "ADP",
        "Adv": "ADV",
        "Interj": "INTJ",
        "N": "NOUN",
        "Num": "NUM",
        "PrfPrc": "VERB",  # participle
        "Pron": "PRON",
        "PrsPrc": "VERB",  # participle
        "Punct": "PUNCT",
        "SENT": "PUNCT",
        "V": "VERB",
        "AgPcp": "VERB",  # participle
        "A": "ADJ",
        "CC": "CONJ",
        "CS": "SCONJ",
        "NON-TWOL": "X"  # unknown
    }
    if pos in pos_dict:
        return pos_dict[pos]
    else:
        return pos_dict.get(pos.split("_")[0], FALLBACK)


def _nld_TreeTagger_convert(pos):
    pos_dict = {
        # http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/dutch-tagset.txt
        "adj": "ADJ",
        "adv": "ADV",
        "con": "CONJ",
        "det": "DET",
        "int": "INTJ",
        "nou": "NOUN",
        "num": "NUM",
        "par": "PART",  # particle "te"
        "pre": "ADP",
        "pro": "PRON",
        "pun": "PUNCT",
        "ver": "VERB"
    }
    if len(pos) == 2 and pos.startswith("$."):
        return "PUNCT"
    elif pos == "pronadv":
        return "ADV"  # pronomial adverb
    elif pos == "det__art":
        return "DET"
    else:
        return pos_dict.get(pos[0:3], FALLBACK)


def _lat_TreeTagger_convert(pos):
    pos_dict = {
        # http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/Lamap-Tagset.pdf
        "ESSE": "AUX",
        "V": "VERB",
        "PRON": "PRON",
        "REL": "PRON",
        "POSS": "PRON",
        "DIMOS": "PRON",
        "INDEF": "PRON",
        "N": "NOUN",
        "NPR": "PROPN",
        "CC": "CONJ",
        "CS": "SCONJ",
        "ADJ": "ADJ",
        "ADV": "ADV",
        "PREP": "ADP",
        "INT": "INTJ",
        "ABBR": "X",  # abbreviation
        "EXCL": "INTJ",  # exclamations
        "FW": "X",  # foreign
        "SENT": "PUNCT",
        "PUN": "PUNCT",
        "SYM": "SYM",
        "CLI": "X"  # enclitics
    }
    if ":" in pos:
        return pos_dict.get(pos.split(":")[0], FALLBACK)
    else:
        return pos_dict.get(pos, FALLBACK)


def _pol_NationalCorpusofPolish_convert(pos):
    pos_dict = {
        # http://nkjp.pl/poliqarp/help/ense2.html
        "subst": "NOUN",
        "depr": "NOUN",  # depreciative form
        "num": "NUM",
        "numcol": "NUM",
        "adj": "ADJ",
        "adja": "ADJ",
        "adjp": "ADJ",
        "adjc": "ADJ",
        "adv": "ADV",
        "qub": "ADV",
        "ppron12": "PRON",
        "ppron3": "PRON",
        "siebie": "PRON",
        "fin": "VERB",
        "bedzie": "VERB",
        "inf": "VERB",
        "ger": "VERB",
        "aglt": "VERB",
        "praet": "PART",
        "pcon": "PART",
        "pant": "PART",
        "pact": "PART",
        "ppas": "PART",
        "impt": "VERB",  # imperative
        "imps": "VERB",  # impersonal
        "winien": "AUX",  # winien
        "pred": "ADJ",  # predicative
        "prep": "ADP",
        "conj": "CONJ",
        "comp": "SCONJ",
        "brev": "X",  # abbreviation
        "burk": "X",  # bound word
        "interj": "INTJ",
        "interp": "PUNCT",
        "SENT": "PUNCT",
        "xxx": "X",  # alien
        "ign": "X"  # unknown form
    }
    if ":" in pos:
        return pos_dict.get(pos.split(":")[0], FALLBACK)
    else:
        return pos_dict.get(pos, FALLBACK)


def _ron_MULTEXT_convert(pos):
    # http://nl.ijs.si/ME/V4/msd/tables/msd-human-ro.tbl
    pos_dict = {
        "Nc": "NOUN",
        "Np": "PROPN",
        "Vm": "VERB",
        "Va": "AUX",
        "A": "ADJ",
        "P": "PRON",
        "D": "DET",
        "T": "DET",
        "R": "ADV",
        "Sp": "ADP",
        "SE": "PUNCT",
        "Cc": "CONJ",
        "Cr": "CONJ",
        "Cs": "SCONJ",
        "CO": "PUNCT",
        "M": "NUM",
        "Q": "PART",
        "I": "INTJ",
        "Y": "X",  # abbreviation
        "X": "X"
    }
    if pos[0] in ["N", "V", "C", "S"]:
        return pos_dict.get(pos[0:2], FALLBACK)
    else:
        return pos_dict.get(pos[0], FALLBACK)


def _slk_SlovakNationalCorpus_convert(pos):
    pos_dict = {
        # http://korpus.juls.savba.sk/morpho_en.html
        "S": "NOUN",
        "A": "ADJ",
        "P": "PRON",
        "N": "NUM",
        "V": "VERB",
        "G": "PART",
        "D": "ADV",
        "E": "ADP",
        "O": "CONJ",  # conjunction
        "T": "PART",
        "J": "INTJ",
        "R": "X",  # reflexive morpheme
        "Y": "X",  # conditional morpheme
        "W": "SYM",  # abbreviation, symbol
        "Z": "PUNCT",
        "Q": "X",
        "#": "X",  # non-verbal element
        "%": "X",  # foreign language citation
        "0": "NUM",
        ":r": "PROPN",
        ":q": "X"  # incorrect spelling
    }
    if len(pos) == 1 and not pos.isalpha():
        return "PUNCT"
    elif pos.startswith(":"):
        return pos_dict.get(pos, FALLBACK)
    else:
        return pos_dict.get(pos[0], FALLBACK)


def _deu_STTS_convert(pos):
    pos_dict = {
        # http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/stts_guide.pdf
        "ADJA": "ADJ",
        "ADJD": "ADJ",
        "ADV": "ADV",
        "APPR": "ADP",
        "APPRART": "ADP",
        "APPO": "ADP",
        "APZR": "ADP",
        "ART": "DET",
        "CARD": "NUM",  # cardinal number
        "FM": "X",  # foreign word
        "ITJ": "INTJ",
        "ORD": "NUM",  # ordinal number
        "KOUI": "SCONJ",
        "KOUS": "SCONJ",
        "KON": "CONJ",
        "KOKOM": "CONJ",
        "NN": "NOUN",
        "NE": "PROPN",
        "PDS": "PRON",
        "PDAT": "PRON",
        "PIS": "PRON",
        "PIAT": "PRON",
        "PIDAT": "PRON",
        "PPER": "PRON",
        "PPOSS": "PRON",
        "PPOSAT": "PRON",
        "PRELS": "PRON",
        "PRELAT": "PRON",
        "PRF": "PRON",
        "PWS": "PRON",
        "PWAT": "PRON",
        "PWAV": "PRON",
        "PAV": "ADV",
        "PTKZU": "PART",  # infinitive marker 'zu'
        "PTKNEG": "PART",  # negation particle
        "PTKVZ": "PART",
        "PTKANT": "PART",
        "PTKA": "PART",
        "SGML": "X",  # SGML markup
        "SPELL": "X",  # spelling
        "TRUNC": "X",  # truncated word (first part)
        "VVFIN": "VERB",
        "VVIMP": "VERB",
        "VVINF": "VERB",
        "VVIZU": "VERB",
        "VVPP": "VERB",
        "VAFIN": "VERB",
        "VAIMP": "VERB",
        "VAINF": "VERB",
        "VAPP": "VERB",
        "VMFIN": "VERB",
        "VMINF": "VERB",
        "VMPP": "VERB",
        "XY": "SYM",  # non-word
        "$,": "PUNCT",
        "$.": "PUNCT",
        "$(": "PUNCT"
    }
    return pos_dict[pos]


def _fra_TreeTagger_convert(pos):
    pos_dict = {
        # https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/french-tagset.html
        "ABR": "X",  # abbreviation
        "ADJ": "ADJ",
        "ADV": "ADV",
        "DET": "DET",
        "INT": "INTJ",
        "KON": "CONJ",
        "NAM": "PROPN",
        "NOM": "NOUN",
        "NUM": "NUM",
        "PRO": "PRON",
        "PRP": "ADP",
        "PUN": "PUNCT",
        "SEN": "X",  # SENT: sentence tag
        "SYM": "SYM",
        "VER": "VERB"
    }
    if pos == "DET:POS":
        return "PRON"
    else:
        return pos_dict.get(pos[:3], "X")


def _spa_TreeTagger_convert(pos):
    pos_dict = {
        # https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/spanish-tagset.txt
        "ADJ": "ADJ",
        "ADV": "ADV",
        "ART": "DET",
        "CAR": "NUM",
        "CC": "CONJ",  # Coordinating conjunction (y, o)
        "CCA": "CONJ",  # Adversative coordinating conjunction (pero)
        "CCN": "CONJ",  # Negative coordinating conjunction (ni)
        "CQU": "SCONJ",  # que (as conjunction)
        "CSU": "SCONJ",
        "DM": "PRON",  # Demonstrative pronouns (ésas, ése, esta)
        "INT": "PRON",  # Interrogative pronouns (quiénes, cuántas, cuánto)
        "ITJ": "INTJ",
        "NC": "NOUN",  # Common nouns (mesas, mesa, libro, ordenador)
        "NME": "NOUN",  # measure noun (metros, litros)
        "NMO": "NOUN",  # month name
        "NP": "PROPN",
        "ORD": "DET",  # Ordinals (primer, primeras, primera)
        "PAL": "ADP",  # Portmanteau word formed by a and el
        "PDE": "ADP",  # Portmanteau word formed by de and el
        "PPC": "PRON",  # Clitic personal pronoun (le, les)
        "PPO": "PRON",  # Possessive pronouns (mi, su, sus)
        "PPX": "PRON",  # Clitics and personal pronouns (nos, me, nosotras, te, sí)
        "PRE": "ADP",
        "REL": "PRON",  # Relative pronouns (cuyas, cuyo)
        "SE": "PART",  # Se (as particle)
        "QU": "DET",  # Quantifiers (sendas, cada)
        "BAC": "SYM",  # backslash (\)
        "CM": "PUNCT",  # comma (,)
        "COL": "PUNCT",  # colon (:)
        "DAS": "PUNCT",  # dash (-)
        "DOT": "PUNCT",  # POS tag for "..."
        "FS": "PUNCT",  # Full stop punctuation marks
        "SYM": "SYM",
        "LP": "PUNCT",  # left parenthesis ("(", "[")
        "QT": "PUNCT",  # quotation symbol (" ' `)
        "RP": "PUNCT",  # right parenthesis (")", "]")
        "SEM": "PUNCT",  # semicolon (;)
        "SLA": "SYM",  # slash (/)
        "PER": "SYM",  # percent sign (%)
        # ACRNM	acronym (ISO, CEI)
        # ALFP	Plural letter of the alphabet (As/Aes, bes)
        # ALFS	Singular letter of the alphabet (A, b)
        # CODE	Alphanumeric code
        # PE	Foreign word
        # FO	Formula
        # PNC	Unclassified word
        # NEG	Negation
        # UMMX	measure unit (MHz, km, mA)
    }
    if pos.startswith("V"):
        return "VERB"
    return pos_dict.get(pos[:3], "X")


def _ita_TreeTagger_convert(pos):
    pos_dict = {
        # https://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/italian-tagset.txt
        "ADJ": "ADJ",
        "ADV": "ADV",
        "CON": "CONJ",  # conjunction
        "DET": "DET",
        "INT": "INTJ",  # interjection
        "LS": "SYM",  # list symbol
        "NOM": "NOUN",
        "NPR": "PROPN",
        "NUM": "NUM",
        "PON": "PUNCT",
        "PRE": "ADP",
        "PRO": "PRON",
        "SYM": "SYM",
        "VER": "VERB",
        # "ABR": "",  # abbreviation
        # "FW": "",  # foreign word
        # "SENT": "",  # sentence marker
    }
    return pos_dict.get(pos[:3], "X")


def _rus_TreeTagger_convert(pos):
    pos_dict = {
        # http://corpus.leeds.ac.uk/mocky/ru-table.tab
        "A": "ADJ",
        "C": "CONJ",
        "I": "INTJ",
        "M": "NUM",
        "N": "NOUN",
        "P": "PRON",
        "Q": "PART",
        "R": "ADV",
        "S": "ADP",
        "V": "VERB",
    }
    return pos_dict.get(pos[0], "X")


################################################################################
# Converter mapping
################################################################################


CONVERTERS = {
    # Swedish:
    ("swe", "SUC"): _swe_SUC_convert,
    # FreeLing:
    ("ast", "EAGLES"): _EAGLES_convert,
    ("cat", "EAGLES"): _EAGLES_convert,
    # ("cy", "EAGLES"): _EAGLES_convert,  # Welsh, Not used yet, FreeLing dict is not working.
    ("deu", "EAGLES"): _EAGLES_convert,
    ("spa", "EAGLES"): _EAGLES_convert,
    ("eng", "Penn"): _eng_Penn_convert,  # Also used by Stanford Parser
    ("fra", "EAGLES"): _EAGLES_convert,
    ("glg", "EAGLES"): _EAGLES_convert,
    ("ita", "EAGLES"): _EAGLES_convert,
    ("nob", "EAGLES"): _EAGLES_convert,
    ("por", "EAGLES"): _EAGLES_convert,
    ("rus", "EAGLES"): _rus_FreeLing_convert,
    ("slv", "EAGLES"): _EAGLES_convert,
    # TreeTagger:
    ("bul", "BulTreeBank"): _bul_BulTreeBank_convert,
    ("est", "TreeTagger"): _est_TreeTagger_convert,
    ("fin", "FinnTreeBank"): _fin_FinnTreeBank_convert,
    ("nld", "TreeTagger"): _nld_TreeTagger_convert,
    ("lat", "TreeTagger"): _lat_TreeTagger_convert,
    ("pol", "NationalCorpusofPolish"): _pol_NationalCorpusofPolish_convert,
    ("ron", "MULTEXT"): _ron_MULTEXT_convert,
    ("slk", "SlovakNationalCorpus"): _slk_SlovakNationalCorpus_convert,
    ("deu", "STTS"): _deu_STTS_convert,
    ("fra", "TreeTagger"): _fra_TreeTagger_convert,
    ("spa", "TreeTagger"): _spa_TreeTagger_convert,
    ("ita", "TreeTagger"): _ita_TreeTagger_convert,
    ("rus", "TreeTagger"): _rus_TreeTagger_convert,
}
