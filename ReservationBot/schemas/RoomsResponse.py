from pydantic import BaseModel


class RoomsResponse(BaseModel):
    number: str
    type_class: str
    places: int
    computer_places: int
    multimedia: bool | None
    description: str | None
