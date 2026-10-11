"""Commissioning-only quirk for the no-GPIO ZG101 probe image.

This does not match the stock TS0044 or the deployed TS0041 garage button.
Writing device_config persists a new GPIO profile and reboots the remote.
"""

from zhaquirks import CustomCluster
import zigpy.types as t
from zigpy.quirks.v2 import QuirkBuilder
from zigpy.zcl.clusters.general import Basic
from zigpy.zcl.foundation import ZCLAttributeDef


class ProbeBasicCluster(CustomCluster, Basic):
    class AttributeDefs(Basic.AttributeDefs):
        device_config = ZCLAttributeDef(
            id=0xFF00,
            type=t.LongCharacterString,
            access="rw",
            is_manufacturer_specific=False,
        )
        multi_press_reset_count = ZCLAttributeDef(
            id=0xFF02,
            type=t.uint8_t,
            access="rw",
            is_manufacturer_specific=False,
        )


(
    QuirkBuilder("wkai4ga5", "TS0044-ZG101-PROBE")
    .replaces(ProbeBasicCluster, endpoint_id=1)
    .add_to_registry()
)
