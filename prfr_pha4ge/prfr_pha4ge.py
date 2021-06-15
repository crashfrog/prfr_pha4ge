"""Main module."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union, Tuple

from porerefiner.notifiers import Notifier
from porerefiner.jobs import FileJob, RunJob
from porerefiner.jobs.submitters import Submitter
from porerefiner.models import Run, File
from porerefiner.samplesheets import SnifferFor, ParserFor
from porerefiner.protocols.porerefiner.rpc.porerefiner_pb2 import SampleSheet

@dataclass
class PrfrPha4GeNotifier(Notifier):
    """Configurable run completion notifier. Implement async method 'notify.'"""

    prfr_pha4ge_sample_param: str

    async def notify(self, run: Run, state: Any, message: str) -> None:
        "Handler for notifications. `state` is not currently implemented."
        pass

@dataclass
class PrfrPha4GeSubmitter(Submitter):
    """Configurable job runner. Implement the below methods."""

    prfr_pha4ge_sample_param: str

    async def test_noop(self) -> None:
        "No-op method submitters should implement to make sure the submitter can access an external resource."
        pass

    def reroot_path(self, path: Path) -> Path:
        "Submitters should translate paths to be relative to execution environment"
        pass

    async def begin_job(self, execution_string: str, datadir: Path, remotedir: Path, environment_hints: dict = {}) -> str:
        "Semantics of scheduling a job. Jobs can provide execution hints. Return an optional job id"
        pass

    async def poll_job(self, job:str) -> str:
        "Semantics of polling a job."
        pass

@dataclass
class PrfrPha4GeFileJob(FileJob):
    """Configurable job that will be triggered whenever a file enters a completed state."""

    command1: str = "cp {file} {remotedir}/{file}"
    command2: str = "convert {remotedir}/{file} --fasta >> {remotedir}/{file.name}.converted.fasta"

    def run(self, run: Run, file: File, datadir: Path, remotedir: Path) -> Generator[Union[str, Tuple[str, dict]], Union[CompletedProcess, int, str]]:
        """File job method. Set up the job, then yield a command string or
           a tuple of a command string plus a dictionary of execution hints.
           The job runner will send back the result if it's successful."""
        errcode = yield command1.format(**locals())
        if not errcode:
            yield command2.format(**locals())


@dataclass
class PrfrPha4GeRunJob(RunJob):
    """Configurable job that will be triggered whenever a run enters a completed state."""

    command: str = "cwltool {self.cwl} --name{run.name} --run {remotedir}"

    def run(self, run: Run, datadir: Path, remotedir: Path) -> Generator[Union[str, Tuple[str, dict]], Union[CompletedProcess, int, str]]:
        """Run job method."""
        yield command.format(**locals())

# Tips for writing a sample sheet parser:
# 1) Write a sniffer that's pretty specific; have the docstring be an example of the format in TSV
# 2) Your example can be cut and pasted in from Excel
# 3) Decorate the sniffer with whether it's for CSV or XLS format or both
# 4) Link the parser to the sniffer using the ParserFor decorator and the name of your sniffer

@SnifferFor.csv
def prfr_pha4ge(rows):
    """porerefiner_ver	1.0.1
library_id	
sequencing_kit	
barcode_kit	
sample_id	accession	barcode_id	organism	extraction_kit	comment user
TEST	TEST	TEST	TEST	TEST	TEST	TEST"""
    note, ver, *_ = rows[0]
    return note == 'porerefiner_ver' and ver == '1.0.1'


@ParserFor.prfr_pha4ge
def prfr_pha4ge_parser(rows):
    "prfr_pha4ge samplesheet parser"
    rows = iter(rows)
    ss = SampleSheet()
    ss.date.GetCurrentTime()
    _, ss.porerefiner_ver, *_ = next(rows)
    _, ss.library_id, *_ = next(rows)
    _, ss.sequencing_kit = next(rows)
    key, value, *rest = next(rows)
    if 'barcode_kit' in key: #if it's not the header
        [ss.barcode_kit.append(barcode) for barcode in [value] + rest]
        next(rows) # skip the header
    for sample_id, accession, barcode_id, organism, extraction_kit, comment, user, *_ in rows:
        ss.samples.add(sample_id=sample_id,
                        accession=accession,
                        barcode_id=barcode_id,
                        organism=organism,
                        extraction_kit=extraction_kit,
                        comment=comment,
                        user=user)
    return ss
