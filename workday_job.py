import dataclasses


@dataclasses.dataclass
class WDJob:
    title: str
    location: str
    description: str
    url: str

    def __str__(self):
        return f'Title: {self.title}, Location: {self.location}, Description: {self.description}, URL: {self.url}'
