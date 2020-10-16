import simplejson as json

CONFIG_NAME = 'config.json'


class Config(object):
    def __init__(self, json_config):
        for key, value in json_config.items():
            setattr(self, key, value)


class ConfigLoader:

    def __load_config(self, file_name):
        with open(file_name) as f:
            config = json.load(f, encoding='utf-8')
        return config

    def get_config(self):
        try:
            cfg = self.__load_config(CONFIG_NAME)
        except FileNotFoundError as e:
            raise RuntimeError('Config not found. Error: {}'.format(e))
        else:
            return Config(cfg)


config = ConfigLoader().get_config()
