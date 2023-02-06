"""Main Sparv executable."""

import argparse
import enum
import sys
from pathlib import Path
from typing import Optional

import pydantic
import typer

from sparv import __version__
from sparv.core import paths


# Check Python version
if sys.version_info < (3, 6, 2):
    raise Exception("Python 3.6.2 or higher is required.")


APP_NAME = "Sparv Pipline"

app = typer.Typer(rich_markup_mode="rich")


def version_callback(value: bool):
    if value:
        print(f"Sparv Pipeline v{__version__}")
        raise typer.Exit()


class LogLevel(str, enum.Enum):
    Debug = "debug"
    Info = "info"
    Warning = "warning"
    Error = "error"
    Critical = "critical"



class CustomArgumentParser(argparse.ArgumentParser):
    """ArgumentParser with custom help message and better handling of misspelled commands."""

    def __init__(self, *args, **kwargs):
        """Init parser."""
        no_help = kwargs.pop("no_help", False)
        # Don't add default help message
        kwargs["add_help"] = False
        super().__init__(*args, **kwargs)
        # Add our own help message unless the (sub)parser is created with the no_help argument
        if not no_help:
            self.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    def _check_value(self, action, value):
        """Check if command is valid, and if not, try to guess what the user meant."""
        if action.choices is not None and value not in action.choices:
            # Check for possible misspelling
            import difflib
            close_matches = difflib.get_close_matches(value, action.choices, n=1)
            if close_matches:
                message = f"unknown command: '{value}' - maybe you meant '{close_matches[0]}'"
            else:
                choices = ", ".join(map(repr, action.choices))
                message = f"unknown command: '{value}' (choose from {choices})"
            raise argparse.ArgumentError(action, message)


class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom help formatter for argparse, silencing subparser lists."""

    def _format_action(self, action):
        result = super()._format_action(action)
        if isinstance(action, argparse._SubParsersAction):
            return ""
        return result


def check_sparv_is_set_up():
    print("check_sparv_is_set_up")
    return
    
    # Make sure that Sparv data dir is set
    if not paths.get_data_path():
        print(f"The path to Sparv's data directory needs to be configured, either by running 'sparv setup' or by "
              f"setting the environment variable '{paths.data_dir_env}'.")
        sys.exit(1)

    # Check if Sparv data dir is outdated (or not properly set up yet)
    version_check = setup.check_sparv_version()
    if version_check is None:
        print("The Sparv data directory has been configured but not yet set up completely. Run 'sparv setup' to "
              "complete the process.")
        sys.exit(1)
    elif not version_check:
        print("Sparv has been updated and Sparv's data directory may need to be upgraded. Please run the "
              "'sparv setup' command.")
        sys.exit(1)


def check_config_exists(dir: Path) -> None:
    print(f"check_config_exists({dir=})")
    return
    if not corpus_config_exists(dir):
        print(f"No config file ({paths.config_file}) found in working directory ({dir}).")
        sys.exit(1)
    

def corpus_config_exists(dir: Path) -> bool:
    """Check that a corpus config file is available in the working dir"""
    try:
        config_exists = Path(dir, paths.config_file).is_file()
    except PermissionError as e:
        print(f"{e.strerror}: {e.filename!r}", file=sys.stderr)
        sys.exit(1)
    return config_exists


@app.callback()
def set_app_context(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "-v", "--version",
        callback=version_callback,
        is_eager=True,
        help="Show Sparv's version number and exit"
        ),
    dir: Optional[Path] = typer.Option(None,"-d", "--dir", help="Specify corpus directory", show_default="CWD")
):
    """Sparv Pipeline"""
    print(f"{ctx.invoked_subcommand=}")
    print(f"{ctx.params=}")
    ctx.obj = {
        "dir": dir,
        "corpus_dir": dir or Path.cwd(),
    }

    
def main():
    """Run Sparv Pipeline (main entry point for Sparv)."""

    # Set up command line arguments
    parser = CustomArgumentParser(prog="sparv",
                                  description="Sparv Pipeline",
                                  allow_abbrev=False,
                                  formatter_class=CustomHelpFormatter)
    description = [
        "",
        "Annotating a corpus:",
        "   run              Annotate a corpus and generate export files",
        "   install          Install a corpus",
        "   uninstall        Uninstall a corpus",
        "   clean            Remove output directories",
        "",
        "Inspecting corpus details:",
        "   config           Display the corpus config",
        "   files            List available corpus source files (input for Sparv)",
        "",
        "Show annotation info:",
        "   modules          List available modules and annotations",
        "   presets          List available annotation presets",
        "   classes          List available annotation classes",
        "   languages        List supported languages",
        "",
        "Setting up the Sparv Pipeline:",
        "   setup            Set up the Sparv data directory",
        "   wizard           Run config wizard to create a corpus config",
        "   build-models     Download and build the Sparv models (optional)",
        "",
        "Advanced commands:",
        "   run-rule         Run specified rule(s) for creating annotations",
        "   create-file      Create specified file(s)",
        "   run-module       Run annotator module independently",
        "   preload          Preload annotators and models",
        "",
        "See 'sparv <command> -h' for help with a specific command",
        "For full documentation, visit https://spraakbanken.gu.se/sparv/docs/"
    ]
    subparsers = parser.add_subparsers(dest="command", title="commands", metavar="<command>",
                                       description="\n".join(description))
    subparsers.required = True

# Annotate
@app.command(rich_help_panel="Annotating a corpus")
def run(
    ctx: typer.Context,
    output: list[str] = typer.Argument(None, help="The type of output format to generate"),
    show_output_format: bool = typer.Option(False,"-l", "--list", help="List available output formats"),
    files: list[Path] = typer.Option(None, "-f", "--file", help="Only annotate specified input file(s)"),
    dry_run: bool = typer.Option(False, "-n", "--dry-run", help="Print summary of tasks without running them"),
    num_cores: int = typer.Option(0, "-j", "--cores", metavar="N", help="Use at most N cores in parallel; if N is omitted, use all available CPU cores"),
    keep_going: bool = typer.Option(False, "-k", "--keep-going", help="Keep going with independent tasks if a task fails"),
    log_level: LogLevel = typer.Option("warning", "--log", metavar="LOGLEVEL", help="Set the log level"),
    file_log_level: LogLevel = typer.Option("warning", "--log-to-file", metavar="LOGLEVEL", help="Set log level for logging to file"),
    show_stats: bool = typer.Option(False, "--stats", help="Show summary of time spent per annotator"),
    show_debug: bool = typer.Option(False, "--debug", help="Show debug messages"),
    socket: Optional[Path] = typer.Option(None, "--socket", help="Path to socket file created by the 'preload' command"),
    force_preloader: bool = typer.Option(False, "--force-preloader", help="Try to wait for preloader when it's busy"),
    show_simple: bool = typer.Option(False, "--simple", help="Show less details while running"),
    unlock_work_dir: bool = typer.Option(False, "--unlock", help="Unlock the working directory"),
    mark_complete: list[Path] = typer.Option(None, "--mark-complete", metavar="FILE", help="Mark output files as complete"),
    rerun_incomplete: bool = typer.Option(False, "--rerun-incomplete", help="Rerun incomplete output files"),
):
    """Annotate a corpus and generate export files."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])
    config, snakemake_args = create_config_and_snakemake_args(
        command=ctx.command.name,
        dir=ctx.obj["corpus_dir"],
        cores=num_cores,
    )

    run_cfg = RunCfg()
    assert config == run_cfg.dict()
    
    run_args = RunArgs(
        workdir=ctx.obj["corpus_dir"]
    )
    assert snakemake_args == run_args.dict()


