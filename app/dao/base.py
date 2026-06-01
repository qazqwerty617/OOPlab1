class BaseDAO:
    def __init__(self, connection_factory):
        self._connection_factory = connection_factory
