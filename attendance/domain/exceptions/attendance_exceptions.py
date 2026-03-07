class AttendanceAlreadyExistsError(Exception):
    pass


class AttendanceNotFoundError(Exception):
    pass


class StudentNotFoundForAttendanceError(Exception):
    pass


class StateCodeNotFoundError(Exception):
    pass


class ClassRoomNotFoundError(Exception):
    pass
