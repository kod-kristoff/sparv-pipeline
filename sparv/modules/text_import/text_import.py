"""Import module for plain text source files."""

import os
import unicodedata

from sparv import importer, util
from sparv.util.classes import Document, Source


@importer("TXT import", source_type="txt", outputs=["text"])
def parse(doc: str = Document,
          source_dir: str = Source,
          prefix: str = "",
          encoding: str = util.UTF8,
          normalize: str = "NFC") -> None:
    """Parse plain text file as input to the Sparv pipeline.

    Args:
        doc: The document name.
        source_dir: The source directory.
        prefix: Optional prefix for output annotation.
        encoding: Encoding of source file. Default is UTF-8.
        normalize: Normalize input text using any of the following forms: 'NFC', 'NFKC', 'NFD', and 'NFKD'.
            'NFC' is used by default.
    """
    # Source path
    if ":" in doc:
        doc, _, doc_chunk = doc.partition(":")
        source_file = os.path.join(source_dir, doc, doc_chunk + ".txt")
    else:
        source_file = os.path.join(source_dir, doc + ".txt")

    with open(source_file, encoding=encoding) as txt:
        text = txt.read()

    if normalize:
        text = unicodedata.normalize("NFC", text)

    util.write_corpus_text(doc, text)

    # Make up a text annotation surrounding the whole file
    text_annotation = "{}.text".format(prefix) if prefix else "text"
    util.write_annotation(doc, text_annotation, [(0, len(text))])
    util.write_data(doc, util.corpus.STRUCTURE_FILE, "")
