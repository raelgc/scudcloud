import os

INSTALL_DIR = '/opt/scudcloud'


def get_resource_path(filename):
    return os.path.join(INSTALL_DIR, 'resources', filename)
