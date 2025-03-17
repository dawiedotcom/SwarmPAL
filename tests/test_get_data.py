from __future__ import annotations

import numpy as np
import pytest
from swarmpal import get_data
from xarray import Dataset, DataTree

from .io.test_paldata import vires_checks, hapi_checks

@pytest.mark.remote()
def test_get_data_vires():
    data_spec = dict(
        provider="vires",
        config=dict(
            collection="SW_OPER_MAGA_LR_1B",
            measurements=["F", "B_NEC"],
            models=["IGRF"],
            start_time="2016-01-01T00:00:00",
            end_time="2016-01-01T00:00:10",
            filters=["(Longitude > 92.8) AND (Latitude < -72.57)"],
            server_url="https://vires.services/ows",
        )
    )

    item = get_data(**data_spec)
    vires_checks(item)
    
@pytest.mark.remote()
def test_get_data_hapi():

    data_spec = dict(
        provider="hapi",
        config=dict(
            dataset="SW_OPER_MAGA_LR_1B",
            parameters="F,B_NEC",
            start="2016-01-01T00:00:00",
            stop="2016-01-01T00:00:10",
            server="https://vires.services/hapi",
        )
    )

    item = get_data(**data_spec)
    hapi_checks(item)

@pytest.mark.remote()
def test_pad_times():
    data_spec = dict(
        provider="vires",
        config=dict(
          collection="SW_OPER_MAGA_LR_1B",
          measurements=["F", "B_NEC"],
          start_time="2016-01-01T00:00:00",
          end_time="2016-01-01T00:00:10",
          pad_times=["0:00:03", "0:00:05"],
          server_url="https://vires.services/ows",
        )
    )
    item = get_data(**data_spec)

    assert "Timestamp" in item.xarray
    assert item.xarray["Timestamp"].to_numpy()[0] >= np.datetime64(
        "2015-12-31T23:59:57"
    )
    assert item.xarray["Timestamp"].to_numpy()[-1] <= np.datetime64(
        "2016-01-01T00:00:14"
    )
