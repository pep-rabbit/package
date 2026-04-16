import msgspec
from litestar import Router, get
from src.core.logic import get_top_pharmacies


class PharmacyInfo(msgspec.Struct):
    legal_entity_name: str
    division_name: str
    division_addresses: str
    division_phone: str
    division_type: str
    division_settlement: str
    activity_score: float


@get("/top-pharmacies")
async def top_pharmacies(
    city: str,
    medical_program: str,
) -> list[PharmacyInfo]:
    pharmacies = await get_top_pharmacies(city, medical_program)
    return [PharmacyInfo(**pharmacy) for pharmacy in pharmacies.to_dicts()]


router = Router(path="/api", route_handlers=[top_pharmacies])
