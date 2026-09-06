import statistics
from src.data_models import PriceGroup, StationPrice


def extract_prices(stations):
    """Agrupa precios nacionales por codigo de combustible."""
    prices: dict[str, PriceGroup] = {}
    for station in stations:
        for fuel, info in (station.get('precios') or {}).items():
            try:
                precio = float(info['precio'])
            except (KeyError, TypeError, ValueError):
                continue
            fuel_data = prices.setdefault(
                fuel, {'unidad': info.get('unidad_cobro'), 'precios': []})
            fuel_data['precios'].append(precio)
    return prices


def extract_prices_by_commune(stations):
    """Agrupa precios por comuna, region y combustible."""
    by_commune = {}
    for station in stations:
        location = station.get('ubicacion') or {}
        commune = location.get('nombre_comuna')
        if not commune:
            continue
        key = (commune, location.get('nombre_region') or '')
        commune_prices = by_commune.setdefault(key, {})
        for fuel, info in (station.get('precios') or {}).items():
            try:
                precio = float(info['precio'])
            except (KeyError, TypeError, ValueError):
                continue
            commune_prices.setdefault(fuel, []).append(precio)
    return by_commune


def extract_station_details_by_commune(stations):
    """Conserva identidad, ubicacion y precio de cada estacion."""
    station_details: dict[tuple[str, str], dict[str, list[StationPrice]]] = {}
    for station in stations:
        location = station.get('ubicacion') or {}
        commune = location.get('nombre_comuna')
        if not commune:
            continue
        key = (commune, location.get('nombre_region') or '')
        commune_stations = station_details.setdefault(key, {})
        station_name = (
            station.get('razon_social')
            or (station.get('distribuidor') or {}).get('marca')
            or 'Estacion sin nombre'
        )
        for fuel, info in (station.get('precios') or {}).items():
            try:
                precio = float(info['precio'])
            except (KeyError, TypeError, ValueError):
                continue
            commune_stations.setdefault(fuel, []).append({
                'nombre': station_name,
                'marca': (station.get('distribuidor') or {}).get('marca')
                or 'Marca no disponible',
                'direccion': location.get('direccion')
                or 'Direccion no disponible',
                'precio': precio,
            })
    return station_details


# Funciones de agregación disponibles para los rankings por comuna
STAT_FUNCS = {
    'promedio': statistics.mean,
    'mediana': statistics.median,
    'moda': statistics.mode,
}


def top_communes(by_commune, fuel, stat, limit=10, min_estaciones=1,
                 selected_region=None, descending=True):
    """Ranking de comunas por estadístico de precio de un combustible.

    Retorna lista de dicts ordenada de mayor a menor:
    [{'comuna': ..., 'region': ..., 'valor': ..., 'estaciones': ...}, ...]
    min_estaciones filtra comunas con muy pocas estaciones (evita que
    comunas con n=1 dominen el ranking). Si region no es None, limita
    el ranking a esa region. descending=False muestra las comunas mas baratas.
    """
    if stat not in STAT_FUNCS:
        raise ValueError(f'Estadístico no soportado: {stat!r}. '
                         f'Usa uno de: {list(STAT_FUNCS)}')
    func = STAT_FUNCS[stat]
    rows = []
    for (comuna, region), fuels in by_commune.items():
        if selected_region is not None and region != selected_region:
            continue
        valores = fuels.get(fuel)
        if not valores or len(valores) < min_estaciones:
            continue
        rows.append({
            'comuna': comuna,
            'region': region,
            'valor': func(valores),
            'estaciones': len(valores),
        })
    rows.sort(key=lambda r: r['valor'], reverse=descending)
    return rows[:limit]


def commune_stats(by_commune, commune_key, fuel):
    """Calcula las tres estadisticas para una comuna y combustible."""
    valores = by_commune[commune_key].get(fuel, [])
    if not valores:
        return None
    return {
        'promedio': statistics.mean(valores),
        'mediana': statistics.median(valores),
        'moda': statistics.mode(valores),
        'min': min(valores),
        'max': max(valores),
        'estaciones': len(valores),
    }



