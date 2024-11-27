from infrahub_sdk.transforms import InfrahubTransform


class DeviceCisco(InfrahubTransform):
    query = "device_info2"

    async def transform(self, data):
        response = {}

        for device in data["InfraDevice"]["edges"]:
            device_name = device["node"]["name"]["value"]
            response[device_name] = {"interfaces": {}}

            for intf in device["node"]["interfaces"]["edges"]:
                intf_name = intf["node"]["name"]["value"]
                intf_data = {}

                # Interface description
                description_value = intf["node"].get("description", {}).get("value")
                intf_data["description"] = description_value if description_value is not None else "FREE"

                # Interface status (enabled/disabled)
                intf_data["enabled"] = intf["node"].get("enabled", {}).get("value", True)

                # # IP addresses assigned to the interface
                # ip_addresses = []
                # if intf["node"].get("ip_addresses"):
                #     for ip_edge in intf["node"]["ip_addresses"]["edges"]:
                #         ip_addresses.append(ip_edge["node"]["address"]["value"])
                # intf_data["ip_addresses"] = ip_addresses

                # # Interface role for OSPF configuration
                # intf_data["role"] = intf["node"].get("role", {}).get("value", None)

                # # VLAN information
                # if intf["node"].get("untagged_vlan") and intf["node"]["untagged_vlan"].get("node"):
                #     intf_data["untagged_vlan"] = intf["node"]["untagged_vlan"]["node"]["vlan_id"]["value"]

                # if intf["node"].get("tagged_vlan") and intf["node"]["tagged_vlan"].get("edges"):
                #     tagged_vlans = [
                #         vlan_edge["node"]["vlan_id"]["value"]
                #         for vlan_edge in intf["node"]["tagged_vlan"]["edges"]
                #     ]
                #     intf_data["tagged_vlans"] = tagged_vlans

                # Add interface data to response
                response[device_name]["interfaces"][intf_name] = intf_data

        return response