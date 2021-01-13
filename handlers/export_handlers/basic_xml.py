import logging

from ..base import ExportHandler
from fahrplan.model.schedule import Schedule
from hacks import noexcept
from util import write_output


log = logging.getLogger(__name__)


class BasicXMLExportHandler(ExportHandler):
    content_type = "application/xml"

    def export(self, schedule: Schedule) -> str:
        return schedule.to_xml(extended=False)
