# Requisitos previos
Antes de comenzar la práctica, se necesitan los siguientes requisitos:
- uv: herramienta de Astral
- aws cli: interfaz de línea de comandos de AWS.
- datos.json: datos de ejemplo del campus virtual.

# Comandos
### General
Los comandos para inicializar, crear el entorno y añadir dependencias:
``` bash
uv init
uv venv
uv add boto3
uv add loguru

```

### Activar venv
``` bash
.venv\Scripts\activate

// Si da fallo, ejecutar lo siguiente:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Ejecutar archivo
En vez del botón de ejecutar, hay que ejecutar el siguiente comando:
``` bash
uv run <archivo>
```

Cuando todo se ha subido a Kinesis Data Stream, se puede visualizar en su Visor de Datos. Si ocurre el error de no poder visualizarlos, se deberá seleccionar otra forma de visualización (en número de secuencia, después de...)
# Descripción
El objetivo es conectarse a AWS, en concreto, a Kinesis Data Stream. Se enviarán datos que llegarán a Kinesis para distribuirlo entre los consumidores.
Posteriormente, de Kinesis Data Stream los datos se enviarán a AWS Data Firehose y, luego, se almacenarán en un bucket de S3.

Más adelante, se añadirá una lambda en el Firehose que realice una ejecución pequeña: añadir un timestamp.

El siguiente paso, será incluir AWS Glue