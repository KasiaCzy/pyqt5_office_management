from enum import IntEnum


class UserData(IntEnum):
    ID = 0
    NAME = 1
    PASSWORD = 2


class TaskData(IntEnum):
    ID = 0
    NAME = 1
    STATUS = 2
    USER_ID = 3


class EntryData(IntEnum):
    ID = 0
    DATE = 1
    NOTE = 2
    TASK_ID = 3
    USER_ID = 4


class EventData(IntEnum):
    ID = 0
    NAME = 1
    DATE = 2
    NOTE = 3
    USER_ID = 4