@app.command(rich_help_panel="Annotating a corpus")
def install(
    ctx: typer.Context,
    type: list[str] = typer.Argument(None, help="The type of installation to perform"),
    show_installations: bool = typer.Option(False, "-l", "--list", help="List installations to be made"),
    dry_run: bool = typer.Option(False, "-n", "--dry-run", help="Print summary of tasks without running them"),
    num_cores: int = typer.Option(0, "-j", "--cores", metavar="N", help="Use at most N cores in parallel; if N is omitted, use all available CPU cores"),
    keep_going: bool = typer.Option(False, "-k", "--keep-going", help="Keep going with independent tasks if a task fails"),
    log_level: LogLevel = typer.Option("warning", "--log", metavar="LOGLEVEL", help="Set the log level"),
    file_log_level: LogLevel = typer.Option("warning", "--log-to-file", metavar="LOGLEVEL", help="Set log level for logging to file"),
    show_stats: bool = typer.Option(False, "--stats", help="Show summary of time spent per annotator"),
    show_debug: bool = typer.Option(False, "--debug", help="Show debug messages"),
    socket: Optional[Path] = typer.Option(None, "--socket", help="Path to socket file created by the 'preload' command"),
    force_preloader: bool = typer.Option(False, "--force-preloader", help="Try to wait for preloader when it's busy"),
    show_simple: bool = typer.Option(False, "--simple", help="Show less details while running"),
):
    """Install a corpus."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])


@app.command(rich_help_panel="Annotating a corpus")
def uninstall(
    ctx: typer.Context,
    type: list[str] = typer.Argument(None, help="The type of uninstallation to perform"),
    show_uninstallations: bool = typer.Option(False, "-l", "--list", help="List uninstallations to be made"),
    dry_run: bool = typer.Option(False, "-n", "--dry-run", help="Print summary of tasks without running them"),
    num_cores: int = typer.Option(0, "-j", "--cores", metavar="N", help="Use at most N cores in parallel; if N is omitted, use all available CPU cores"),
    keep_going: bool = typer.Option(False, "-k", "--keep-going", help="Keep going with independent tasks if a task fails"),
    log_level: LogLevel = typer.Option("warning", "--log", metavar="LOGLEVEL", help="Set the log level"),
    file_log_level: LogLevel = typer.Option("warning", "--log-to-file", metavar="LOGLEVEL", help="Set log level for logging to file"),
    show_stats: bool = typer.Option(False, "--stats", help="Show summary of time spent per annotator"),
    show_debug: bool = typer.Option(False, "--debug", help="Show debug messages"),
    socket: Optional[Path] = typer.Option(None, "--socket", help="Path to socket file created by the 'preload' command"),
    force_preloader: bool = typer.Option(False, "--force-preloader", help="Try to wait for preloader when it's busy"),
    show_simple: bool = typer.Option(False, "--simple", help="Show less details while running"),
):
    """Uninstall a corpus."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])


