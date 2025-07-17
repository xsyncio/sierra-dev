import datetime

import sierra.abc.base as sierra_abc_base


class Invoker(sierra_abc_base.SierraABC):
    name: str
    link: str
    date_of_last_edit: datetime.datetime


class Source(sierra_abc_base.SierraABC):
    name: str
    link: str
    date_of_last_edit: datetime.datetime
    invokers: list[Invoker]
    index: int


class LoaderList(sierra_abc_base.SierraABC):
    sources: list[Source]
