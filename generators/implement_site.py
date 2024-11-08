from infrahub_sdk import InfrahubClient
from infrahub_sdk.generator import InfrahubGenerator
from infrahub_sdk.node import InfrahubNode
from infrahub_sdk.protocols import CoreIPPrefixPool, CoreNumberPool

PROVISIONING_STATUS = "provisioning"
ACTIVE_STATUS = "active"

# Here we have some design information
# TODO: eventually we would like to capture that in infrahub in a proper design object
DESIGNS = {"single-node": {"number_of_switch": 1}, "ha": {"number_of_switch": 2}}

# Here we have device type information
# TODO: eventually we would like to capture that in infrahub in a device type object
TEMPLATES = {
    "cisco-ws-c3650-24pd-s": {
        "label": "Cisco WS-C3650-24PD-S",
        "interfaces": [
            {
                "name": "GigabitEthernet1/0/1",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/2",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/3",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/4",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/5",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/6",
                "speed": 1000,
            },
            # Omitted
            {"name": "GigabitEthernet1/1/1", "speed": 1000},
            {"name": "GigabitEthernet1/1/2", "speed": 1000},
            {"name": "TenGigabitEthernet1/1/3", "speed": 10000},
            {"name": "TenGigabitEthernet1/1/4", "speed": 10000},
        ],
    },
    "cisco-ws-c3650-48fd-s": {
        "label": "Cisco WS-C3650-48FD-S",
        "interfaces": [
            {
                "name": "GigabitEthernet1/0/1",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/2",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/3",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/4",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/5",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/6",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/7",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/8",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/9",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/10",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/11",
                "speed": 1000,
            },
            {
                "name": "GigabitEthernet1/0/12",
                "speed": 1000,
            },
            # Omitted
            {"name": "GigabitEthernet1/1/1", "speed": 1000},
            {"name": "GigabitEthernet1/1/2", "speed": 1000},
            {"name": "TenGigabitEthernet1/1/3", "speed": 10000},
            {"name": "TenGigabitEthernet1/1/4", "speed": 10000},
        ],
    },
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

        # Create switches
        for i in range(1, number_of_switches + 1):  # here we +1 to not have switch 0
            # Create the device object
            device_obj = await self.client.create(
                kind="InfraDevice",
                name=f"switch-0{str(i)}",
                description="Switch bulding a site.",
                status="active",
                role="cpe",
                site=site_dict["name"]["value"],
                type=switch_template["label"],
            )

            # .. and save device in DB
            await device_obj.save(allow_upsert=True)

            # Now we add interfaces
            is_first_interface: bool = True
            for inteface_template in switch_template["interfaces"]:
                # Prepare var for interfaces
                role: str = "spare"
                enable: bool = False

                # First interface is slighly different
                # Could be 'codify' or supported in profiles, templates ...
                if is_first_interface:
                    role = "upstream"
                    enable = True
                    is_first_interface = False

                # Create interface
                interface_obj = await self.client.create(
                    kind="InfraInterfaceL3",
                    device=device_obj,
                    name=inteface_template["name"],
                    speed=inteface_template["speed"],
                    enabled=enable,
                    status="active",
                    role=role,
                )

                interface_batch.add(
                    task=interface_obj.save, node=interface_obj, allow_upsert=True
                )

        # Execute the batch
        async for node, _ in interface_batch.execute():
            pass
