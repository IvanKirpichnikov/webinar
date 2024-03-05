from dishka import provide, Provider, Scope

from webinar.config import Config, ConfigFactory


class GatewayProvider(Provider):
    @provide(scope=Scope.APP)
    def config_factory(self) -> ConfigFactory:
        return ConfigFactory()
    
    @provide(scope=Scope.APP)
    def config(self, config_factory: ConfigFactory) -> Config:
        return config_factory.config
