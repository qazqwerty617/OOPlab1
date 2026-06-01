import re
from dataclasses import dataclass

@dataclass
class Route:
    method: str
    pattern: str
    controller: object
    action: str

class Router:
    def __init__(self):
        self._routes: list[Route] = []

    def add(self, method: str, pattern: str, controller: object, action: str):
        self._routes.append(Route(method.upper(), pattern, controller, action))

    def resolve(self, method: str, path: str):
        for route in self._routes:
            match = re.fullmatch(route.pattern, path)
            if route.method == method.upper() and match:
                return getattr(route.controller, route.action), match.groupdict()
        return None, {}
