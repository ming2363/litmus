"""由抄表和单价计算电费。"""

import logging
from decimal import Decimal

from protocol.reading import Reading

logger = logging.getLogger("billing.charge")


def energy_fee(reading: Reading, yuan_per_kwh: Decimal) -> Decimal:
    logger.info("fee meter=%s", reading.meter_id)
    scaled = reading.energy / Decimal(1000)
    amount = scaled * yuan_per_kwh
    logger.info("fee amount=%s", amount)
    return amount
