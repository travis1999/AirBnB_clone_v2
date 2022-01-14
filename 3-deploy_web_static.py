#!/usr/bin/python3
# Fabfile to create and distribute an archive to a web server.
import os.path
from datetime import datetime


from fabric.api import env
from fabric.api import local
from fabric.api import put
from fabric.api import run, sudo


env.hosts = ["34.74.227.185", "100.24.126.241"]


def do_pack():
    """Create a tar gzipped archive of the directory web_static."""
    dt = datetime.utcnow()

    attrs = ["year", "month", "day", "hour", "minute", "second"]
    path_is = f"versions/web_static_{''.join(str(getattr(dt, x)) for x in attrs)}.tgz"
    
    if (
        os.path.isdir("versions") is False
        and local("mkdir -p versions").failed is True
    ):
        return None
    if local("tar -cvzf {} web_static".format(path_is)).failed is True:
        return None
    return path_is


def do_deploy(archive_path):
    """Distributes an archive to a web server.
    Args:
        archive_path (str): The path of the archive to distribute.
    Returns:
        If the file doesn't exist at archive_path or an error occurs - False.
        Otherwise - True.
    """
    if not os.path.isfile(archive_path):
        return False
    
    file = archive_path.split("/")[-1]
    name = file.split(".")[0]

    if put(archive_path, f"/tmp/{file}").failed:
        return False


    to_run = [
        f"rm -rf /data/web_static/releases/{name}/",
        f"mkdir -p /data/web_static/releases/{name}/",
        f"tar -xzf /tmp/{file} -C /data/web_static/releases/{name}/",
        f"rm /tmp/{file}",
        f"mv /data/web_static/releases/{name}/web_static/* "
        f"/data/web_static/releases/{name}/",
        f"rm -rf /data/web_static/releases/{name}/web_static",
        "rm -rf /data/web_static/current",
        f"ln -s /data/web_static/releases/{name}/ /data/web_static/current"
    ]
    return not any(sudo(command).failed for command in to_run)


def deploy():
    """Create and distribute an archive to a web server."""
    file = do_pack()
    if not file:
        return False
    return do_deploy(file)