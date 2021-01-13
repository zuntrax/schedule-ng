import logging
import json

from ..base import ExportHandler
from fahrplan.model.schedule import Schedule
from fahrplan.datetime import format_duration, format_date, format_datetime, format_time


log = logging.getLogger(__name__)


class FrabJsonExportHandler(ExportHandler):
    content_type = "application/json"

    def export(self, schedule: Schedule) -> str:
        content = self.get_data(schedule)
        return json.dumps({"schedule": content}, ensure_ascii=False, sort_keys=True, indent=2)

    def get_data(self, schedule):
        """
        adapted from FrabJsonExporter of the pretalx.org project, Licensed under the Apache License
        https://github.com/pretalx/pretalx/blob/master/src/pretalx/schedule/exporters.py#L143
        """
        return {
            "version": schedule.version,
            "base_url": None, # we don't have this information
            "conference": {
                "acronym": schedule.conference.acronym,
                "title": schedule.conference.title,
                "start": format_date(schedule.conference.get_start()),
                "end": format_date(schedule.conference.get_end()),
                "daysCount": schedule.conference.day_count,
                "timeslot_duration": format_duration(schedule.conference.time_slot_duration),
                "days": [
                    {
                        "index": day.index,
                        "date": format_date(day.date),
                        "day_start": format_datetime(day.get_start().astimezone()),
                        "day_end": format_datetime(day.get_end().astimezone()),
                        "rooms": {
                            str(room.name): [
                                {
                                    "id": event.id,
                                    "guid": event.guid,
                                    "logo": event.logo,
                                    "date": format_datetime(event.date.astimezone()),
                                    "start": format_time(event.start),
                                    "duration": format_duration(event.duration),
                                    "room": str(room.name),
                                    "slug": event.slug,
                                    "url": None, # we don't have this information
                                    "title": event.title,
                                    "subtitle": event.subtitle,
                                    "track": event.track,
                                    "type": event.type,
                                    "language": event.language,
                                    "abstract": event.abstract,
                                    "description": event.description,
                                    "recording_license": event.rec_license,
                                    "do_not_record": bool(event.rec_optout),
                                    **({"video_download_url": event.download_url} if event.download_url else {}),
                                    "persons": [
                                        {
                                            "id": person[0],
                                            "public_name": person[1]
                                        }
                                        for person in event.persons.items()
                                    ],
                                    "links": [
                                        {
                                            "url": link[0],
                                            "title": link[1]
                                        }
                                        for link in event.links.items()
                                    ],
                                    "attachments": [
                                        {
                                            "url": attachment[0],
                                            "title": attachment[1]
                                        }
                                        for attachment in event.attachments.items()
                                    ],
                                }
                                for event in room.events.values()
                            ]
                            for room in day.rooms.values()
                        },
                    }
                    for day in schedule.days.values()
                ],
            },
        }
