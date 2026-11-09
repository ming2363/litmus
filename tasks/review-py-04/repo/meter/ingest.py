"""接入一条瓦时抄表。"""

import logging

from protocol.reading import Reading, reading_from_watt_hours

logger = logging.getLogger("meter.ingest")


def ingest_row(meter_id: str, lane: str, taken_at: int, watt_hours: int, voltage: str) -> Reading:
    reading = reading_from_watt_hours(meter_id, lane, taken_at, watt_hours, voltage)
    logger.info("ingest meter=%s lane=%s", reading.meter_id, reading.lane)
    return reading
