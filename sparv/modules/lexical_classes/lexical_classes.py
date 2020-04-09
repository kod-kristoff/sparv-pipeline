"""Annotate words or documents with lexical classes from Blingbring or SweFN."""

import os
import subprocess
import sys
from collections import defaultdict
from typing import List

import sparv.util as util
from sparv import Annotation, Document, Model, annotator

# Path to the cwb binaries
CWB_SCAN_EXECUTABLE = "cwb-scan-corpus"
CWB_DESCRIBE_EXECUTABLE = "cwb-describe-corpus"
CORPUS_REGISTRY = os.environ.get("CORPUS_REGISTRY")


@annotator("Annotate tokens with Blingbring classes")
def annotate_bb_words(doc: str = Document,
                      out: str = Annotation("<token>:lexical_classes.blingbring"),
                      model: str = Model("[lexical_classes.bb_word_model=blingbring.pickle]"),
                      saldoids: str = Annotation("<token:sense>"),
                      pos: str = Annotation("<token:pos>"),
                      pos_limit: List[str] = ["NN", "VB", "JJ", "AB"],
                      class_set: str = "bring",
                      connect_ids: bool = False,
                      delimiter: str = util.DELIM,
                      affix: str = util.AFFIX,
                      scoresep: str = util.SCORESEP,
                      lexicon=None):
    """Blingbring specific wrapper for annotate_words. See annotate_words for more info."""
    # pos_limit="NN VB JJ AB" | None
    connect_ids = util.strtobool(connect_ids)

    if class_set not in ["bring", "roget_head", "roget_subsection", "roget_section", "roget_class"]:
        util.log.warning("Class '%s' not available. Fallback to 'bring'.")
        class_set = "bring"

    # Blingbring annotation function
    def annotate_bring(saldo_ids, lexicon, connect_IDs=False, scoresep=util.SCORESEP):
        rogetid = set()
        if saldo_ids:
            for sid in saldo_ids:
                if connect_IDs:
                    rogetid = rogetid.union(set(i + scoresep + sid for i in lexicon.lookup(sid, default=set())))
                else:
                    rogetid = rogetid.union(lexicon.lookup(sid, default=dict()).get(class_set, set()))
        return sorted(rogetid)

    annotate_words(doc, out, model, saldoids, pos, annotate_bring, pos_limit=pos_limit, class_set=class_set,
                   connect_ids=connect_ids, delimiter=delimiter, affix=affix, scoresep=scoresep, lexicon=lexicon)


def annotate_swefn_words(doc, out, model, saldoids, pos, pos_limit="NN VB JJ AB", disambiguate=True, connect_ids=False,
                         delimiter=util.DELIM, affix=util.AFFIX, scoresep=util.SCORESEP, lexicon=None):
    """SweFN specific wrapper for annotate_words. See annotate_words for more info."""
    disambiguate = util.strtobool(disambiguate)
    connect_ids = util.strtobool(connect_ids)

    # SweFN annotation function
    def annotate_swefn(saldo_ids, lexicon, connect_IDs=False, scoresep=util.SCORESEP):
        swefnid = set()
        if saldo_ids:
            for sid in saldo_ids:
                if connect_IDs:
                    swefnid = swefnid.union(set(i + scoresep + sid for i in lexicon.lookup(sid, default=set())))
                else:
                    swefnid = swefnid.union(lexicon.lookup(sid, default=set()))
        return sorted(swefnid)

    annotate_words(doc, out, model, saldoids, pos, annotate_swefn, pos_limit=pos_limit, disambiguate=disambiguate,
                   connect_ids=connect_ids, delimiter=delimiter, affix=affix, scoresep=scoresep, lexicon=lexicon)


