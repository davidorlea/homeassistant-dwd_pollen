"""Tests for DWD Pollen Sensor."""

from collections.abc import Callable, Generator
import datetime
from datetime import datetime as real_datetime
import json
from typing import Any
from unittest.mock import patch

from homeassistant.const import PERCENTAGE
import pytest
import requests
import requests_mock

from custom_components.dwd_pollen.sensor import DwdPollenApi, DwdPollenSensor


@pytest.fixture()
def mock_today() -> Generator[Callable[[datetime.datetime], None]]:
    """Fixture to mock today from datetime."""
    with patch(
        "custom_components.dwd_pollen.sensor.datetime", wraps=real_datetime
    ) as m:

        def _mock(date: datetime.datetime) -> None:
            m.today.return_value = date

        yield _mock


@pytest.mark.parametrize(
    "api_response",
    [
        None,
        "",
        {},
        {"content": None},
        {"content": {}},
    ],
)
def test_sensor_with_empty_response(
    api_response: Any, requests_mock: requests_mock.Mocker
) -> None:
    """Test that sensor with empty response returns correct properties."""
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=json.dumps(api_response),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 123, "Type")

    sensor.update()

    assert sensor.name == "Sensor 123 Type"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.state is None
    assert "description" not in sensor.extra_state_attributes
    assert "last_update" not in sensor.extra_state_attributes
    assert "next_update" not in sensor.extra_state_attributes
    assert "region_name" not in sensor.extra_state_attributes
    assert "partregion_name" not in sensor.extra_state_attributes
    assert "attribution" not in sensor.extra_state_attributes


def test_sensor_with_malformed_response(requests_mock: requests_mock.Mocker) -> None:
    """Test that sensor with malformed response returns correct properties."""
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text="some text",
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 123, "Type")

    sensor.update()

    assert sensor.name == "Sensor 123 Type"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.state is None
    assert "description" not in sensor.extra_state_attributes
    assert "last_update" not in sensor.extra_state_attributes
    assert "next_update" not in sensor.extra_state_attributes
    assert "region_name" not in sensor.extra_state_attributes
    assert "partregion_name" not in sensor.extra_state_attributes
    assert "attribution" not in sensor.extra_state_attributes


def test_sensor_with_error_response(requests_mock: requests_mock.Mocker) -> None:
    """Test that sensor with error response returns correct properties."""
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        status_code=500,
        text="some error",
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 123, "Type")

    sensor.update()

    assert sensor.name == "Sensor 123 Type"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.state is None
    assert "description" not in sensor.extra_state_attributes
    assert "last_update" not in sensor.extra_state_attributes
    assert "next_update" not in sensor.extra_state_attributes
    assert "region_name" not in sensor.extra_state_attributes
    assert "partregion_name" not in sensor.extra_state_attributes
    assert "attribution" not in sensor.extra_state_attributes


def test_sensor_with_no_response(requests_mock: requests_mock.Mocker) -> None:
    """Test that sensor with no response returns correct properties."""
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        exc=requests.exceptions.ConnectionError,
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 123, "Type")

    sensor.update()

    assert sensor.name == "Sensor 123 Type"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.state is None
    assert "description" not in sensor.extra_state_attributes
    assert "last_update" not in sensor.extra_state_attributes
    assert "next_update" not in sensor.extra_state_attributes
    assert "region_name" not in sensor.extra_state_attributes
    assert "partregion_name" not in sensor.extra_state_attributes
    assert "attribution" not in sensor.extra_state_attributes


