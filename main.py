"""
Reads luminosity from a TSL2561 sensor and stores the results in BigQuery.
"""

import os
from datetime import datetime

import adafruit_tsl2561
import board
import busio
from dotenv import load_dotenv
from google.cloud import bigquery


def _sensor_setup():
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor = adafruit_tsl2561.TSL2561(i2c)
    sensor.gain = os.environ.get("TSL2561_GAIN", 0)
    sensor.integration_time = os.environ.get("TSL2561_INTERGRATION_TIME", 2)
    sensor.sensor_id = os.environ["TSL2561_SENSOR_ID"]
    return sensor


def _measurement(sensor):
    return {
        "lux": int(sensor.lux),
        "broadband": int(sensor.broadband),
        "infrared": int(sensor.infrared),
        "sensor_id": sensor.sensor_id,
        "requested_at": datetime.now(),
    }


def _gbq_setup():
    project_id = os.environ["GBQ_PROJECT_ID"]
    dataset_id = os.environ["GBQ_DATASET_ID"]
    table_id = os.environ["GBQ_TABLE_ID"]
    client = bigquery.Client()
    dataset = bigquery.dataset.DatasetReference.from_string(
        f"{project_id}.{dataset_id}"
    )
    table = client.get_table(dataset.table(table_id))
    return client, table


def _gbq_insert(measurement, client, table):
    errors = client.insert_rows(table, [measurement])
    if errors:
        raise RuntimeError(errors)


if __name__ == "__main__":
    load_dotenv()
    client, table = _gbq_setup()
    sensor = _sensor_setup()
    measurement = _measurement(sensor)
    _gbq_insert(measurement, client, table)