def annotate_words(doc, out, model, saldoids, pos, annotate, pos_limit, class_set=None, disambiguate=True,
                   connect_ids=False, delimiter=util.DELIM, affix=util.AFFIX, scoresep=util.SCORESEP, lexicon=None):
    """
    Annotate words with blingbring classes (rogetID).

    - out_sent: resulting annotation file.
    - model: pickled lexicon with saldoIDs as keys.
    - saldoids, pos: existing annotation with saldoIDs/parts of speech.
    - annotate: annotation function, returns an iterable containing annotations
        for one token ID. (annotate_bring() or annotate_swefn())
    - pos_limit: parts of speech that will be annotated.
        Set to None to annotate all pos.
    - class_set: output Bring classes or Roget IDs ("bring", "roget_head",
        "roget_subsection", "roget_section" or "roget_class").
        Set to None when not annotating blingbring.
    - disambiguate: use WSD and use only the most likely saldo ID.
    - connect_IDs: for sweFN: paste saldo ID after each sweFN ID.
    - delimiter: delimiter character to put between ambiguous results
    - affix: optional character to put before and after results to mark a set.
    - lexicon: this argument cannot be set from the command line,
      but is used in the catapult. This argument must be last.
    """
    if not lexicon:
        lexicon = util.PickledLexicon(model)
    # Otherwise use pre-loaded lexicon (from catapult)

    if pos_limit.lower() == "none":
        pos_limit = None

    sense = util.read_annotation(doc, saldoids)
    token_pos = list(util.read_annotation(doc, pos))
    out_annotation = util.create_empty_attribute(doc, token_pos)

    for token_index, token_sense in enumerate(sense):

        # Check if part of speech of this token is allowed
        if not pos_ok(token_pos, token_index, pos_limit):
            saldo_ids = None
            out_annotation[token_index] = affix
            continue

        if util.SCORESEP in token_sense:  # WSD
            ranked_saldo = token_sense.strip(util.AFFIX).split(util.DELIM) \
                if token_sense != util.AFFIX else None
            saldo_tuples = [(i.split(util.SCORESEP)[0], i.split(util.SCORESEP)[1]) for i in ranked_saldo]

            if not disambiguate:
                saldo_ids = [i[0] for i in saldo_tuples]

            # Only take the most likely analysis into account.
            # Handle wsd with equal probability for several words
            else:
                saldo_ids = [saldo_tuples[0]]
                del saldo_tuples[0]
                while saldo_tuples and (saldo_tuples[0][1] == saldo_ids[0][1]):
                    saldo_ids = [saldo_tuples[0]]
                    del saldo_tuples[0]

                saldo_ids = [i[0] for i in saldo_ids]

        else:  # No WSD
            saldo_ids = token_sense.strip(util.AFFIX).split(util.DELIM) \
                if token_sense != util.AFFIX else None

        result = annotate(saldo_ids, lexicon, connect_ids, scoresep)
        out_annotation[token_index] = util.cwbset(result, delimiter, affix) if result else affix
    util.write_annotation(doc, out, out_annotation)


def pos_ok(token_pos, token_index, pos_limit):
    """If there is a pos_limit, check if token has correct part of speech. Pass all tokens otherwise."""
    if pos_limit:
        return token_pos[token_index] in pos_limit.split()
    else:
        return True


def annotate_doc(doc, out, in_token_annotation, text, token, saldoids=None, cutoff=3, types=False,
                 delimiter=util.DELIM, affix=util.AFFIX, freq_model=None, decimals=3):
    """
    Annotate documents with lexical classes.

    - out: resulting annotation file
    - in_token_annotation: existing annotation with lexical classes on token level.
    - text, token: existing annotations for the text-IDs and the tokens.
    - saldoids: existing annotation with saldoIDs, needed when types=True.
    - cutoff: value for limiting the resulting bring classes.
              The result will contain all words with the top x frequencies.
              Words with frequency = 1 will be removed from the result.
    - types: if True, count every class only once per saldo ID occurrence.
    - delimiter: delimiter character to put between ambiguous results.
    - affix: optional character to put before and after results to mark a set.
    - freq_model: pickled file with reference frequencies.
    - decimals: number of decimals to keep in output.
    """
    cutoff = int(cutoff)
    types = util.strtobool(types)
    text_children, orphans = util.get_children(doc, text, token, preserve_parent_annotation_order=True)
    classes = list(util.read_annotation(doc, in_token_annotation))
    sense = list(util.read_annotation(doc, saldoids)) if types else None

    if freq_model:
        freq_model = util.PickledLexicon(freq_model)

    out_annotation = util.create_empty_attribute(doc, text)

    for text_index, words in enumerate(text_children):
        seen_types = set()
        class_freqs = defaultdict(int)

        for token_index in words:
            # Count only sense types
            if types:
                senses = str(sorted([s.split(util.SCORESEP)[0] for s in sense[token_index].strip(util.AFFIX).split(util.DELIM)]))
                if senses in seen_types:
                    continue
                else:
                    seen_types.add(senses)

            rogwords = classes[token_index].strip(util.AFFIX).split(util.DELIM) if classes[token_index] != util.AFFIX else []
            for w in rogwords:
                class_freqs[w] += 1

        if freq_model:
            for c in class_freqs:
                # Relative frequency
                rel = class_freqs[c] / len(words)
                # Calculate class dominance
                ref_freq = freq_model.lookup(c.replace("_", " "), 0)
                if not ref_freq:
                    util.log.error("Class '%s' is missing" % ref_freq)
                class_freqs[c] = (rel / ref_freq)

        # Sort words according to frequency/dominance
        ordered_words = sorted(class_freqs.items(), key=lambda x: x[1], reverse=True)
        if freq_model:
            # Remove words with dominance < 1
            ordered_words = [w for w in ordered_words if w[1] >= 1]
        else:
            # Remove words with frequency 1
            ordered_words = [w for w in ordered_words if w[1] > 1]

        if len(ordered_words) > cutoff:
            cutoff_freq = ordered_words[cutoff - 1][1]
            ordered_words = [w for w in ordered_words if w[1] >= cutoff_freq]

        # Join words and frequencies/dominances
        ordered_words = [util.SCORESEP.join([word, str(round(freq, decimals))]) for word, freq in ordered_words]
        out_annotation[text_index] = util.cwbset(ordered_words, delimiter, affix) if ordered_words else affix

    util.write_annotation(doc, out, out_annotation)


