# Práctica 2 - 

**Autor:** Alejandro de Olózaga Ramírez

**Fecha:** Diciembre del 2025



# Recursos
Los recursos que se nombran a continuación forman la columna vertebral de una arquitectura de Big Data y Analítica moderna.


## Kinesis Data Streams
El servicio _Amazon Kinesis Data Streams_ sirve para capturar, recopilar y procesar grandes flujos de registros de datos en tiempo real. Es capaz de recibir enormes volúmenes de datos de miles de fuentes simultáneamente en tiempo real, es decir, con una latencia extremandamente baja (en milisegundos).

> Los datos de _streaming_ son los datos emitidos en volúmenes enormes de manera continua con el fin de conseguir un procesamiento de latencia baja.

El servicio _Kinesis Data Streams_ sirve para recibir o capturar enormes volúmenes de datos de miles de fuentes simultáneamente con una latencia extremadamente baja. De esta manera, los datos capturados podrán ser procesados o analizados en el instante en el que se generan.

Este servicio funciona recibiendo los datos de las aplicaciones y el usuario que usa el servicio escribe el código que leerá y procesará dichos datos.

Casos de uso: datos del mercado de valores en tiempo real, logs de aplicaciones para detección de fraudes instantánea, datos de telemetría en videojuegos.


## Firehose
El servicio _Firehose_ es completamente gestionado y está diseñado para capturar, transformar y cargar datos de streaming en un destino de almacenamiento final. Sirve para guardar datos de streaming en un Data Lake propio o almacén de datos.

Este servicio funciona acumulando los datos que llegan en lotes antes de entregarlos, así que es casi en tiempo real, distinguiéndose así la velocidad del _Kinesis Data Streams_

Caso de uso: almacenamiento de los logs de servidor web en S3 para su análisis posterior.


## Athena
El servicio _Athena_ es un servicio de consultas interactivo que sirve para analizar los datos guardados en Amazon S3 utilizando lenguaje SQL estándar. Funciona de la siguiente manera: el usuario apunta Athena a la carpeta de S3 donde se guardan los archivos, se define el esquema (columnas) y se escribe la consulta (``SELECT...``). Se paga por la cantidad de datos escaneados por cada consulta.

Casos de uso: análisis ad-hoc (preguntas rápidas a los datos), investigación de los de errores, generación de reportes rápidos sin levantar infraestructura de servidores.


## ETL
El proceso _Extract, Transform, Load_ consiste en tomar datos sucios o crudos, limpiarlos, cambiarles el formato o enriquecerlos y guardarlos en su destino final. En AWS, existen las siguientes opciones:

### AWS Glue

### Amazon EMR (Elastic MapReduce)

### AWS Lambda (ETL ligero)

