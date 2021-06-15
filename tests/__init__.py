"""Unit test package for prfr_pha4ge."""

import tempfile


from collections import namedtuple
from datetime import datetime
from hypothesis.strategies import *
from pathlib import Path
import os
import namesgenerator

from porerefiner import models, jobs, notifiers

from porerefiner.protocols.porerefiner.rpc import porerefiner_pb2 as messages

the_present = datetime.now()

@composite
def paths(draw, under="", min_deep=2, pathlib_only=False, real=False):
    if real:
        return draw(builds(Path, builds(lambda: tempfile.NamedTemporaryFile().name)))
    r = [just(under)]
    for _ in range(min_deep):
        r.append(text(min_size=1, max_size=255))
    p = builds(Path, *r)
    if pathlib_only:
        return draw(p)
    return draw(one_of(p, p.map(str)))

@composite
def files(draw, real=False):
    if real:
        path = builds(Path, builds(lambda: tempfile.NamedTemporaryFile().name))
    else:
        path = paths(pathlib_only=True)
    return draw(builds(models.File,
                       pk=sql_ints(),
                       path=path))


@composite
def samples(draw):
    sid = text(min_size=7, max_size=10)
    acc = text(min_size=5, max_size=10)
    bar = text(min_size=10, max_size=10)
    org = text(min_size=12, max_size=12)
    ext = text(min_size=10, max_size=10)
    com = text()
    use = emails()
    return draw(builds(messages.SampleSheet.Sample,
                       sample_id=sid,
                       accession=acc,
                       barcode_id=bar,
                       organism=org,
                       extraction_kit=ext,
                       comment=com,
                       user=use))

@composite
def samplesheets(draw):
    ver = just('1.0.1')
    dat = datetimes()
    lib = text(min_size=12, max_size=12)
    seq = text(min_size=12, max_size=12)
    bar = text(min_size=12, max_size=12)
    sam = lists(samples(), min_size=1, max_size=12)
    ss = draw(builds(messages.SampleSheet,
                     porerefiner_ver=ver,
                     library_id=lib,
                     sequencing_kit=seq,
                     barcode_kit=bar,
                     samples=sam))
    ss.date.FromDatetime(draw(dat))
    return ss


@composite
def flowcells(draw, path=None):
    pk  = sql_ints()
    cid = text()
    cname = text()
    cty = text()
    if not path:
        pat = paths(min_deep=2, under="/data")
    else:
        pat = just(Path(path))
    return draw(builds(models.Flowcell,
                       #pk=pk,
                       consumable_id=cid,
                       consumable_name=cname,
                       consumable_type=cty,
                       path=pat))

@composite
def runs(draw, sheet=True):
    if sheet:
        ss = samplesheets()
    else:
        ss = just(None)
    path = draw(paths(pathlib_only=True))
    return draw(builds(models.Run,
                       #pk=sql_ints(),
                       # flowcell=flowcells(path=path.parent),
                       _sample_sheets=ss,
                       name=text(),
                       library_id=text(),
                       run_id=text(),
                       started=datetimes(max_value=the_present),
                       ended=datetimes(min_value=the_present),
                       status=sampled_from([status[0] for status in models.Run.statuses]),
                       path=just(path),
                       basecalling_model=sampled_from([model[0] for model in models.Run.basecallers])))

Event = namedtuple('Event', ('src_path', 'is_directory'))

@composite
def fsevents(draw, min_deep=4):
    return draw(builds(Event,
                       src_path=paths(min_deep=min_deep, pathlib_only=True),
                       is_directory=booleans()))

def random_name_subclass(of=object, **classdef):
    classdef['__module__'] = __name__
    new_typename = namesgenerator.get_random_name(sep=' ').title().replace(' ', '') + of.__name__
    new_type = type(new_typename, (of,), classdef)
    globals()[new_typename] = new_type
    return new_type

@composite
def notifiers(draw,
            subclass_of=notifiers.Notifier,
            classdef=dict(notify=lambda *a, **k: None)):
    return draw(builds(random_name_subclass(of=subclass_of, **classdef)))


@composite
def submitters(draw, 
              subclass_of=jobs.submitters.Submitter,
              classdef=dict(test_noop=lambda: None,
                                            reroot_path=lambda: None,
                                            begin_job=lambda: "",
                                            poll_job=lambda: "",
                                            closeout_job=lambda: None)):
    return draw(builds(random_name_subclass(of=subclass_of,
                                            **classdef)))

@composite
def jobs(draw, subclass_of=jobs.RunJob, classdef=dict(setup=lambda *a, **k: None, collect=lambda *a, **k: None)):
    return draw(builds(random_name_subclass(of=subclass_of, **classdef),
                       submitter=submitters()))