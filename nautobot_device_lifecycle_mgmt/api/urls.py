"""API URLs for the Lifecycle Management plugin."""

from rest_framework import routers
from nautobot_device_lifecycle_mgmt.api.views import (
    HardwareLCMView,
    ContractLCMView,
    ProviderLCMView,
    ContactLCMView,
    SoftwareLCMViewSet,
    SoftwareImageLCMViewSet,
    ValidatedSoftwareLCMViewSet,
    CVELCMViewSet,
    VulnerabilityLCMViewSet,
    DeviceSoftwareValidationResultListViewSet,
    InventoryItemSoftwareValidationResultListViewSet,
)

router = routers.DefaultRouter()

router.register("hardware", HardwareLCMView)
router.register("contract", ContractLCMView)
router.register("provider", ProviderLCMView)
router.register("contact", ContactLCMView)
router.register("software", SoftwareLCMViewSet)
router.register("software-image", SoftwareImageLCMViewSet)
router.register("validated-software", ValidatedSoftwareLCMViewSet)
router.register("cve", CVELCMViewSet)
router.register("vulnerability", VulnerabilityLCMViewSet)
router.register("device-validated-software-result", DeviceSoftwareValidationResultListViewSet)
router.register("inventory-item-validated-software-result", InventoryItemSoftwareValidationResultListViewSet)

app_name = "nautobot_device_lifecycle_mgmt"

urlpatterns = router.urls
