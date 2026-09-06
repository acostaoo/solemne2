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
        json={'email': email, 'password': pw}
    )
    response.raise_for_status()
    data = response.json()
    TOKEN = data.get('token')
    if not TOKEN:
        raise RuntimeError('No se pudo obtener el token JWT.', response.text)


def get_estaciones():
    """Descarga la lista de estaciones desde la API del CNE."""
    if not TOKEN:
        get_token()
    response = requests.get(API_URL, headers={'Authorization': f'Bearer {TOKEN}'})
    response.raise_for_status()
    data = response.json()
    # La API responde 200 con {'status': 'Token is Expired'} al expirar el JWT
    if not isinstance(data, list):
        detalle = data.get('status') if isinstance(data, dict) else str(data)
        raise RuntimeError(
            f'Respuesta inesperada de la API: {detalle}. '
            f'¿Renovaste el token en api_client.py?')
    return data


if __name__ == '__main__':
    # Prueba rápida: descarga y muestra la primera estación
    estaciones = get_estaciones()
    print(f'Estaciones descargadas: {len(estaciones)}')
    print(estaciones[0])
