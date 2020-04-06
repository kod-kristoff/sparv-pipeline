"""Main Sparv package."""
from sparv.core import config
from sparv.core.registry import annotator
from sparv.util.classes import AllDocuments, Annotation, Binary, Config, Document, Export, ExportAnnotations, Model,\
    Output, Source

__all__ = [
    "annotator",
    "config",
    "AllDocuments",
    "Annotation",
    "Binary",
    "Config",
    "Document",
    "Export",
    "ExportAnnotations",
    "Model",
    "Output",
    "Source"
]
