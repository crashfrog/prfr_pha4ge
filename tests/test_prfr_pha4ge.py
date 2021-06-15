#!/usr/bin/env python

"""Tests for `prfr_pha4ge` package."""

from asyncio import run

from tests import *
from hypothesis import given
from hypothesis.strategies import *

import unittest

from prfr_pha4ge.prfr_pha4ge import *


class TestPrfr_pha4ge(unittest.TestCase):
    """Tests for `prfr_pha4ge` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        pass

    def tearDown(self):
        """Tear down test fixtures, if any."""
        pass
    
    # Notifiers

    @given(
        notifiers(subclass_of=PrfrPha4GeNotifier, classdef={}),
        runs(),
        just(dict()),
        strings()
    )
    def test_PrfrPha4GeNotifier_notify(self, notifier, run, state, message):
        """Notifier.notify"""
        self.assertIsNone(notifier.notify(run, state, message))

    # Submitters

    @given(
        submitters(subclass_of=PrfrPha4GeSubmitter, classdef={})
    )
    def test_PrfrPha4GeSubmitter_test_noop(self, submitter):
        """Submitter.test_noop"""
        self.assertIsNone(run(submitter.test_noop()))

    @given(
        submitters(subclass_of=PrfrPha4GeSubmitter, classdef={}),
        paths()
    )
    def test_PrfrPha4GeSubmitter_reroot_path(self, submitter, path):
        """Submitter.reroot_path"""
        self.assertIsNotNone(submitter.reroot_path(path))

    @given(
        submitters(subclass_of=PrfrPha4GeSubmitter, classdef={}),
        strings(),
        paths(real=True),
        paths(),
        oneof(just(dict), dict(TEST=strings().example())) # empty and non-empty dicts
    )
    def test_PrfrPha4GeSubmitter_begin_job(self, submitter, execution_string, datadir, remotedir, environment_hints):
        """Submitter.begin_job"""
        self.assertIsNotNone(run(submitter.begin_job(execution_string, datadir, remotedir, environment_hints)))

    @given(
        submitters(subclass_of=PrfrPha4GeSubmitter, classdef={}),
        strings()
    )
    def test_PrfrPha4GeSubmitter_test_noop(self, submitter, job):
        """Submitter.poll_job"""
        self.assertIsNone(run(submitter.poll_job(job)))

    #FileJobs

    @given(
        jobs(subclass_of=PrfrPha4GeFileJob, classdef={}),
        runs(),
        files(real=True),
        paths(),
        paths()
    )
    def test_PrfrPha4GeFileJob_submit(self, job, run, file, datadir, remotedir):
        """FileJob.submit"""
        self.assertIsNotNone(job.setup(run, datadir, remotedir))

    @given(
        jobs(subclass_of=PrfrPha4GeFileJob, classdef={}),
        runs(),
        files(real=True),
        paths(),
        oneof(strings(), ints())
    )
    def test_PrfrPha4GeFileJob_collect(self, job, run, file, datadir, pid):
        """FileJob.collect"""
        self.assertIsNone(job.collect(run, datadir, pid))

    #RunJobs

    @given(
        jobs(subclass_of=PrfrPha4GeRunJob, classdef={}),
        runs(),
        paths(),
        paths()
    )
    def test_PrfrPha4GeRunJob_submit(self, job, run, datadir, remotedir):
        """RunJob.submit"""
        self.assertIsNotNone(job.setup(run, datadir, remotedir))

    @given(
        jobs(subclass_of=PrfrPha4GeRunJob, classdef={}),
        runs(),
        paths(),
        oneof(strings(), ints())
    )
    def test_PrfrPha4GeRunJob_collect(self, job, run, datadir, pid):
        """RunJob.collect"""
        self.assertIsNone(job.collect(run, datadir, pid))