#!/usr/bin/python3
# Fabfile to generates a .tgz archive from the contents of web_static.
import os.path
from datetime import datetime
from fabric.api import local


def do_pack():
    """Create a tar gzipped archive of the directory web_static."""
    dt = datetime.utcnow()

    attrs = ["year", "month", "day", "hour", "minute", "second"]
    path_is = f"versions/web_static_{''.join(getattr(dt, x) for x in attrs)}.tgz"
    
    if (
        os.path.isdir("versions") is False
        and local("mkdir -p versions").failed is True
    ):
        return None
    if local("tar -cvzf {} web_static".format(path_is)).failed is True:
        return None
    return path_is