import os.path
import pylons
from paste.deploy import appconfig


def easy_app_init(ini_path):
    ini_path = os.path.abspath(ini_path)
    assert os.path.exists(ini_path)

    # Initialize Pylons app
    conf = appconfig('config:' + ini_path)
    import debexpo.config.environment
    pylons.config = debexpo.config.environment \
        .load_environment(conf.global_conf, conf.local_conf)