def read_blingbring(tsv="blingbring.txt", classmap="rogetMap.xml", verbose=True):
    """Read the tsv version of the Blingbring lexicon (blingbring.xml).

    Return a lexicon dictionary: {senseid: {roget_head: roget_head,
                                            roget_subsection: roget_subsection,
                                            roget_section: roget_section,
                                            roget_class: roget_class,
                                            bring: bring_ID}
    """
    rogetdict = read_rogetmap(xml=classmap, verbose=True)

    import csv

    if verbose:
        util.log.info("Reading tsv lexicon")
    lexicon = {}
    classmapping = {}

    with open(tsv) as f:
        for line in csv.reader(f, delimiter="\t"):
            if line[0].startswith("#"):
                continue
            rogetid = line[1].split("/")[-1]
            if rogetid in rogetdict:
                roget_l3 = rogetdict[rogetid][0]  # subsection
                roget_l2 = rogetdict[rogetid][1]  # section
                roget_l1 = rogetdict[rogetid][2]  # class
            else:
                roget_l3 = roget_l2 = roget_l1 = ""
            senseids = set(line[3].split(":"))
            for senseid in senseids:
                lexicon.setdefault(senseid, set()).add((rogetid, roget_l3, roget_l2, roget_l1))

            # Make mapping between Roget and Bring classes
            if line[0].split("/")[1] == "B":
                classmapping[rogetid] = line[2]

    for senseid, rogetids in lexicon.items():
        roget_head = set([tup[0] for tup in rogetids])
        roget_subsection = set([tup[1] for tup in rogetids if tup[1]])
        roget_section = set([tup[2] for tup in rogetids if tup[2]])
        roget_class = set([tup[3] for tup in rogetids if tup[3]])
        lexicon[senseid] = {"roget_head": roget_head,
                            "roget_subsection": roget_subsection,
                            "roget_section": roget_section,
                            "roget_class": roget_class,
                            "bring": set([classmapping[r] for r in roget_head])}

    testwords = ["fågel..1",
                 "behjälplig..1",
                 "köra_ner..1"
                 ]
    util.test_annotations(lexicon, testwords)

    if verbose:
        util.log.info("OK, read")
    return lexicon


def read_rogetmap(xml="roget_hierarchy.xml", verbose=True):
    """Parse Roget map (Roget hierarchy) into a dictionary with Roget head words as keys."""
    import xml.etree.ElementTree as cet
    if verbose:
        util.log.info("Reading XML lexicon")
    lexicon = {}
    context = cet.iterparse(xml, events=("start", "end"))
    context = iter(context)
    event, root = next(context)

    for event, elem in context:
        if elem.tag == "class":
            l1 = elem.get("name")
        elif elem.tag == "section":
            l2 = elem.get("name")
        elif elem.tag == "subsection":
            l3 = elem.get("name")
        elif elem.tag == "headword":
            head = elem.get("name")
            lexicon[head] = (l3, l2, l1)

    testwords = ["Existence",
                 "Health",
                 "Amusement",
                 "Marriage"]
    util.test_annotations(lexicon, testwords)

    if verbose:
        util.log.info("OK, read.")
    return lexicon


