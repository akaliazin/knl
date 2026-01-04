"""MkDocs hooks for custom build steps."""

import shutil
from pathlib import Path


def on_post_build(config, **kwargs):
    """
    Copy install.sh to the built site after build completes.

    This ensures the installer script is available at:
    https://akaliazin.github.io/knl/install.sh
    """
    # Source: docs/install.sh
    # Destination: site/install.sh
    source = Path("docs/install.sh")
    destination = Path(config["site_dir"]) / "install.sh"

    if source.exists():
        shutil.copy2(source, destination)
        print(f"✓ Copied install.sh to {destination}")
    else:
        print(f"⚠ Warning: {source} not found, skipping copy")
