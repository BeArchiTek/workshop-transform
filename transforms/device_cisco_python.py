from infrahub_sdk.transforms import InfrahubTransform


class DeviceCisco(InfrahubTransform):
    query = "device_info"

    async def transform(self, data):
        response = {}

        for device in data["InfraDevice"]["edges"]:
            for intf in device["node"]["interfaces"]["edges"]:
                intf_name = intf["node"]["name"]["value"]
                intf_description = intf["node"]["description"]["value"]
                response[intf_name] = intf_description

        return response