def test_sensor_with_malformed_pollen_exposure(
    create_exposure: Any,
    create_region: Any,
    create_api_response: Any,
    mock_today: Callable[[datetime.datetime], None],
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test that sensor with malformed pollen exposure returns correct properties."""
    exposure = create_exposure().with_grass("999", "0", "0").build()
    region = (
        create_region()
        .with_region_id(111)
        .with_region_name("One Region")
        .with_partregion_id(222)
        .with_partregion_name("One Partregion")
        .with_exposure(exposure)
        .build()
    )
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=create_api_response(
            "2024-01-15 06:00 Uhr", "2024-01-16 06:00 Uhr", [region]
        ),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 222, "grass")

    mock_today(datetime.datetime(2024, 1, 15, 12, 00, 00))

    sensor.update()

    assert sensor.name == "Sensor 222 grass"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.state is None
    assert sensor.extra_state_attributes["description"] == "unknown level of exposure"
    assert sensor.extra_state_attributes["last_update"] == datetime.datetime(
        2024, 1, 15, 6, 0
    )
    assert sensor.extra_state_attributes["next_update"] == datetime.datetime(
        2024, 1, 16, 6, 0
    )
    assert sensor.extra_state_attributes["region_name"] == "One Region"
    assert sensor.extra_state_attributes["partregion_name"] == "One Partregion"
    assert (
        sensor.extra_state_attributes["attribution"]
        == "Data provided by Deutscher Wetterdienst"
    )


def test_sensor_with_unknown_partregion(
    create_exposure: Any,
    create_region: Any,
    create_api_response: Any,
    mock_today: Callable[[datetime.datetime], None],
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test that sensor with unknown partregion returns correct properties."""
    exposure = create_exposure().with_grass("1", "2", "3").build()
    region = (
        create_region()
        .with_region_id(111)
        .with_region_name("One Region")
        .with_partregion_id(222)
        .with_partregion_name("One Partregion")
        .with_exposure(exposure)
        .build()
    )
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=create_api_response(
            "2024-01-15 06:00 Uhr", "2024-01-16 06:00 Uhr", [region]
        ),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 999, "grass")

    mock_today(datetime.datetime(2024, 1, 15, 12, 00, 00))

    sensor.update()

    assert sensor.name == "Sensor 999 grass"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.state is None
    assert "description" not in sensor.extra_state_attributes
    assert "last_update" not in sensor.extra_state_attributes
    assert "next_update" not in sensor.extra_state_attributes
    assert "region_name" not in sensor.extra_state_attributes
    assert "partregion_name" not in sensor.extra_state_attributes
    assert "attribution" not in sensor.extra_state_attributes


def test_sensor_with_unknown_pollen_type(
    create_exposure: Any,
    create_region: Any,
    create_api_response: Any,
    mock_today: Callable[[datetime.datetime], None],
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test that sensor with unknown pollen type returns correct properties."""
    exposure = create_exposure().with_grass("1", "2", "3").build()
    region = (
        create_region()
        .with_region_id(111)
        .with_region_name("One Region")
        .with_partregion_id(222)
        .with_partregion_name("One Partregion")
        .with_exposure(exposure)
        .build()
    )
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=create_api_response(
            "2024-01-15 06:00 Uhr", "2024-01-16 06:00 Uhr", [region]
        ),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 999, "something")

    mock_today(datetime.datetime(2024, 1, 15, 12, 00, 00))

    sensor.update()

    assert sensor.name == "Sensor 999 something"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.state is None
    assert "description" not in sensor.extra_state_attributes
    assert "last_update" not in sensor.extra_state_attributes
    assert "next_update" not in sensor.extra_state_attributes
    assert "region_name" not in sensor.extra_state_attributes
    assert "partregion_name" not in sensor.extra_state_attributes
    assert "attribution" not in sensor.extra_state_attributes


def test_sensor_with_today(
    create_exposure: Any,
    create_region: Any,
    create_api_response: Any,
    mock_today: Callable[[datetime.datetime], None],
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test that sensor with today returns correct properties."""
    exposure = create_exposure().with_grass("1", "2", "3").build()
    region = (
        create_region()
        .with_region_id(111)
        .with_region_name("One Region")
        .with_partregion_id(999)
        .with_partregion_name("One Partregion")
        .with_exposure(exposure)
        .build()
    )
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=create_api_response(
            "2024-01-15 06:00 Uhr", "2024-01-16 06:00 Uhr", [region]
        ),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 999, "grass")

    mock_today(datetime.datetime(2024, 1, 15, 12, 00, 00))

    sensor.update()

    assert sensor.name == "Sensor 999 grass"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.unit_of_measurement == PERCENTAGE
    assert sensor.state == 33
    assert sensor.extra_state_attributes["description"] == "low level of exposure"
    assert sensor.extra_state_attributes["last_update"] == datetime.datetime(
        2024, 1, 15, 6, 0
    )
    assert sensor.extra_state_attributes["next_update"] == datetime.datetime(
        2024, 1, 16, 6, 0
    )
    assert sensor.extra_state_attributes["region_name"] == "One Region"
    assert sensor.extra_state_attributes["partregion_name"] == "One Partregion"
    assert (
        sensor.extra_state_attributes["attribution"]
        == "Data provided by Deutscher Wetterdienst"
    )


