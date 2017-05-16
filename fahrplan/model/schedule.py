from datetime import date as _date, timedelta
from typing import Dict, List

from fahrplan.xml import XmlWriter, XmlSerializable
from .conference import Conference
from .day import Day
from .event import Event
from .room import Room


class Schedule(XmlSerializable):
    def __init__(self, conference: Conference, days: Dict[int, Day] = None, version: str = "1.0"):
        self.conference = conference

        if days:
            assert len(days) == conference.day_count
            self.days = days
        else:
            self.days = {}
            for i in range(conference.day_count):
                index = i + 1
                date: _date = conference.start + timedelta(i)
                self.days[index] = Day(index=index, date=date)

        self.version = version

    def add_room(self, name: str, day_filter: List[int] = None):
        """
        Adds a room to the days given in day_filter, or all days.
        :param name: Name of the room to be added.
        :param day_filter: List of day indices to create the room for. If empty, use all days.
        :return: None
        """
        for day in self.days.values():
            if not day_filter or day.index in day_filter:
                day.add_room(Room(name))

    def add_event(self, day: int, room: str, event: Event):
        self.days[day].add_event(room, event)

    def append_xml(self, xml: XmlWriter):
        with xml.context("schedule"):
            xml.tag("version", self.version)
            xml.append_object(self.conference)
            for day in self.days.values():
                xml.append_object(day)
