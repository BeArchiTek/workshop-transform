from infrahub_sdk.generator import InfrahubGenerator

PROVISIONING_STATUS = "provisioning"
ACTIVE_STATUS = "active"

# Here we have some design information
# TODO: eventually we would like to capture that in infrahub in a proper design object
DESIGNS = {"single-node": {"number_of_switch": 1}, "ha": {"number_of_switch": 2}}

IP_MANAGEMENT_POOL = "Management addresses pool"

DEVICE_GROUP = "cisco_devices"

# Here we have device type information
# TODO: eventually we would like to capture that in infrahub in a device template object
TEMPLATES = {
    "cisco-ws-c3650-24pd-s": {
        "label": "Cisco WS-C3650-24PD-S",
        "interfaces": [
            {
                "name": "GigabitEthernet1/0/1",
                "speed": 1000,
                "role": "peer",
                "kind": "InfraInterfaceL3",
            },
            {
                "name": "GigabitEthernet1/0/2",
                "speed": 1000,
                "role": "peer",
                "kind": "InfraInterfaceL3",
            },
            {
                "name": "GigabitEthernet1/0/3",
                "speed": 1000,
                "role": "server",
                "kind": "InfraInterfaceL3",
            },
            {
                "name": "GigabitEthernet1/0/4",
                "speed": 1000,
                "role": "server",
                "kind": "InfraInterfaceL3",
            },
            {
                "name": "GigabitEthernet1/0/5",
                "speed": 1000,
                "role": "spare",
                "kind": "InfraInterfaceL3",
            },
            {
                "name": "GigabitEthernet1/0/6",
                "speed": 1000,
                "role": "spare",
                "kind": "InfraInterfaceL3",
            },
            # Omitted
            {
                "name": "TenGigabitEthernet1/1/3",
                "speed": 10000,
                "role": "upstream",
                "kind": "InfraInterfaceL2",
                "l2_mode": "Trunk",
                "enabled": True,
            },
            {
                "name": "TenGigabitEthernet1/1/4",
                "speed": 10000,
                "role": "spare",
                "kind": "InfraInterfaceL2",
                "l2_mode": "Access",
            },
        ],
    },
    # TODO: Add other examples
}


class ImplementSiteGenerator(InfrahubGenerator):
    async def generate(self, data: dict) -> None:
        # Get the site from data
        site_dict: dict = data["LocationSite"]["edges"][0]["node"]

        # Get interesting informations
        design: str = site_dict["design"]["value"]
        building_block: str = site_dict["building_block"]["value"]

        # Get number of switch to create
        number_of_switches: int = DESIGNS[design]["number_of_switch"]
        switch_template: dict = TEMPLATES[building_block]

        # Prepare the batch object for interfaces
        interface_batch = await self.client.create_batch()

        # Get the resource pool
        pool = await self.client.get(
            kind="CoreIPAddressPool", name__value=IP_MANAGEMENT_POOL
        )
        group = await self.client.get(
            kind="CoreStandardGroup", name__value=DEVICE_GROUP
        )

        # Create switches
        for i in range(1, number_of_switches + 1):  # here we +1 to not have switch 0
            # Create the device object
            device_obj = await self.client.create(
                kind="InfraDevice",
                name=f"switch-0{str(i)}.{site_dict['name']['value']}",
                description="Switch bulding a site.",
                status="active",
                role="cpe",
                site=site_dict["name"]["value"],
                type=switch_template["label"],
                member_of_groups=[group.id],
                primary_address=pool,  # This is where the magic happens
            )

            # .. and save device in DB
            await device_obj.save(allow_upsert=True)

            # Now we add interfaces
            for interface_template in switch_template["interfaces"]:
                # Prepare var for interfaces
                interface_data: dict = {
                    "name": interface_template["name"],
                    "device": device_obj,
                    "speed": interface_template["speed"],
                    "status": "active",  # TODO: Maybe move out of generator
                    "role": interface_template["role"],
                }

                # Manage l2 interface specific point
                if interface_template["kind"] == "InfraInterfaceL2":
                    interface_data["l2_mode"] = interface_template["l2_mode"]

                # If we have enable defined in the template
                if "enabled" in interface_template:
                    interface_data["enabled"] = interface_template["enabled"]

                # Create interface
                interface_obj = await self.client.create(
                    kind=interface_template["kind"], data=interface_data
                )

                # Add save operation to the batch
                interface_batch.add(
                    task=interface_obj.save, node=interface_obj, allow_upsert=True
                )

        # Execute the batch
        async for node, _ in interface_batch.execute():
            pass  # TODO: Improve that part

        # Manage the service part
        services_list: dict = site_dict["services"]["edges"]

        for service in services_list:
            service = service["node"]
            service_type: str = service["service_type"]["value"]

            # Here we are going to create the WIFI related objects
            if service_type == "wifi":
                # First we create the VLAN 444
                vlan_obj = await self.client.create(
                    kind="InfraVLAN",
                    name=f"wifi-{site_dict['name']['value']}",
                    vlan_id=444,
                    description=f"VLAN for wifi on site {site_dict['name']['value']}.",
                    status="active",
                    role="user",
                    site=site_dict["name"]["value"],
                )

                await vlan_obj.save(allow_upsert=True)

                # We first get all devices on that site
                devices = await self.client.filters(
                    kind="InfraDevice",
                    site__name__value=site_dict["name"]["value"],
                    # TODO: add a filter on device role for instance
                    include=["interfaces"],
                )

                # FIXME: Maybe not a good example as scale down isn't right ...

                # Then we seach upstream interfaces to tag the VLAN
                for device in devices:
                    # Looping over interfaces
                    for interface in device.interfaces.peers:
                        # Finding those L2 upstream interfaces
                        if (
                            interface.typename == "InfraInterfaceL2"
                            and interface.peer.role.value == "upstream"
                        ):
                            # Tag vlan
                            await interface.peer.tagged_vlan.fetch()
                            interface.peer.tagged_vlan.add(vlan_obj)
                            await interface.peer.save()