def test_sensor_with_yesterday(
    create_exposure: Any,
    create_region: Any,
    create_api_response: Any,
    mock_today: Callable[[datetime.datetime], None],
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test that sensor with yesterday returns correct properties."""
    exposure = create_exposure().with_grass("1", "2", "3").build()
    region = (
        create_region()
        .with_region_id(111)
        .with_region_name("One Region")
        .with_partregion_id(999)
        .with_partregion_name("One Partregion")
        .with_exposure(exposure)
        .build()
    )
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=create_api_response(
            "2024-01-15 06:00 Uhr", "2024-01-16 06:00 Uhr", [region]
        ),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 999, "grass")

    mock_today(datetime.datetime(2024, 1, 16, 12, 00, 00))

    sensor.update()

    assert sensor.name == "Sensor 999 grass"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.unit_of_measurement == PERCENTAGE
    assert sensor.state == 67
    assert sensor.extra_state_attributes["description"] == "medium level of exposure"
    assert sensor.extra_state_attributes["last_update"] == datetime.datetime(
        2024, 1, 15, 6, 0
    )
    assert sensor.extra_state_attributes["next_update"] == datetime.datetime(
        2024, 1, 16, 6, 0
    )
    assert sensor.extra_state_attributes["region_name"] == "One Region"
    assert sensor.extra_state_attributes["partregion_name"] == "One Partregion"
    assert (
        sensor.extra_state_attributes["attribution"]
        == "Data provided by Deutscher Wetterdienst"
    )


def test_sensor_with_ereyesterday(
    create_exposure: Any,
    create_region: Any,
    create_api_response: Any,
    mock_today: Callable[[datetime.datetime], None],
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test that sensor with ereyesterday returns correct properties."""
    exposure = create_exposure().with_grass("1", "2", "3").build()
    region = (
        create_region()
        .with_region_id(111)
        .with_region_name("One Region")
        .with_partregion_id(999)
        .with_partregion_name("One Partregion")
        .with_exposure(exposure)
        .build()
    )
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=create_api_response(
            "2024-01-15 06:00 Uhr", "2024-01-16 06:00 Uhr", [region]
        ),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 999, "grass")

    mock_today(datetime.datetime(2024, 1, 17, 12, 00, 00))

    sensor.update()

    assert sensor.name == "Sensor 999 grass"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.unit_of_measurement == PERCENTAGE
    assert sensor.state == 100
    assert sensor.extra_state_attributes["description"] == "high level of exposure"
    assert sensor.extra_state_attributes["last_update"] == datetime.datetime(
        2024, 1, 15, 6, 0
    )
    assert sensor.extra_state_attributes["next_update"] == datetime.datetime(
        2024, 1, 16, 6, 0
    )
    assert sensor.extra_state_attributes["region_name"] == "One Region"
    assert sensor.extra_state_attributes["partregion_name"] == "One Partregion"
    assert (
        sensor.extra_state_attributes["attribution"]
        == "Data provided by Deutscher Wetterdienst"
    )