@app.command(rich_help_panel="Annotating a corpus")
def clean(
    ctx: typer.Context,
    remove_export: bool = typer.Option(False, "-e", "--export", help="Remove export directory"),
    remove_logs: bool = typer.Option(False, "-l", "--logs", help="Remove logs directory"),
    remove_all: bool = typer.Option(False, "-a", "--all", help="Remove workdir, export and logs directories"),
):
    """Remove output directories (by default only the sparv-workdir directory)."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])


# Inspect
@app.command(name="config", rich_help_panel="Inspecting corpus details")    
def display_config(
    ctx: typer.Context,
    options: list[str] = typer.Argument(None, help="Specific options(s) in config to display"),
):
    """Display the corpus configuration."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])
    
    config, snakemake_args = create_config_and_snakemake_args(
        command=ctx.command.name,
        dir=ctx.obj["corpus_dir"],
        options=options,
    )

    display_config_cfg = DisplayConfigCfg(
        options=options or None,
    )
    assert config == display_config_cfg.dict(exclude_none=True)
    
    display_config_args = DisplayConfigArgs(
        workdir=ctx.obj["corpus_dir"]
    )
    assert snakemake_args == display_config_args.dict()


@app.command(rich_help_panel="Inspecting corpus details:")    
def files(
    ctx: typer.Context,
):
    """List available corpus source files (input for Sparv)
    
    List available corpus source files that can be annotated by Sparv."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])
    config, snakemake_args = create_config_and_snakemake_args(
        command=ctx.command.name,
        dir=ctx.obj["corpus_dir"],
    )

    files_cfg = DefaultCfg()
    assert config == files_cfg.dict()
    
    files_args = FilesArgs(
        workdir=ctx.obj["corpus_dir"]
    )
    assert snakemake_args == files_args.dict()


# Annotation info
@app.command(rich_help_panel="Show annotation info")
def modules(
    ctx: typer.Context,
    list_annotators: bool = typer.Option(False, "--annotators", help="List info for annotators"),
    list_importers: bool = typer.Option(False, "--importers", help="List info for importers"),
    list_exporters: bool = typer.Option(False, "--exporters", help="List info for exporters"),
    list_installers: bool = typer.Option(False, "--installers", help="List info for installers"),
    list_uninstallers: bool = typer.Option(False, "--uninstallers", help="List info for uninstallers"),
    list_all: bool = typer.Option(False, "--all", help="List info for all module types"),
    names: list[str] = typer.Argument(None, help="Specific module(s) to display"),
):
    """List available modules and annotations."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])

    types = []
    if list_annotators:
        types.append("annotators")
    if list_importers:
        types.append("importers")
    if list_exporters:
        types.append("exporters")
    if list_installers:
        types.append("installers")
    if list_uninstallers:
        types.append("uninstallers")
    if list_all:
        types.append("all")
    
    config, snakemake_args = create_config_and_snakemake_args(
        command=ctx.command.name,
        dir=ctx.obj["corpus_dir"],
        names=names,
        types=types,
    )

    modules_cfg = ModulesCfg(
        types=types,
        names=names,
    )
    assert config == modules_cfg.dict()
    
    modules_args = ModulesArgs(
        workdir=ctx.obj["corpus_dir"]
    )
    assert snakemake_args == modules_args.dict()


@app.command(rich_help_panel="Show annotation info")
def presets(
    
    ctx: typer.Context,
):
    """Display all available annotation presets."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])

    
@app.command(rich_help_panel="Show annotation info")
def classes(
    
    ctx: typer.Context,
):
    """Display all available annotation classes."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])

    
@app.command(rich_help_panel="Show annotation info")
def languages():
    """List supported languages."""
    
    check_sparv_is_set_up()


