"""Nautobot Device LCM  plugin application level metrics ."""
from datetime import datetime

from django.conf import settings
from nautobot.dcim.models import Device, Site
from prometheus_client.core import GaugeMetricFamily

from nautobot_device_lifecycle_mgmt.models import HardwareLCM

PLUGIN_SETTINGS = settings.PLUGINS_CONFIG.get("nautobot_device_lifecycle_mgmt", {})


def nautobot_metrics_dlcm_eos():
    """Calculate number of EOS devices per Device Type and per Site.
    Yields:
        GaugeMetricFamily: Prometheus Metrics
    """
    current_dt = datetime.now()
    hw_eos_notices = HardwareLCM.objects.filter(end_of_support__lte=current_dt)
    hw_eos_device_types = [notice.device_type for notice in hw_eos_notices]

    part_number_gauge = GaugeMetricFamily(
        "nautobot_lcm_devices_eos_per_part_number", "Nautobot LCM Devices EOS per Part Number", labels=["part_number"]
    )
    devices_gauge = GaugeMetricFamily(
        "nautobot_lcm_devices_eos_per_site", "Nautobot LCM Devices EOS per Site", labels=["site"]
    )

    for notice in hw_eos_notices:
        if notice.device_type:
            part_number = notice.device_type.slug
            eos_devices = Device.objects.filter(device_type=notice.device_type)
            metric_value = eos_devices.count()
        elif notice.inventory_item:
            part_number = notice.inventory_item
            eos_devices = Device.objects.filter(device_type__part_number=notice.inventory_item)
            metric_value = eos_devices.count()
        else:
            part_number = 'UNKNOWN'
            metric_value = 0
        part_number_gauge.add_metric(labels=[part_number], value=metric_value)
   
    yield part_number_gauge

    for site in Site.objects.all():
        eos_devices_in_site = Device.objects.filter(site=site, device_type__in=hw_eos_device_types)
        devices_gauge.add_metric(labels=[site.slug], value=eos_devices_in_site.count())
    
    yield devices_gauge


metrics = [nautobot_metrics_dlcm_eos]
