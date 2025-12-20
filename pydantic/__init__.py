from typing import Any, Dict


def Field(default: Any = ..., **kwargs):
    return default if default is not ... else None


class BaseModel:
    def __init__(self, **data: Any):
        for key, value in data.items():
            setattr(self, key, value)

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}

    class Config:
        from_attributes = True
