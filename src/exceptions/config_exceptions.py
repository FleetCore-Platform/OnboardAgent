class ConfigError(Exception):
    pass


class ConfigValueError(ConfigError):
    pass


class ConfigTypeError(ConfigError):
    pass
