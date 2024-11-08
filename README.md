# Workshop 20241111

Repository containing some resources to learn how to build generators with Infrahub.

```console
# Start the demo
invoke demo.start

# Load the schema
invoke demo.load-infra-schema

# Load the data
invoke demo.load-infra-data

# Load schema extension
infrahubctl schema load schemas/site-extension.yml

# Create a new site + add a service to it

# Run generator
infrahubctl generator implement_site site_name="my-site-123"
```

infrahubctl generator implement_site site_name="my-site"
