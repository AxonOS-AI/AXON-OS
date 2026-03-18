# Axon OS — Add-on Manifest

Each add-on must have a `.axonplugin` descriptor file with:

```ini
[addon]
id=my_addon
name=My Addon
version=1.0.0
description=What this addon does
entry=main.py
layer=platform
requires=
```

Place descriptor in: platform/addons/
Place code in:       platform/addons/<id>/

The add-on loader (02-enable-extensions.sh) scans this directory
and registers valid add-ons with the desktop shell.
