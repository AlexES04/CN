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

Hay que hacer ``aws configure``.

Se ejecuta el script ``deploy_project.ps1``.
Posteriormente, se ejecuta el archivo de Python ``kinesis.py``. Luego ejecutar el archivo ``project-execution.ps1``.
Al final, cuando todo esté visualizado y se termine de trabajar, se ejecuta el script ``clean_up.ps1`` para limpiar los recursos creados.

Cuando todo se ha subido a Kinesis Data Stream, se puede visualizar en su Visor de Datos. Si ocurre el error de no poder visualizarlos, se deberá seleccionar otra forma de visualización (en número de secuencia, después de...)
# Descripción
El objetivo es conectarse a AWS, en concreto, a Kinesis Data Stream. Se enviarán datos que llegarán a Kinesis para distribuirlo entre los consumidores.
Posteriormente, de Kinesis Data Stream los datos se enviarán a AWS Data Firehose y, luego, se almacenarán en un bucket de S3.

Más adelante, se añadirá una lambda en el Firehose que realice una ejecución pequeña: añadir un timestamp.

El siguiente paso, será incluir AWS Glue

No se pueden mandar muchos registros, lo mejor es que esté entre el intervalo: 864-50.000 registros.
Hay que tener cuidado al elegir la clave de partición. Para elegir una adecuada, primero, hay que entender los datos. Por ejemplo, un dataset de coches, una clave de partición posible puede ser el país SIEMPRE Y CUANDO haya varios países que fabriquen coches y esté más o menos distribuido (USA 150M registros | ESP 15M registros | MXN 1M registros | COL 10k registros).
La clave de partición permite hacer un filtrado rápido en un sistema complejo donde la filtración es muy costosa.

### energy_aggregation_daily.py energy_aggregation_monthly.py
Son scripts de Python que se diferencian en que en el _daily_ se procesan los datos por fecha hasta el mes y en el _monthly_ se procesan por fecha hasta el año.


Orden de ejecución de scripts:
```bash
./project-deployment.ps1
```

```bash
uv run kinesis.py
```

```bash
./project-execution.ps1
```

Cuando se quiera borrar:
```bash
./project-cleanup.ps1
```