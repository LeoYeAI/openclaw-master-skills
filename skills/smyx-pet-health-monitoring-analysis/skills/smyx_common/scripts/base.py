class BaseUtil:
    pass


class BaseMixin:
    pass


class BaseDao:
    pass


class BaseService:
    def __init__(self):
        super().__init__()


class BaseApiService(BaseService):
    INSTANCE = None

    def __init__(self):
        super().__init__()

    @classmethod
    def get_instance(cls):
        if cls.INSTANCE is None:
            cls.INSTANCE = cls()
        return cls.INSTANCE


class BaseSkill:
    def __init__(self):
        super().__init__()
