"""Jobs for the CVE Tracking portion of the Device Lifecycle plugin."""
from datetime import datetime

from nautobot.extras.jobs import Job, StringVar, BooleanVar
from nautobot.extras.models import Relationship, RelationshipAssociation

from nautobot_device_lifecycle_mgmt.models import (
    CVELCM,
    VulnerabilityLCM,
)


name = "CVE Tracking"  # pylint: disable=invalid-name


class GenerateVulnerabilities(Job):
    """Generates VulnerabilityLCM objects based on CVEs that are related to Devices."""

    name = "Generate Vulnerabilities"
    description = "Generates any missing Vulnerability objects."
    read_only = False
    published_after = StringVar(
        regex=r"^[0-9]{4}\-[0-9]{2}\-[0-9]{2}$",
        label="CVEs Published After",
        description="Enter a date in ISO Format (YYYY-MM-DD) to only process CVEs published after that date.",
        default="1970-01-01",
        required=False,
    )
    debug = BooleanVar(description="Enable for more verbose logging.")

    class Meta:  # pylint: disable=too-few-public-methods
        """Meta class for the job."""

        commit_default = True
        field_order = [
            "published_after",
            "_task_queue",
            "debug",
        ]

    def run(self, published_after, debug=False):  # pylint: disable=too-many-locals
        """Check if software assigned to each device is valid. If no software is assigned return warning message."""
        # Although the default is set on the class attribute for the UI, it doesn't default for the API
        published_after = published_after if published_after is not None else "1970-01-01"
        cves = CVELCM.objects.filter(published_date__gte=datetime.fromisoformat(published_after))
        count_before = VulnerabilityLCM.objects.count()

        for cve in cves:
            if debug:
                self.logger.info(message="Generating vulnerabilities for CVE {cve}", extra={"object": cve})
            software_rels = RelationshipAssociation.objects.filter(relationship__slug="soft_cve", destination_id=cve.id)
            for soft_rel in software_rels:
                # Loop through any device relationships
                device_rels = soft_rel.source.get_relationships()["source"][
                    Relationship.objects.get(slug="device_soft")
                ]
                for dev_rel in device_rels:
                    vuln_obj, _ = VulnerabilityLCM.objects.get_or_create(
                        cve=cve, software=dev_rel.source, device=dev_rel.destination
                    )
                    vuln_obj.validated_save()

                # Loop through any inventory tem relationships
                item_rels = soft_rel.source.get_relationships()["source"][
                    Relationship.objects.get(slug="inventory_item_soft")
                ]
                for item_rel in item_rels:
                    vuln_obj, _ = VulnerabilityLCM.objects.get_or_create(
                        cve=cve, software=item_rel.source, inventory_item=item_rel.destination
                    )
                    vuln_obj.validated_save()

        diff = VulnerabilityLCM.objects.count() - count_before
        self.logger.info(f"Processed {cves.count()} CVEs and generated {diff} Vulnerabilities.")
