class GradeNotFoundError(Exception):
    pass


class StudentNotFoundForGradeError(Exception):
    pass


class ClassRoomNotFoundForGradeError(Exception):
    pass


class CatalogTypeNotFoundError(Exception):
    pass


class SubjectNotFoundForGradeError(Exception):
    pass


class GradeVersionConflictError(Exception):
    pass
