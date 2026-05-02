"""Benchmarks for measuring library performance using real-world fixtures."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock

import pytest

from pyomnilogic_local.models.mspconfig import MSPConfig
from pyomnilogic_local.models.telemetry import Telemetry
from pyomnilogic_local.omnilogic import OmniLogic
from tests.test_fixtures import FIXTURES_DIR, load_fixture

FIXTURE_FILES = sorted(f.name for f in FIXTURES_DIR.glob("*.json"))


@pytest.fixture(params=FIXTURE_FILES)
def fixture_data(request: pytest.FixtureRequest) -> dict[str, str]:
    """Load fixture data, parameterized across all available fixture files."""
    return load_fixture(request.param)


def get_omni(fixture_data: dict[str, str]) -> OmniLogic:
    """Helper to create an OmniLogic instance with mocked API."""
    omni = OmniLogic("127.0.0.1")
    omni._api = AsyncMock()
    omni._api.async_get_telemetry.return_value = Telemetry.load_xml(fixture_data["telemetry"])
    omni._api.async_get_mspconfig.return_value = MSPConfig.load_xml(fixture_data["mspconfig"])
    return omni


def test_refresh_telemetry(benchmark: Any, fixture_data: dict[str, str]) -> None:
    """Benchmark a recurring refresh cycle where only telemetry is updated."""
    omni = get_omni(fixture_data)
    benchmark(lambda: asyncio.run(omni.refresh(force_telemetry=True)))


def test_refresh_mspconfig(benchmark: Any, fixture_data: dict[str, str]) -> None:
    """Benchmark a recurring refresh cycle where only MSP Config is updated."""
    omni = get_omni(fixture_data)
    benchmark(lambda: asyncio.run(omni.refresh(force_mspconfig=True)))
