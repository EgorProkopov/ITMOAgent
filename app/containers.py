from dependency_injector import containers, providers
from omegaconf import OmegaConf
import logging

from app.model import ChatModel


class AppContainer(containers.DeclarativeContainer):
    logging.basicConfig(level=logging.INFO)
    logger = providers.Singleton(logging.getLogger, __name__)
    config = providers.Singleton(OmegaConf.load, "configs/main_config.yaml")

    chat_model = providers.Singleton(ChatModel, config=config, logger=logger)