# Setup
@app.command(rich_help_panel="Setting up the Sparv Pipeline")
def setup(
    dir: Optional[Path] = typer.Option(None, "-d", "--dir", help="Directory to use as Sparv data directory", show_default="choosen interactively"),
    reset: bool = typer.Option(False, "--reset", help="Reset data directory setting."),
):
    """Set up the Sparv data directory. 
    
    Run without arguments for interactive setup."""
    
    if reset:
        print("setup.reset()")
    else:
        print(f"setup.run({dir})")
    sys.exit(0)


@app.command(rich_help_panel="Setting up the Sparv Pipeline")
def build_models(
    ctx: typer.Context,
    model: list[str] = typer.Argument(None, help="The model(s) to be built"),
    list_models: bool = typer.Option(False, "-l", "--list", help="List available models"),
    language: Optional[str] = typer.Option(None, "--language", help="Language (ISO 639-3) if different from current corpus language"),
    build_all: bool = typer.Option(False, "--all", help="Build all models for the current language"),
    dry_run: bool = typer.Option(False, "-n", "--dry-run", help="Print summary of tasks without running them"),
    num_cores: int = typer.Option(0, "-j", "--cores", metavar="N", help="Use at most N cores in parallel; if N is omitted, use all available CPU cores"),
    keep_going: bool = typer.Option(False, "-k", "--keep-going", help="Keep going with independent tasks if a task fails"),
    log_level: LogLevel = typer.Option("warning", "--log", metavar="LOGLEVEL", help="Set the log level"),
    file_log_level: LogLevel = typer.Option("warning", "--log-to-file", metavar="LOGLEVEL", help="Set log level for logging to file"),
    show_stats: bool = typer.Option(False, "--stats", help="Show summary of time spent per annotator"),
    show_debug: bool = typer.Option(False, "--debug", help="Show debug messages"),
    socket: Optional[Path] = typer.Option(None, "--socket", help="Path to socket file created by the 'preload' command"),
    force_preloader: bool = typer.Option(False, "--force-preloader", help="Try to wait for preloader when it's busy"),
    show_simple: bool = typer.Option(False, "--simple", help="Show less details while running"),
):
    """Download and build the Sparv models (optional)
    
    Download and build the Sparv models. This is optional, as 
    models will be downloaded and built automatically the first 
    time they are needed."""
    
    check_sparv_is_set_up()

    if not corpus_config_exists(ctx.obj["corpus_dir"]) and not language:
        print("Models are built for a specific language. Please provide one with the --language param or run this "
              f"from a directory that has a config file ({paths.config_file}).")
        sys.exit(1)


@app.command(rich_help_panel="Setting up the Sparv Pipeline")
def wizard():
    """Run config wizard to create a corpus config"""
    
    from sparv.core.wizard import Wizard
    
    check_sparv_is_set_up()
    
    wizard = Wizard()
    print("wizard.run()")
    sys.exit(0)


# Advanced commands
        



@app.command(rich_help_panel="Advanced commands")
def run_module(
    log_level: LogLevel = typer.Option("info", "--log", metavar="LOGLEVEL", help="Set the log level (default: 'info')"),
    module_args: list[str] = typer.Argument(None, help="Arguments to module"),
):
    """Run annotator module independently

    To pass flags to module use '--', e.g. `sparv run-module -- --flag`
    """
    
    check_sparv_is_set_up()
    print(f"{log_level!r}")
    # from sparv.core import run
    print(f"run.main({module_args}, log_level={log_level.value})")    
    sys.exit()


