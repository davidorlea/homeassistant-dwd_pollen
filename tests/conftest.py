"""Test fixtures for DWD Pollen Sensor."""

from collections.abc import Callable
import json
from typing import Any, Self

from pytest import fixture


class DwdPollenExposureFixture:
    """Representation of a DWD Pollen exposure fixture."""

    def __init__(self) -> None:
        """Initialize the DWD Pollen exposure fixture."""
        self._alder = ["0", "0", "0"]
        self._ambrosia = ["0", "0", "0"]
        self._ash = ["0", "0", "0"]
        self._birch = ["0", "0", "0"]
        self._grass = ["0", "0", "0"]
        self._hazel = ["0", "0", "0"]
        self._mugwort = ["0", "0", "0"]
        self._rye = ["0", "0", "0"]

    def with_grass(self, today: str, tomorrow: str, overmorrow: str) -> Self:
        """Set an individual grass exposure."""
        self._grass = [today, tomorrow, overmorrow]
        return self

    def build(self) -> dict[str, Any]:
        """Return the exposure."""
        return {
            "Ambrosia": {
                "today": self._ambrosia[0],
                "tomorrow": self._ambrosia[1],
                "dayafter_to": self._ambrosia[2],
            },
            "Beifuss": {
                "today": self._mugwort[0],
                "tomorrow": self._mugwort[1],
                "dayafter_to": self._mugwort[2],
            },
            "Birke": {
                "today": self._birch[0],
                "tomorrow": self._birch[1],
                "dayafter_to": self._birch[2],
            },
            "Erle": {
                "today": self._alder[0],
                "tomorrow": self._alder[1],
                "dayafter_to": self._alder[2],
            },
            "Esche": {
                "today": self._ash[0],
                "tomorrow": self._ash[1],
                "dayafter_to": self._ash[2],
            },
            "Graeser": {
                "today": self._grass[0],
                "tomorrow": self._grass[1],
                "dayafter_to": self._grass[2],
            },
            "Hasel": {
                "today": self._hazel[0],
                "tomorrow": self._hazel[1],
                "dayafter_to": self._hazel[2],
            },
            "Roggen": {
                "today": self._rye[0],
                "tomorrow": self._rye[1],
                "dayafter_to": self._rye[2],
            },
        }


class DwdPollenRegionFixture:
    """Representation of a DWD Pollen region fixture."""

    def __init__(self) -> None:
        """Initialize the DWD Pollen region fixture."""
        self._region_id = 123
        self._region_name = "Some Region Name"
        self._partregion_id = 456
        self._partregion_name = "Some Part Region Name"
        self._exposure: dict[str, Any] = {}

    def with_region_id(self, region_id: int) -> Self:
        """Set an individual region ID."""
        self._region_id = region_id
        return self

    def with_region_name(self, region_name: str) -> Self:
        """Set an individual region name."""
        self._region_name = region_name
        return self

    def with_partregion_id(self, partregion_id: int) -> Self:
        """Set an individual partregion ID."""
        self._partregion_id = partregion_id
        return self

    def with_partregion_name(self, partregion_name: str) -> Self:
        """Set an individual partregion name."""
        self._partregion_name = partregion_name
        return self

    def with_exposure(self, exposure: dict[str, Any]) -> Self:
        """Set an individual exposure."""
        self._exposure = exposure
        return self

    def build(self) -> dict[str, Any]:
        """Return the region."""
        return {
            "region_id": self._region_id,
            "region_name": self._region_name,
            "partregion_id": self._partregion_id,
            "partregion_name": self._partregion_name,
            "Pollen": self._exposure,
        }


class DwdPollenApiFixture:
    """Representation of a DWD Pollen API fixture."""

    def __init__(self) -> None:
        """Initialize the DWD Pollen API fixture."""
        self._last_update = "1970-01-01 00:01 Uhr"
        self._next_update = "1970-01-02 00:02 Uhr"
        self._regions: list[dict[str, Any]] = []

    def with_last_update(self, last_update: str) -> Self:
        """Set an individual last update."""
        self._last_update = last_update
        return self

    def with_next_update(self, next_update: str) -> Self:
        """Set an individual next update."""
        self._next_update = next_update
        return self

    def with_regions(self, regions: list[dict[str, Any]]) -> Self:
        """Set an individual list of regions."""
        self._regions = regions
        return self

    def build(self) -> dict[str, Any]:
        """Return the API."""
        return {
            "last_update": self._last_update,
            "next_update": self._next_update,
            "content": self._regions,
        }


@fixture()
def create_exposure() -> Callable[[], DwdPollenExposureFixture]:
    """Fixture to create a DWD Pollen exposure."""

    def _create_exposure() -> DwdPollenExposureFixture:
        return DwdPollenExposureFixture()

    return _create_exposure


@fixture()
def create_region() -> Callable[[], DwdPollenRegionFixture]:
    """Fixture to create a DWD Pollen region."""

    def _create_region() -> DwdPollenRegionFixture:
        return DwdPollenRegionFixture()

    return _create_region


@fixture()
def create_api_response() -> Callable[[str, str, list[dict[str, Any]]], str]:
    """Fixture to create a DWD Pollen API response."""

    def _create_api_response(
        last_update: str, next_update: str, regions: list[dict[str, Any]]
    ) -> str:
        response = (
            DwdPollenApiFixture()
            .with_last_update(last_update)
            .with_next_update(next_update)
            .with_regions(regions)
            .build()
        )
        return json.dumps(response)

    return _create_api_response
