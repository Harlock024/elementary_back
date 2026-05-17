from dataclasses import dataclass

@dataclass(frozen=True)
class GroupEntity:
    letter: str
    school_grade_id: str

    def __post_init__(self):
        if not self.letter or not self.letter.strip():
            raise ValueError("letter is required")
        if not self.school_grade_id or not self.school_grade_id.strip():
            raise ValueError("school_grade_id is required")
        
@dataclass(frozen=True)
class SubjectEntity:
    name: str
    description: str
    school_grade_id: str

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("name is required")
        if not self.description or not self.description.strip():
            raise ValueError("description is required")
        if not self.school_grade_id or not self.school_grade_id.strip():
            raise ValueError("school_grade_id is required")
        


@dataclass(frozen=True)
class ClassRoomEntity:
    group_id: str
    staff_id: str

    def __post_init__(self):
        if not self.group_id or not self.group_id.strip():
            raise ValueError("group_id is required")
        if not self.staff_id or not self.staff_id.strip():
            raise ValueError("staff_id is required")

@dataclass(frozen=True)
class EnrollmentEntity:
    student_id: str
    group_id: str
    period: str
    state: str

    def __post_init__(self):
        if not self.student_id or not self.student_id.strip():
            raise ValueError("student_id is required")
        if not self.group_id or not self.group_id.strip():
            raise ValueError("group_id is required")
        if not self.period or not self.period.strip():
            raise ValueError("period is required")
        if not self.state or not self.state.strip():
            raise ValueError("state is required")