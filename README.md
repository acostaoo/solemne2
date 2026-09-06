# Solemne II : Análisis precios de combustible desde CNE

## Introducción 

proyecto de análisis de datos de los precios de combustible en vivo entregados por la CNE. Se entrega el promedio, la media y la moda de los datos obtenidos desde la API semi-pública del CNE ~api.cne.cl~. Estas métricas se entregan por comuna por región, pudiendo seleccionar el precio más alto y el más bajo, a la vez entrega los datos de los que se basa el gráfico.

## Desafíos

El desafío más grande fue encontrar una API pública; esta API es parcialmente pública al requerir un token de autenticación que obtiene con mis credenciales propias, ya que la fuente entregada de la página del gobierno es atroz, está muy desactualizada y la entrega de los datos es de lo más pobre que visto como API, ni siquiera se llamaría API, mucho menos REST.


Posterior a obtener los datos del CNE fue relativamente directo, ya que la API está sencilla y relativamente moderna y bien documentada para su consumo.

## Datos seleccionados: CNE

Elegí los datos del CNE por simplicidad, como explicado previamente, y por curiosidad. A pesar que el sitio bencinaenlinea.cl , también del CNE, está bien hecho, esto es una interpretación mía de el consumo de datos expuestos.

## Desarrollo

Empecé con el flujo de autenticación y secretos para refrescar el token y mantenerlo oculto del público, y luego con el llamado a la API con GET que entrega toda la información requerida en un solo endpoint, y se almacena en caché para no realizar llamadas constantemente y analizar los datos en paz.

Luego, se modelaron las entidades de los datos para deserializar el JSON obtenido. 

Posteriormente, levanté el sitio con streamlit agregando títulos y la cajonera, para concluir con el análisis en sí y la construcción de los gráficos.

## Hallazgos

Aunque la API esté relativemente moderna, los datos no lo son, algunos con fechas del 2015 los más lejanos, y los más cercanos en marzo 2026 aprox. En comunas como Estación Central, hay 10 estaciones registradas con datos, de las que 9 de ellas presentan el mismo precio de gasolina 93, lo que muestra la misma moda, mediana y mínimo de precio, haciéndome cuestionar la fiabilidad de los datos y del análisis realizado. Esto llevó a crear la lista que muestra las estaciones de los que se basa el gráfico inferior, para concluir que efectivamente las 9 estaciones tienen elmismo precio y no fue error de trata de datos.

## Aprendizajes obtenidos

Aprendí que el sitio del gobierno es muy poco útil como API pública. La información es muy difícil de obtener, incluso para uno que se maneja con el computador. Aprendí que streamlit es muy útil para generar MVPs como este.

