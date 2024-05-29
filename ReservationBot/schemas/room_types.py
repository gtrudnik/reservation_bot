from enum import Enum


class RoomTypes(str, Enum):
    lecture_room = 'лекционная'
    practice_room = 'практическая'
    meeting_room = "переговорная"
