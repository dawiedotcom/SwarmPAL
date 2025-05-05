from __future__ import annotations

import pytest

import swarmpal.toolboxes
from swarmpal.toolboxes import dsecs


@pytest.mark.dsecs()
def test_by_name():
    """The DSECS toolbox was added to the toolboxes lookup dictionary"""
    preprocess = swarmpal.make_process("dsecs.preprocess")
    assert isinstance(preprocess, dsecs.processes.Preprocess)

    analysis = swarmpal.make_process("dsecs.analysis")
    assert isinstance(analysis, dsecs.processes.Analysis)
