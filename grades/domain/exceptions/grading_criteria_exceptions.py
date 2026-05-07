class GradingCriteriaException(Exception):
    pass

class GradingCriteriaNotFoundError(GradingCriteriaException):
    pass

class GradingCriteriaAlreadyExistsError(GradingCriteriaException):
    pass

class GradingCriteriaInvalidError(GradingCriteriaException):
    pass

class GradingCriteriaNotFoundForSubjectError(GradingCriteriaException):
    pass