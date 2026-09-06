import statistics

import matplotlib.pyplot as plt
import streamlit as st

import src.api_client as api
from src.data_models import (
    FUEL_NAMES,
)
from src.data_processing import (
    commune_stats,
    extract_prices,
    extract_prices_by_commune,
    extract_station_details_by_commune,
    top_communes,
)


@st.cache_data(ttl=3600, show_spinner='Descargando datos del CNE...')
def load_data():
    """Descarga y procesa las estaciones una sola vez por hora.

    Retorna (precios_por_combustible, precios_por_comuna, n_estaciones).
    Se cachean dicts simples, más robustos que la respuesta cruda.
    """
    stations = api.get_estaciones()
    return (
        extract_prices(stations),
        extract_prices_by_commune(stations),
        extract_station_details_by_commune(stations),
        len(stations),
    )


CHART_STYLES = {
    'promedio': {'color': '#F4B942', 'title': 'Precio promedio'},
    'mediana': {'color': '#F2776B', 'title': 'Precio mediano'},
    'moda': {'color': '#62D2A2', 'title': 'Precio modal'},
}

FUEL_ORDER = ['93', 'A93', '95', 'A95', '97', 'A97',
              'DI', 'ADI', 'KE', 'AKE', 'GLP', 'GNC']


def plot_top_communes(ax, rows, titulo, unidad, color):
    """Dibuja un ranking vertical con escala ajustada al rango real."""
    etiquetas = [r['comuna'] for r in rows]
    valores = [r['valor'] for r in rows]
    ax.set_facecolor('#20262B')
    ax.figure.set_facecolor('#20262B')
    bars = ax.bar(etiquetas, valores, color=color, alpha=0.92, label=titulo)
    ax.set_title(titulo, color='#F5F1E8', loc='left', pad=14,
                 fontweight='bold')
    ax.set_ylabel(f'Precio ({unidad})', color='#B7C0C5')
    ax.tick_params(axis='both', colors='#DCE2E5')
    ax.tick_params(axis='x', labelrotation=35)
    ax.grid(axis='y', color='#526067', alpha=0.35, linewidth=0.8)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    value_range = max(valores) - min(valores)
    padding = max(value_range * 0.35, max(valores) * 0.005)
    ax.set_ylim(min(valores) - padding, max(valores) + padding)
    for bar, row in zip(bars, rows):
        ax.annotate(f"{row['valor']:.0f}\n(n={row['estaciones']})",
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 5), textcoords='offset points', ha='center',
                    va='bottom', fontsize=8, color='#F5F1E8')
    ax.legend(loc='lower right', facecolor='#20262B', edgecolor='#526067',
              labelcolor='#F5F1E8', framealpha=0.9)
    ax.margins(x=0.04)


st.title('Precios de Combustibles en Chile (CNE)')

try:
    prices, by_commune, station_details, n_stations = load_data()
except RuntimeError as e:
    st.error(f'{e}\n\nRenueva el JWT en `src/api_client.py` (variable `TOKEN`) '
             f'y recarga la página.')
    st.stop()

st.caption(f'{n_stations} estaciones · datos de api.cne.cl')

# Controles: hoy fijos en la barra lateral, fáciles de mover a columnas después
with st.sidebar:
    st.header('Filtros')
    if st.button('Actualizar datos', use_container_width=True,
                 help='Descarga nuevamente los precios desde la API del CNE.'):
        load_data.clear()
        st.rerun()
    regions = sorted({region for _, region in by_commune if region})
    metropolitan_region = next(
        (region for region in regions if 'Metropolitana' in region),
        regions[0] if regions else 'Todas las regiones',
    )
    region_options = ['Todas las regiones'] + regions
    region = st.selectbox(
        'Región',
        options=region_options,
        index=region_options.index(metropolitan_region)
        if metropolitan_region in region_options else 0,
    )
    ordered_fuels = sorted(
        prices,
        key=lambda fuel_code: (
            FUEL_ORDER.index(fuel_code)
            if fuel_code in FUEL_ORDER else len(FUEL_ORDER),
            FUEL_NAMES.get(fuel_code, fuel_code),
        ),
    )
    fuel = st.selectbox(
        'Combustible',
        options=ordered_fuels,
        format_func=lambda f: FUEL_NAMES.get(f, f),
        index=ordered_fuels.index('93') if '93' in ordered_fuels else 0,
    )
    top_n = st.slider('Comunas a mostrar', min_value=5, max_value=25, value=10)
    reliability_options = {
        'Todas las comunas': 1,
        'Al menos 2 estaciones': 2,
        'Al menos 3 estaciones (recomendado)': 3,
        'Al menos 5 estaciones': 5,
        'Al menos 10 estaciones': 10,
    }
    reliability = st.selectbox(
        'Confiabilidad del ranking',
        options=list(reliability_options),
        index=2,
        help='Las comunas con más estaciones producen estadísticas más '
             'representativas.',
    )
    min_est = reliability_options[reliability]
    ranking_direction = st.radio(
        'Orden del ranking',
        options=['Más caras', 'Más baratas'],
        horizontal=True,
    )

unidad = prices[fuel]['unidad']
nombre = FUEL_NAMES.get(fuel, fuel)
selected_region = None if region == 'Todas las regiones' else region

region_values = [
    value
    for (commune, commune_region), fuels in by_commune.items()
    if selected_region is None or commune_region == selected_region
    for value in fuels.get(fuel, [])
]

