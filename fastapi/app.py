import inspect
from contextlib import ExitStack
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from . import status


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class Depends:
    def __init__(self, dependency: Callable):
        self.dependency = dependency


@dataclass
class Route:
    method: str
    path: str
    endpoint: Callable
    status_code: Optional[int] = None


class FastAPI:
    def __init__(self, title: str = "", version: str = ""):
        self.title = title
        self.version = version
        self.routes: List[Route] = []

    def _register(self, method: str, path: str, **kwargs):
        def decorator(func: Callable):
            self.routes.append(Route(method=method.upper(), path=path, endpoint=func, status_code=kwargs.get("status_code")))
            return func

        return decorator

    def get(self, path: str, **kwargs):
        return self._register("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._register("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self._register("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs):
        return self._register("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._register("DELETE", path, **kwargs)

    def find_route(self, method: str, path: str) -> Tuple[Route, Dict[str, Any]]:
        for route in self.routes:
            params = match_path(route.path, path)
            if route.method == method.upper() and params is not None:
                return route, params
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")


def match_path(template: str, path: str) -> Optional[Dict[str, Any]]:
    template_parts = template.strip("/").split("/")
    path_parts = path.strip("/").split("/")
    if len(template_parts) != len(path_parts):
        return None

    params: Dict[str, Any] = {}
    for t, p in zip(template_parts, path_parts):
        if t.startswith("{") and t.endswith("}"):
            params[t.strip("{} ")] = p
        elif t != p:
            return None
    return params


class Response:
    def __init__(self, status_code: int, json_data: Any = None):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data


class TestClient:
    __test__ = False

    def __init__(self, app: FastAPI):
        self.app = app

    def _call(self, method: str, path: str, json: Any = None) -> Response:
        route, path_params = self.app.find_route(method, path)
        try:
            with ExitStack() as stack:
                kwargs: Dict[str, Any] = {}
                sig = inspect.signature(route.endpoint)
                for name, param in sig.parameters.items():
                    if name in path_params:
                        kwargs[name] = _convert_type(param.annotation, path_params[name])
                    elif isinstance(param.default, Depends):
                        dep = param.default.dependency()
                        if inspect.isgenerator(dep):
                            value = next(dep)
                            stack.callback(dep.close)
                            dep = value
                        elif hasattr(dep, "__enter__") and hasattr(dep, "__exit__"):
                            dep = stack.enter_context(dep)
                        kwargs[name] = dep
                    elif json is not None and param.default is inspect.Parameter.empty:
                        if inspect.isclass(param.annotation) and hasattr(param.annotation, "__mro__"):
                            kwargs[name] = param.annotation(**json)
                        else:
                            kwargs[name] = json
                result = route.endpoint(**kwargs)
                code = route.status_code or status.HTTP_200_OK
                return Response(code, _serialize(result))
        except HTTPException as exc:  # type: ignore[no-untyped-def]
            return Response(exc.status_code, {"detail": exc.detail})

    def get(self, path: str):
        return self._call("GET", path)

    def post(self, path: str, json: Any = None):
        return self._call("POST", path, json=json)

    def put(self, path: str, json: Any = None):
        return self._call("PUT", path, json=json)

    def patch(self, path: str, json: Any = None):
        return self._call("PATCH", path, json=json)

    def delete(self, path: str):
        return self._call("DELETE", path)


def _serialize(obj: Any):
    if obj is None:
        return None
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        data = {}
        for key, value in obj.__dict__.items():
            if hasattr(value, "isoformat"):
                data[key] = value.isoformat()
            else:
                data[key] = value
        return data
    return obj


def _convert_type(annotation, value: Any):
    try:
        if annotation is int:
            return int(value)
    except Exception:
        pass
    return value
