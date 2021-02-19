from __future__ import annotations

from pathlib import Path
import yaml
from collections import namedtuple

DEFAULT_CONFIGS = {
    "debug": False,
    "providers": [],
    "controllers": [{
        "cli": True
    }]
}


def get_configs():
    configs = DEFAULT_CONFIGS.copy()

    config_path = Path('./config.yaml')
    if not config_path.exists():
        return namedtuple('Configurations', configs.keys())(**configs)

    with open("config.yaml", "r") as config_file:
        provided_configs = yaml.load(config_file, Loader=yaml.FullLoader)

    configs['debug'] = provided_configs.get(
        'debug') if provided_configs.get('debug') is not None else configs['debug']
    configs['providers'] = provided_configs.get(
        'providers') or configs['providers']
    configs['controllers'] = provided_configs.get(
        'controllers') or configs['controllers']

    return namedtuple('Configurations', configs.keys())(**configs)
