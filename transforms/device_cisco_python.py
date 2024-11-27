from infrahub_sdk.transforms import InfrahubTransform


class DeviceCisco(InfrahubTransform):
    query = "device_info2"

    async def transform(self, data):
        response = []

        for device in data["InfraDevice"]["edges"]:
            for intf in device["node"]["interfaces"]["edges"]:
                intf_name = intf["node"]["name"]["value"]
                description = intf["node"].get("description", {}).get("value", "FREE")

                response.append(f"interface {intf_name}")
                if description:
                    response.append(f"  description {description}")
                response.append("!")

        return "\n".join(response)
