from typing import TypedDict


class PriceGroup(TypedDict):
    unidad: str | None
    precios: list[float]


class StationPrice(TypedDict):
    nombre: str
    marca: str
    direccion: str
    precio: float


# Nombres legibles para los tipos de combustible desde API CNE
FUEL_NAMES = {
    '93': 'Bencina 93', 'A93': 'Bencina 93 (aditivada)',
    '95': 'Bencina 95', 'A95': 'Bencina 95 (aditivada)',
    '97': 'Bencina 97', 'A97': 'Bencina 97 (aditivada)',
    'DI': 'Diésel', 'ADI': 'Diésel (aditivado)',
    'KE': 'Kerosene', 'AKE': 'Kerosene (aditivado)',
    'GLP': 'Gas licuado (GLP)', 'GNC': 'Gas natural (GNC)',
}
