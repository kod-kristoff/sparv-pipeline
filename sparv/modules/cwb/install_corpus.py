"""Module for installing cwb binary files on remote host."""

import os
import re

from sparv.api import Config, Corpus, ExportInput, OutputCommonData, SparvErrorMessage, installer, util


@installer("Install CWB datafiles (for a corpus in its original order) on remote host")
def install_corpus(
        corpus: Corpus = Corpus(),
        out: OutputCommonData = OutputCommonData("cwb.install_corpus_original_marker"),
        host: str = Config("cwb.remote_host"),
        datadir: str = Config("cwb.cwb_datadir"),
        registry: str = Config("cwb.corpus_registry"),
        target_datadir: str = Config("cwb.remote_datadir"),
        target_registry: str = Config("cwb.remote_registry"),
        # The remaining arguments are needed by Snakemake
        original_marker: ExportInput = ExportInput("[cwb.cwb_datadir]/[metadata.id]/.original_marker",
                                                    absolute_path=True),
        info_file: ExportInput = ExportInput("[cwb.cwb_datadir]/[metadata.id]/.info", absolute_path=True),
        cwb_file: ExportInput = ExportInput("[cwb.corpus_registry]/[metadata.id]", absolute_path=True)):
    """Install CWB datafiles on server, by rsyncing datadir and registry."""
    sync_cwb(corpus=corpus, out=out, host=host, datadir=datadir, registry=registry, target_datadir=target_datadir,
             target_registry=target_registry)


@installer("Install CWB datafiles for a scrambled corpus on remote host")
def install_corpus_scrambled(
        corpus: Corpus = Corpus(),
        out: OutputCommonData = OutputCommonData("cwb.install_corpus_marker"),
        host: str = Config("cwb.remote_host"),
        datadir: str = Config("cwb.cwb_datadir"),
        registry: str = Config("cwb.corpus_registry"),
        target_datadir: str = Config("cwb.remote_datadir"),
        target_registry: str = Config("cwb.remote_registry"),
        # The remaining arguments are needed by Snakemake
        scrambled_marker: ExportInput = ExportInput("[cwb.cwb_datadir]/[metadata.id]/.scrambled_marker",
                                                    absolute_path=True),
        info_file: ExportInput = ExportInput("[cwb.cwb_datadir]/[metadata.id]/.info", absolute_path=True),
        cwb_file: ExportInput = ExportInput("[cwb.corpus_registry]/[metadata.id]", absolute_path=True)):
    """Install scrambled CWB datafiles on server, by rsyncing datadir and registry."""
    sync_cwb(corpus=corpus, out=out, host=host, datadir=datadir, registry=registry, target_datadir=target_datadir,
             target_registry=target_registry)

def sync_cwb(corpus, out, host, datadir, registry, target_datadir, target_registry):
    """Install CWB datafiles on server, by rsyncing datadir and registry."""
    if not corpus:
        raise SparvErrorMessage("Missing corpus name. Corpus not installed.")

    if not host:
        raise SparvErrorMessage("Configuration variable cwb.remote_host not set! Corpus not installed.")

    if not target_datadir:
        raise SparvErrorMessage("Configuration variable cwb.remote_datadir not set! Corpus not installed.")

    if not target_registry:
        raise SparvErrorMessage("Configuration variable cwb.remote_registry not set! Corpus not installed.")

    target = os.path.join(target_datadir, corpus)
    util.system.rsync(os.path.join(datadir, corpus), host, target)

    target_registry_file = os.path.join(target_registry, corpus)
    source_registry_file = os.path.join(registry, corpus + ".tmp")

    # Fix absolute paths in registry file
    with open(os.path.join(registry, corpus)) as registry_in:
        with open(source_registry_file, "w") as registry_out:
            for line in registry_in:
                if line.startswith("HOME"):
                    line = re.sub(r"HOME .*(/.+)", r"HOME " + target_datadir + r"\1", line)
                elif line.startswith("INFO"):
                    line = re.sub(r"INFO .*(/.+)/\.info", r"INFO " + target_datadir + r"\1/.info", line)

                registry_out.write(line)

    util.system.rsync(source_registry_file, host, target_registry_file)
    os.remove(source_registry_file)

    # Write marker file
    out.write("")