@app.command(rich_help_panel="Advanced commands")
def run_rule(
    ctx: typer.Context,
    targets: list[str] = typer.Argument(None, show_default="'list'", help="Annotation(s) to create"),
    list_rules: bool = typer.Option(False, "-l", "--list", help="List available rules"),
    wildcards: list[str] = typer.Option(None, "-w", "--wildcards", metavar="WILDCARD",
                                help="Supply values for wildcards using the format 'name=value'"),
    force_recreation: bool = typer.Option(False, "--force", help="Force recreation of target"),
    files: list[Path] = typer.Option(None, "-f", "--file", help="Only annotate specified input file(s)"),
    dry_run: bool = typer.Option(False, "-n", "--dry-run", help="Print summary of tasks without running them"),
    num_cores: int = typer.Option(0, "-j", "--cores", metavar="N", help="Use at most N cores in parallel; if N is omitted, use all available CPU cores"),
    keep_going: bool = typer.Option(False, "-k", "--keep-going", help="Keep going with independent tasks if a task fails"),
    log_level: LogLevel = typer.Option("warning", "--log", metavar="LOGLEVEL", help="Set the log level"),
    file_log_level: LogLevel = typer.Option("warning", "--log-to-file", metavar="LOGLEVEL", help="Set log level for logging to file"),
    show_stats: bool = typer.Option(False, "--stats", help="Show summary of time spent per annotator"),
    show_debug: bool = typer.Option(False, "--debug", help="Show debug messages"),
    socket: Optional[Path] = typer.Option(None, "--socket", help="Path to socket file created by the 'preload' command"),
    force_preloader: bool = typer.Option(False, "--force-preloader", help="Try to wait for preloader when it's busy"),
    show_simple: bool = typer.Option(False, "--simple", help="Show less details while running"),
):
    """Run specified rule(s) for creating annotations."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])
    print(f"{wildcards=}")


@app.command(rich_help_panel="Advanced commands")
def create_file(
    ctx: typer.Context,
    targets: list[str] = typer.Argument(None, show_default="'list'", help="File(s) to create"),
    list_files: bool = typer.Option(False, "-l", "--list", help="List available files that can be created"),
    force_recreation: bool = typer.Option(False, "--force", help="Force recreation of target"),
    dry_run: bool = typer.Option(False, "-n", "--dry-run", help="Print summary of tasks without running them"),
    num_cores: int = typer.Option(0, "-j", "--cores", metavar="N", help="Use at most N cores in parallel; if N is omitted, use all available CPU cores"),
    keep_going: bool = typer.Option(False, "-k", "--keep-going", help="Keep going with independent tasks if a task fails"),
    log_level: LogLevel = typer.Option("warning", "--log", metavar="LOGLEVEL", help="Set the log level"),
    file_log_level: LogLevel = typer.Option("warning", "--log-to-file", metavar="LOGLEVEL", help="Set log level for logging to file"),
    show_stats: bool = typer.Option(False, "--stats", help="Show summary of time spent per annotator"),
    show_debug: bool = typer.Option(False, "--debug", help="Show debug messages"),
    socket: Optional[Path] = typer.Option(None, "--socket", help="Path to socket file created by the 'preload' command"),
    force_preloader: bool = typer.Option(False, "--force-preloader", help="Try to wait for preloader when it's busy"),
    show_simple: bool = typer.Option(False, "--simple", help="Show less details while running"),
):
    """Create specified file(s). 
    
    The full path must be supplied and wildcards must be replaced."""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])


class StartStop(str, enum.Enum):
    Start = "start"
    Stop = "stop"

    
@app.command(rich_help_panel="Advanced commands")
def preload(
    ctx: typer.Context,
    preload_command: StartStop = typer.Argument("start"),
    socket: str = typer.Option("sparv.socket", "--socket", help="Path to socket file"),
    num_processes: int = typer.Option(1, "-j", "--processes", help="Number of processes to use"),
    list_preloads: bool = typer.Option(False, "-l", "--list", help="List annotators available for preloading"),
):
    """Preload annotators and models"""
    
    check_sparv_is_set_up()
    check_config_exists(ctx.obj["corpus_dir"])

    config, snakemake_args = create_config_and_snakemake_args(
        command=ctx.command.name,
        dir=ctx.obj["corpus_dir"],
        socket=socket,
        processes=num_processes,
        preload_command=preload_command.value,
        arg_list=list_preloads,
    )

    preload_cfg = PreloadCfg(
        socket=socket,
        processes=num_processes,
        preload_command=preload_command,
    )
    config2 = preload_cfg.dict()
    assert config == config2
    
    if list_preloads:
        preload_args = ListPreloadArgs(
            workdir=ctx.obj["corpus_dir"]
        )

    else:
        preload_args = PreloadArgs(
            workdir=ctx.obj["corpus_dir"]
        )
    snakemake_args2 = preload_args.dict()
    assert snakemake_args == snakemake_args2


class DefaultCfg(pydantic.BaseModel):
    run_by_sparv: bool = True


class DisplayConfigCfg(DefaultCfg):
    options: Optional[list[str]] = None


class ModulesCfg(DefaultCfg):
    types: list[str]
    names: list[str]

    
class PreloadCfg(DefaultCfg):
    preloader: bool = True
    socket: str
    processes: int
    preload_command: StartStop

    @pydantic.validator("socket")
    def resolve_path(cls, value):
        if isinstance(value, str):
            value = Path(value)
        if not isinstance(value, Path):
            raise TypeError("expecting str or Path")
        return str(value.resolve())

class RunCfg(DefaultCfg):
    ...
    
class SnakeMakeArgs(pydantic.BaseModel):
    workdir: Path
    force_use_threads: bool


class SimpleTargetMixin(pydantic.BaseModel):
    force_use_threads: bool = True

    
class DisplayConfigArgs(SimpleTargetMixin, SnakeMakeArgs):
    targets: list[str] = pydantic.Field(default_factory=lambda: ["config"])

    
class FilesArgs(SimpleTargetMixin, SnakeMakeArgs):
    targets: list[str] = pydantic.Field(default_factory=lambda: ["files"])

    
class ModulesArgs(SimpleTargetMixin, SnakeMakeArgs):
    targets: list[str] = pydantic.Field(default_factory=lambda: ["modules"])


class PreloadArgs(SimpleTargetMixin, SnakeMakeArgs):
    targets: list[str] = pydantic.Field(default_factory=lambda: ["preload"])


class ListPreloadArgs(SimpleTargetMixin, SnakeMakeArgs):
    targets: list[str] = pydantic.Field(default_factory=lambda: ["preload_list"])
    

class RunArgs(SnakeMakeArgs):
    ...
    

def create_config_and_snakemake_args(
    command: str,
    dir: Path,
    socket: Path = None,
    processes: int = None,
    preload_command: str = None,
    arg_list: bool = False,
    names: list[str] = None,
    types: list[str] = None,
    options: list[str] = None,
    cores: int = None,
):
    print(f"{command=}")
    snakemake_args = {"workdir": dir}
    config = {"run_by_sparv": True}
    simple_target = False
    log_level = ""
    log_file_level = ""
    simple_mode = False
    stats = False
    pass_through = False
    dry_run = False
    keep_going = False


    if command in ("modules", "config", "files", "clean", "presets", "classes", "languages", "preload"):
        snakemake_args["targets"] = [command]
        simple_target = True
        if command == "clean":
            config["export"] = export
            config["logs"] = logs
            config["all"] = all
        elif command == "config" and options:
            config["options"] = options
        elif command == "modules":
            if names:
                config["names"] = names
            config["types"] = types or []
        elif command == "preload":
            config["socket"] = str(Path(socket).resolve())
            config["preloader"] = True
            config["processes"] = processes
            config["preload_command"] = preload_command
            if arg_list:
                snakemake_args["targets"] = ["preload_list"]

        # return config, snakemake_args
    
    elif command in ("run", "run-rule", "create-file", "install", "uninstall", "build-models"):
        try:
            cores = cores or available_cpu_count()
        except NotImplementedError:
            cores = 1
        snakemake_update({
            "dryrun": dry_run,
            "cores": cores,
            "keepgoing": keep_going,
            "resources": {"threads": cores}
        })
        # Never show progress bar for list commands or dry run
        if arg_list or dry_run:
            simple_target = True

        stats = stats
        dry_run = dry_run
        keep_going = keep_going

        # Command: run
        if command == "run":
            if unlock:
                snakemake_args["unlock"] = unlock
                simple_target = True
                pass_through = True
            if mark_complete:
                snakemake_args["cleanup_metadata"] = mark_complete
                simple_target = True
                pass_through = True
            elif rerun_incomplete:
                snakemake_args["force_incomplete"] = True
            if list:
                snakemake_args["targets"] = ["list_exports"]
            elif output:
                snakemake_args["targets"] = output
            else:
                snakemake_args["targets"] = ["export_corpus"]
        # Command: run-rule
        elif command == "run-rule":
            snakemake_args["targets"] = targets
            if wildcards:
                config["wildcards"] = wildcards
            if list or snakemake_args["targets"] == ["list"]:
                snakemake_args["targets"] = ["list_targets"]
                simple_target = True
            elif force:
                # Rename all-files-rule to the related regular rule
                snakemake_args["forcerun"] = [t.replace(":", "::") for t in targets]
        # Command: create-file
        elif command == "create-file":
            snakemake_args["targets"] = targets
            if list or snakemake_args["targets"] == ["list"]:
                snakemake_args["targets"] = ["list_files"]
                simple_target = True
            elif force:
                snakemake_args["forcerun"] = targets
        # Command: install
        elif command == "install":
            if list:
                snakemake_args["targets"] = ["list_installs"]
            else:
                config["install_types"] = type
                snakemake_args["targets"] = ["install_corpus"]
        # Command: uninstall
        elif command == "uninstall":
            if list:
                snakemake_args["targets"] = ["list_uninstalls"]
            else:
                config["uninstall_types"] = type
                snakemake_args["targets"] = ["uninstall_corpus"]
        # Command: build-models
        elif command == "build-models":
            config["language"] = language
            if model:
                snakemake_args["targets"] = model
            elif all:
                snakemake_args["targets"] = ["build_models"]
            else:
                snakemake_args["targets"] = ["list_models"]
                simple_target = True

        log_level = log or "warning"
        log_file_level = log_to_file or "warning"
        simple_mode = simple
        socket = socket

        if socket:
            # Convert to absolute path, to work together with --dir
            socket_path = Path(socket).resolve()
            if not socket_path.is_socket():
                print(f"Socket file '{socket}' doesn't exist or isn't a socket.")
                sys.exit(1)
            socket = str(socket_path)

        config.update({"debug": debug,
                       "file": vars(args).get("file", []),
                       "log_level": log_level,
                       "log_file_level": log_file_level,
                       "socket": socket,
                       "force_preloader": force_preloader,
                       "targets": snakemake_args["targets"],
                       "threads": cores})

    if simple_target:
        # Force Snakemake to use threads to prevent unnecessary processes for simple targets
        snakemake_args["force_use_threads"] = True

    return config, snakemake_args

    
def main_cont():
    # Add common arguments
    for subparser in [run_parser, runrule_parser, createfile_parser, models_parser, install_parser, uninstall_parser]:
        subparser.add_argument("-n", "--dry-run", action="store_true",)
        subparser.add_argument("-j", "--cores", type=int, nargs="?", const=0, metavar="N",
                               default=1)
        subparser.add_argument("-k", "--keep-going", action="store_true",
                               help="Keep going with independent tasks if a task fails")
        subparser.add_argument("--log", metavar="LOGLEVEL", const="info",
                               help="Set the log level (default: 'warning' if --log is not specified, "
                                    "'info' if LOGLEVEL is not specified)",
                               nargs="?", choices=["debug", "info", "warning", "error", "critical"])
        subparser.add_argument("--log-to-file", metavar="LOGLEVEL", const="info",
                               help="Set log level for logging to file (default: 'warning' if --log-to-file is not "
                                    "specified, 'info' if LOGLEVEL is not specified)",
                               nargs="?", choices=["debug", "info", "warning", "error", "critical"])
        subparser.add_argument("--stats", action="store_true", help="Show summary of time spent per annotator")
        subparser.add_argument("--debug", action="store_true", help="Show debug messages")
        subparser.add_argument("--socket", help="Path to socket file created by the 'preload' command")
        subparser.add_argument("--force-preloader", action="store_true",
                               help="Try to wait for preloader when it's busy")
        subparser.add_argument("--simple", action="store_true", help="Show less details while running")

    # Add extra arguments to 'run' that we want to come last

    # Backward compatibility
    if len(sys.argv) > 1 and sys.argv[1] == "make":
        print("No rule to make target")
        sys.exit(1)

    # Parse arguments. We allow unknown arguments for the "run-module" command which is handled separately.
    args, unknown_args = parser.parse_known_args(args=None if sys.argv[1:] else ["--help"])

    # The "run-module" command is handled by a separate script
    if args.command == "run-module":
        from sparv.core import run
        run.main(unknown_args, log_level=args.log)
        sys.exit()
    else:
        import snakemake
        from snakemake.logging import logger
        from snakemake.utils import available_cpu_count
        from sparv.core import log_handler, paths, setup
        args = parser.parse_args()

    if args.command not in ("setup",):
        # Make sure that Sparv data dir is set
        if not paths.get_data_path():
            print(f"The path to Sparv's data directory needs to be configured, either by running 'sparv setup' or by "
                  f"setting the environment variable '{paths.data_dir_env}'.")
            sys.exit(1)

        # Check if Sparv data dir is outdated (or not properly set up yet)
        version_check = setup.check_sparv_version()
        if version_check is None:
            print("The Sparv data directory has been configured but not yet set up completely. Run 'sparv setup' to "
                  "complete the process.")
            sys.exit(1)
        elif not version_check:
            print("Sparv has been updated and Sparv's data directory may need to be upgraded. Please run the "
                  "'sparv setup' command.")
            sys.exit(1)

    if args.command == "setup":
        if args.reset:
            setup.reset()
        else:
            setup.run(args.dir)
        sys.exit(0)
    elif args.command == "wizard":
        from sparv.core.wizard import Wizard
        wizard = Wizard()
        wizard.run()
        sys.exit(0)

    # Check that a corpus config file is available in the working dir
    try:
        config_exists = Path(args.dir or Path.cwd(), paths.config_file).is_file()
    except PermissionError as e:
        print(f"{e.strerror}: {e.filename!r}")
        sys.exit(1)

    if args.command not in ("build-models", "languages"):
        if not config_exists:
            print(f"No config file ({paths.config_file}) found in working directory.")
            sys.exit(1)
    # For the 'build-models' command there needs to be a config file or a language parameter
    elif args.command == "build-models":
        if not config_exists and not args.language:
            print("Models are built for a specific language. Please provide one with the --language param or run this "
                  f"from a directory that has a config file ({paths.config_file}).")
            sys.exit(1)

    snakemake_args = {"workdir": args.dir}
    config = {"run_by_sparv": True}
    simple_target = False
    log_level = ""
    log_file_level = ""
    simple_mode = False
    stats = False
    pass_through = False
    dry_run = False
    keep_going = False

    if args.command in ("modules", "config", "files", "clean", "presets", "classes", "languages", "preload"):
        snakemake_args["targets"] = [args.command]
        simple_target = True
        if args.command == "clean":
            config["export"] = args.export
            config["logs"] = args.logs
            config["all"] = args.all
        elif args.command == "config" and args.options:
            config["options"] = args.options
        elif args.command == "modules":
            config["types"] = []
            if args.names:
                config["names"] = args.names
            for t in ["annotators", "importers", "exporters", "installers", "uninstallers", "all"]:
                if getattr(args, t):
                    config["types"].append(t)
        elif args.command == "preload":
            config["socket"] = str(Path(args.socket).resolve())
            config["preloader"] = True
            config["processes"] = args.processes
            config["preload_command"] = args.preload_command
            if args.list:
                snakemake_args["targets"] = ["preload_list"]

    elif args.command in ("run", "run-rule", "create-file", "install", "uninstall", "build-models"):
        try:
            cores = args.cores or available_cpu_count()
        except NotImplementedError:
            cores = 1
        snakemake_args.update({
            "dryrun": args.dry_run,
            "cores": cores,
            "keepgoing": args.keep_going,
            "resources": {"threads": args.cores}
        })
        # Never show progress bar for list commands or dry run
        if args.list or args.dry_run:
            simple_target = True

        stats = args.stats
        dry_run = args.dry_run
        keep_going = args.keep_going

        # Command: run
        if args.command == "run":
            if args.unlock:
                snakemake_args["unlock"] = args.unlock
                simple_target = True
                pass_through = True
            if args.mark_complete:
                snakemake_args["cleanup_metadata"] = args.mark_complete
                simple_target = True
                pass_through = True
            elif args.rerun_incomplete:
                snakemake_args["force_incomplete"] = True
            if args.list:
                snakemake_args["targets"] = ["list_exports"]
            elif args.output:
                snakemake_args["targets"] = args.output
            else:
                snakemake_args["targets"] = ["export_corpus"]
        # Command: run-rule
        elif args.command == "run-rule":
            snakemake_args["targets"] = args.targets
            if args.wildcards:
                config["wildcards"] = args.wildcards
            if args.list or snakemake_args["targets"] == ["list"]:
                snakemake_args["targets"] = ["list_targets"]
                simple_target = True
            elif args.force:
                # Rename all-files-rule to the related regular rule
                snakemake_args["forcerun"] = [t.replace(":", "::") for t in args.targets]
        # Command: create-file
        elif args.command == "create-file":
            snakemake_args["targets"] = args.targets
            if args.list or snakemake_args["targets"] == ["list"]:
                snakemake_args["targets"] = ["list_files"]
                simple_target = True
            elif args.force:
                snakemake_args["forcerun"] = args.targets
        # Command: install
        elif args.command == "install":
            if args.list:
                snakemake_args["targets"] = ["list_installs"]
            else:
                config["install_types"] = args.type
                snakemake_args["targets"] = ["install_corpus"]
        # Command: uninstall
        elif args.command == "uninstall":
            if args.list:
                snakemake_args["targets"] = ["list_uninstalls"]
            else:
                config["uninstall_types"] = args.type
                snakemake_args["targets"] = ["uninstall_corpus"]
        # Command: build-models
        elif args.command == "build-models":
            config["language"] = args.language
            if args.model:
                snakemake_args["targets"] = args.model
            elif args.all:
                snakemake_args["targets"] = ["build_models"]
            else:
                snakemake_args["targets"] = ["list_models"]
                simple_target = True

        log_level = args.log or "warning"
        log_file_level = args.log_to_file or "warning"
        simple_mode = args.simple
        socket = args.socket

        if socket:
            # Convert to absolute path, to work together with --dir
            socket_path = Path(socket).resolve()
            if not socket_path.is_socket():
                print(f"Socket file '{socket}' doesn't exist or isn't a socket.")
                sys.exit(1)
            socket = str(socket_path)

        config.update({"debug": args.debug,
                       "file": vars(args).get("file", []),
                       "log_level": log_level,
                       "log_file_level": log_file_level,
                       "socket": socket,
                       "force_preloader": args.force_preloader,
                       "targets": snakemake_args["targets"],
                       "threads": args.cores})

    if simple_target:
        # Force Snakemake to use threads to prevent unnecessary processes for simple targets
        snakemake_args["force_use_threads"] = True

    # Disable Snakemake's default log handler and use our own
    logger.log_handler = []
    progress = log_handler.LogHandler(progressbar=not simple_target, log_level=log_level, log_file_level=log_file_level,
                                      simple=simple_mode, stats=stats, pass_through=pass_through, dry_run=dry_run,
                                      keep_going=keep_going)
    snakemake_args["log_handler"] = [progress.log_handler]

    config["log_server"] = progress.log_server

    # Run Snakemake
    success = snakemake.snakemake(paths.sparv_path / "core" / "Snakefile", config=config, **snakemake_args)

    progress.stop()
    progress.cleanup()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    app()
