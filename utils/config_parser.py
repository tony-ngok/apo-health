import configparser

config = configparser.ConfigParser()


def get_config(path):
    config.read(path)
    return config


def get_section(path, section):
    config = get_config(path)
    return config[section]


if __name__ == "__main__":
    import os

    config_path: str = os.path.expanduser(os.path.join("~", ".em-spider", "config.ini"))
    section = get_section(config_path, "elastic.product.import.web.uk")
