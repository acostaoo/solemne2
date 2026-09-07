import streamlit as st

import requests

API_URL = 'https://api.cne.cl/api/v4/estaciones'
TOKEN = ''

email = st.secrets['EMAIL']
pw = st.secrets['PASSWORD']

def get_token():
    """Obtiene un nuevo token JWT usando el email y la contraseña."""
    global TOKEN
    response = requests.post(
        'https://api.cne.cl/api/login',
        json={'email': email, 'password': pw},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    TOKEN = data.get('token')
    if not TOKEN:
        raise RuntimeError('No se pudo obtener el token JWT.', response.text)


def get_estaciones():
    """Descarga la lista de estaciones desde la API del CNE."""
    global TOKEN
    for attempt in range(2):
        if not TOKEN:
            get_token()
        response = requests.get(
            API_URL,
            headers={'Authorization': f'Bearer {TOKEN}'},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            return data

        # La API responde 200 con un estado de token invalido o expirado.
        token_status = data.get('status') if isinstance(data, dict) else None
        token_needs_refresh = token_status in {'Token is Expired', 'Token is Invalid'}
        if token_needs_refresh and attempt == 0:
            TOKEN = ''
            continue

        detalle = data.get('status') if isinstance(data, dict) else str(data)
        raise RuntimeError(f'Respuesta inesperada de la API: {detalle}')


if __name__ == '__main__':
    # Prueba rápida: descarga y muestra la primera estación
    estaciones = get_estaciones()
    print(f'Estaciones descargadas: {len(estaciones)}')
    print(estaciones[0])