def test_sensor_with_before_last_update(
    create_exposure: Any,
    create_region: Any,
    create_api_response: Any,
    mock_today: Callable[[datetime.datetime], None],
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test that sensor with before last update returns correct properties."""
    exposure = create_exposure().with_grass("1", "2", "3").build()
    region = (
        create_region()
        .with_region_id(111)
        .with_region_name("One Region")
        .with_partregion_id(999)
        .with_partregion_name("One Partregion")
        .with_exposure(exposure)
        .build()
    )
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=create_api_response(
            "2024-01-15 06:00 Uhr", "2024-01-16 06:00 Uhr", [region]
        ),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 999, "grass")

    mock_today(datetime.datetime(2024, 1, 15, 3, 00, 00))

    sensor.update()

    assert sensor.name == "Sensor 999 grass"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.unit_of_measurement == PERCENTAGE
    assert sensor.state == 33
    assert sensor.extra_state_attributes["description"] == "low level of exposure"
    assert sensor.extra_state_attributes["last_update"] == datetime.datetime(
        2024, 1, 15, 6, 0
    )
    assert sensor.extra_state_attributes["next_update"] == datetime.datetime(
        2024, 1, 16, 6, 0
    )
    assert sensor.extra_state_attributes["region_name"] == "One Region"
    assert sensor.extra_state_attributes["partregion_name"] == "One Partregion"
    assert (
        sensor.extra_state_attributes["attribution"]
        == "Data provided by Deutscher Wetterdienst"
    )


def test_sensor_with_before_next_update(
    create_exposure: Any,
    create_region: Any,
    create_api_response: Any,
    mock_today: Callable[[datetime.datetime], None],
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test that sensor with before next update returns correct properties."""
    exposure = create_exposure().with_grass("1", "2", "3").build()
    region = (
        create_region()
        .with_region_id(111)
        .with_region_name("One Region")
        .with_partregion_id(999)
        .with_partregion_name("One Partregion")
        .with_exposure(exposure)
        .build()
    )
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=create_api_response(
            "2024-01-15 06:00 Uhr", "2024-01-16 06:00 Uhr", [region]
        ),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 999, "grass")

    mock_today(datetime.datetime(2024, 1, 16, 3, 00, 00))

    sensor.update()

    assert sensor.name == "Sensor 999 grass"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.unit_of_measurement == PERCENTAGE
    assert sensor.state == 67
    assert sensor.extra_state_attributes["description"] == "medium level of exposure"
    assert sensor.extra_state_attributes["last_update"] == datetime.datetime(
        2024, 1, 15, 6, 0
    )
    assert sensor.extra_state_attributes["next_update"] == datetime.datetime(
        2024, 1, 16, 6, 0
    )
    assert sensor.extra_state_attributes["region_name"] == "One Region"
    assert sensor.extra_state_attributes["partregion_name"] == "One Partregion"
    assert (
        sensor.extra_state_attributes["attribution"]
        == "Data provided by Deutscher Wetterdienst"
    )


def test_sensor_with_too_old(
    create_exposure: Any,
    create_region: Any,
    create_api_response: Any,
    mock_today: Callable[[datetime.datetime], None],
    requests_mock: requests_mock.Mocker,
) -> None:
    """Test that sensor with too old returns correct properties."""
    exposure = create_exposure().with_grass("1", "2", "3").build()
    region = (
        create_region()
        .with_region_id(111)
        .with_region_name("One Region")
        .with_partregion_id(999)
        .with_partregion_name("One Partregion")
        .with_exposure(exposure)
        .build()
    )
    requests_mock.get(
        "https://opendata.dwd.de/climate_environment/health/alerts/s31fg.json",
        text=create_api_response(
            "2024-01-15 06:00 Uhr", "2024-01-16 06:00 Uhr", [region]
        ),
    )
    sensor = DwdPollenSensor(DwdPollenApi(), "Sensor", 999, "grass")

    mock_today(datetime.datetime(2024, 1, 18, 12, 00, 00))

    sensor.update()

    assert sensor.name == "Sensor 999 grass"
    assert sensor.icon == "mdi:flower"
    assert sensor.device_class is None
    assert sensor.unit_of_measurement == PERCENTAGE
    assert sensor.state is None
    assert sensor.extra_state_attributes["description"] == "unknown level of exposure"
    assert sensor.extra_state_attributes["last_update"] == datetime.datetime(
        2024, 1, 15, 6, 0
    )
    assert sensor.extra_state_attributes["next_update"] == datetime.datetime(
        2024, 1, 16, 6, 0
    )
    assert sensor.extra_state_attributes["region_name"] == "One Region"
    assert sensor.extra_state_attributes["partregion_name"] == "One Partregion"
    assert (
        sensor.extra_state_attributes["attribution"]
        == "Data provided by Deutscher Wetterdienst"
    )
