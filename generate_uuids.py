import uuid

# Generate stable UUIDs for the MSI
print(f"UpgradeCode: {uuid.uuid5(uuid.NAMESPACE_DNS, 'master-refreshing-app-upgrade-code')}")
print(f"ProductComponent: {uuid.uuid5(uuid.NAMESPACE_DNS, 'master-refreshing-app-product')}")
