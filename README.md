# Workshop 20241111

Repository containing some resources to learn how to build generators with Infrahub.

Preparation:

```console
# Start the demo
invoke demo.start

# Load the schema
invoke demo.load-infra-schema

# Load the data
invoke demo.load-infra-data

# Load schema extension
infrahubctl schema load schemas/site-extension.yml

# Create a group called `automated_sites`
```

Demo:

```console
# Connect repository
# Wait for it to be in sync
# Create a branch
# Create a site and add it to the group
# Create a proposed change
```

Dev:

```console
# Run generator
infrahubctl generator implement_site site_name="my-site-123"
```
