import logging

from abc import ABCMeta, abstractmethod
from configparser import ConfigParser

from fahrplan.model.schedule import Schedule
from hacks import noexcept
from util import write_output

log = logging.getLogger(__name__)

class HandlerBase(metaclass=ABCMeta):
    def __init__(self, name: str, config: ConfigParser, global_config: ConfigParser):
        self.name = name
        self.config = config
        self.global_config = global_config


class ImportHandler(HandlerBase, metaclass=ABCMeta):
    @abstractmethod
    def run(self) -> Schedule:
        pass


class ExportHandler(HandlerBase, metaclass=ABCMeta):
    content_type = None

    @noexcept(log)
    def run(self, schedule: Schedule) -> bool:
        return write_output(self.config["path"], self.export(schedule))

    @abstractmethod
    def export(self, schedule: Schedule) -> str:
        pass
