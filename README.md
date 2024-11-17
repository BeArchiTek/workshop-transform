# Workshop 20241111

Repository containing some resources to learn how to build generators with Infrahub.

## Preparation:

1. From the main repository Infrahub :

```console
# Start the demo
invoke demo.start

# Load the schema
invoke demo.load-infra-schema

# Load the data
invoke demo.load-infra-data

2. From this repository :
```console
# Load schema extension
infrahubctl schema load schemas/site-extension.yml
```

3. Create a group called `automated_sites` via the UI


## Demo:

```console
# Connect repository
# Wait for it to be in sync
# Create a branch
# Create a site `my-site-123` with the block `cisco-ws-c3650-24pd-s` and add it to the group `automated_sites`
# Create a proposed change
```

## Dev:

```console
# Run generator
infrahubctl generator implement_site site_name="my-site-123"
```