def read_swefn(xml='swefn.xml', verbose=True):
    """Read the XML version of the swedish Framenet resource.

    Return a lexicon dictionary, {saldoID: {swefnID}}.
    """
    import xml.etree.ElementTree as cet
    if verbose:
        util.log.info("Reading XML lexicon")
    lexicon = {}

    context = cet.iterparse(xml, events=("start", "end"))  # "start" needed to save reference to root element
    context = iter(context)
    event, root = next(context)

    for event, elem in context:
        if event == "end":
            if elem.tag == 'LexicalEntry':
                sense = elem.find("Sense")
                sid = sense.get("id").lstrip("swefn--")
                for lu in sense.findall("feat[@att='LU']"):
                    saldosense = lu.get("val")
                    lexicon.setdefault(saldosense, set()).add(sid)

            # Done parsing section. Clear tree to save memory
            if elem.tag in ['LexicalEntry', 'frame', 'resFrame']:
                root.clear()

    testwords = ["slant..1",
                 "befrielse..1",
                 "granne..1",
                 "sisådär..1",
                 "mjölkcentral..1"]
    util.test_annotations(lexicon, testwords)

    if verbose:
        util.log.info("OK, read.")
    return lexicon


def blingbring_to_pickle(tsv, classmap, filename, protocol=-1, verbose=True):
    """Read blingbring tsv dictionary and save as a pickle file."""
    lexicon = read_blingbring(tsv, classmap)
    util.lexicon_to_pickle(lexicon, filename)


def swefn_to_pickle(xml, filename, protocol=-1, verbose=True):
    """Read sweFN xml dictionary and save as a pickle file."""
    lexicon = read_swefn(xml)
    util.lexicon_to_pickle(lexicon, filename)


def create_freq_pickle(corpus, annotation, filename, model, class_set=None, score_separator=util.SCORESEP):
    """Build pickle with relative frequency for a given annotation in one or more reference corpora."""
    lexicon = util.PickledLexicon(model)
    # Create a set of all possible classes
    if class_set:
        all_classes = set(cc for c in lexicon.lexicon.values() for cc in c[class_set])
    else:
        all_classes = set(cc for c in lexicon.lexicon.values() for cc in c)
    lexicon_size = len(all_classes)
    smoothing = 0.1

    corpus_stats = defaultdict(int)
    corpus_size = 0

    if isinstance(corpus, str):
        corpus = corpus.split()

    for c in corpus:
        # Get corpus size
        process = subprocess.Popen([CWB_DESCRIBE_EXECUTABLE, "-r", CORPUS_REGISTRY, c],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        reply, error = process.communicate()
        reply = reply.decode()

        if error:
            error = error.decode()
            util.log.error(error)
            sys.exit(1)

        for line in reply.splitlines():
            if line.startswith("size (tokens)"):
                _, size = line.split(":")
                corpus_size += int(size.strip())

        # Get frequency of annotation
        util.log.info("Getting frequencies from %s", c)
        process = subprocess.Popen([CWB_SCAN_EXECUTABLE, "-r", CORPUS_REGISTRY, c] + [annotation],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        reply, error = process.communicate()
        reply = reply.decode()
        if error:
            error = error.decode()
            if "Error:" in error:  # We always get something back on stderror from cwb-scan-corpus, so we must check if it really is an error
                if "Error: can't open attribute" in error:
                    util.log.error("Annotation '%s' not found", annotation)
                    sys.exit(1)

        for line in reply.splitlines():
            if not line.strip():
                continue
            freq, classes = line.split("\t")
            for cl in classes.split("|"):
                if cl:
                    freq = int(freq)
                    if score_separator:
                        cl, score = cl.rsplit(score_separator, 1)
                        score = float(score)
                        if score <= 0:
                            continue
                        freq = freq * score
                    corpus_stats[cl.replace("_", " ")] += freq

    rel_freq = defaultdict(float)

    for cl in all_classes:
        cl = cl.replace("_", " ")
        rel_freq[cl] = (corpus_stats[cl] + smoothing) / (corpus_size + smoothing * lexicon_size)

    util.lexicon_to_pickle(rel_freq, filename)


if __name__ == '__main__':
    util.run.main(annotate_bb_words=annotate_bb_words,
                  annotate_doc=annotate_doc,
                  blingbring_to_pickle=blingbring_to_pickle,
                  annotate_swefn_words=annotate_swefn_words,
                  swefn_to_pickle=swefn_to_pickle,
                  create_freq_pickle=create_freq_pickle
                  )