if region_values:
    metric_columns = st.columns(4)
    metric_columns[0].metric(f'Promedio ({unidad})',
                             f'{sum(region_values) / len(region_values):.1f}')
    metric_columns[1].metric(f'Mediana ({unidad})',
                             f'{statistics.median(region_values):.1f}')
    metric_columns[2].metric(f'Moda ({unidad})',
                             f'{statistics.mode(region_values):.1f}')
    metric_columns[3].metric('Estaciones', len(region_values))

st.header(f'Top {top_n} comunas — {nombre}')
st.caption(f'{region if selected_region else "Todas las regiones"} · '
           f'{ranking_direction.lower()}')

chart_tabs = st.tabs(['Promedio', 'Mediana', 'Moda'])

# Tres rankings: promedio, mediana y moda
for tab, (stat, etiqueta) in zip(
        chart_tabs,
        [('promedio', 'Precio promedio'),
         ('mediana', 'Precio mediano'),
         ('moda', 'Precio modal')]):
    with tab:
        rows = top_communes(by_commune, fuel, stat, limit=top_n,
                            min_estaciones=min_est,
                            selected_region=selected_region,
                            descending=ranking_direction == 'Más caras')
        if not rows:
            st.warning(f'Sin comunas que cumplan "{reliability}" para '
                       f'{nombre} ({etiqueta.lower()}).')
            continue
        highest = rows[0]
        ranking_label = 'Más cara' if ranking_direction == 'Más caras' else 'Más barata'
        st.info(
            f'{ranking_label} según {etiqueta.lower()}: **{highest["comuna"]}** '
            f'con **{highest["valor"]:.1f} {unidad}** '
            f'({highest["estaciones"]} estaciones).'
        )
        fig, ax = plt.subplots(figsize=(10, 5.5))
        style = CHART_STYLES[stat]
        plot_top_communes(ax, rows, f'{etiqueta} ({nombre})', unidad,
                          style['color'])
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)


st.divider()
st.subheader('Explorar una comuna')
commune_options = sorted(
    [key for key, fuels in by_commune.items()
     if (selected_region is None or key[1] == selected_region)
     and fuel in fuels],
    key=lambda key: (key[0], key[1]),
)

if commune_options:
    selected_commune = st.selectbox(
        'Selecciona una comuna para ver sus estadísticas',
        options=commune_options,
        format_func=lambda key: f'{key[0]} ({key[1]})',
    )
    details = commune_stats(by_commune, selected_commune, fuel)
    candidates = station_details[selected_commune].get(fuel, [])
    representative = min(
        candidates,
        key=lambda station: abs(station['precio'] - details['mediana']),
    )
    st.caption(f'{selected_commune[0]} · {selected_commune[1]} · '
               f'{details["estaciones"]} estaciones')
    st.info(
        f'Estación representativa (precio más cercano a la mediana): '
        f'**{representative["nombre"]}** · '
        f'{representative["precio"]:.1f} {unidad} · '
        f'{representative["direccion"]}'
    )

    station_table = sorted(candidates, key=lambda station: station['precio'])
    st.markdown('**Estaciones que forman este análisis**')
    st.dataframe(
        [
            {
                'Marca': station['marca'],
                'Estación': station['nombre'],
                'Dirección': station['direccion'],
                f'Precio ({unidad})': station['precio'],
            }
            for station in station_table
        ],
        hide_index=True,
        width='stretch',
    )

    detail_columns = st.columns(5)
    detail_columns[0].metric(f'Promedio ({unidad})',
                             f'{details["promedio"]:.1f}')
    detail_columns[1].metric(f'Mediana ({unidad})',
                             f'{details["mediana"]:.1f}')
    detail_columns[2].metric(f'Moda ({unidad})',
                             f'{details["moda"]:.1f}')
    detail_columns[3].metric(f'Mínimo ({unidad})',
                             f'{details["min"]:.1f}')
    detail_columns[4].metric(f'Máximo ({unidad})',
                             f'{details["max"]:.1f}')

    detail_values = [details[stat] for stat in ('promedio', 'mediana', 'moda')]
    detail_fig, detail_ax = plt.subplots(figsize=(8, 3.5))
    detail_fig.set_facecolor('#20262B')
    detail_ax.set_facecolor('#20262B')
    detail_ax.bar(['Promedio', 'Mediana', 'Moda'], detail_values,
                  color=['#F4B942', '#F2776B', '#62D2A2'])
    station_label = representative['nombre']
    if len(station_label) > 38:
        station_label = f'{station_label[:35]}...'
    detail_ax.axhline(
        representative['precio'],
        color='#F5F1E8',
        linestyle='--',
        linewidth=1.5,
        label=f'{station_label} ({representative["precio"]:.1f} {unidad})',
    )
    detail_ax.set_ylabel(f'Precio ({unidad})', color='#B7C0C5')
    detail_ax.set_title(f'Comparación de estadísticas — {selected_commune[0]}',
                        color='#F5F1E8', loc='left', pad=12,
                        fontweight='bold')
    detail_ax.tick_params(axis='both', colors='#DCE2E5')
    detail_ax.grid(axis='y', color='#526067', alpha=0.35, linewidth=0.8)
    detail_ax.set_axisbelow(True)
    detail_ax.legend(facecolor='#20262B', edgecolor='#526067',
                     labelcolor='#F5F1E8', fontsize=8)
    for spine in detail_ax.spines.values():
        spine.set_visible(False)
    detail_padding = max((max(detail_values) - min(detail_values)) * 0.5,
                         max(detail_values) * 0.005)
    detail_ax.set_ylim(min(detail_values) - detail_padding,
                       max(detail_values) + detail_padding)
    detail_fig.tight_layout()
    st.pyplot(detail_fig)
    plt.close(detail_fig)