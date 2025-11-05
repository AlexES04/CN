# Práctica 4 - Modelo acoplado

**Autor:** Alejandro de Olózaga Ramírez

**Fecha:** Noviembre del 2025

## Introducción
Este es el modelo acoplado de la primera práctica entregable de la asignatura de Computación en la Nube, de la Universidad de Las Palmas de Gran Canaria. El diagrama de la infraestructura se presenta en la siguiente imagen


La aplicación web que se despliega simula una lista de la compra donde se pueden añadir, editar, visualziar y eliminar elementos, con una categoría y una cantidad especificadas. Básciamente, se permiten las operaciones CRUD.

Se va a utilizar una base de datos DynamoDB por la simplicidad de la aplicación web, ya que los accesos no requieren consultas complejas. Además, es escalable e ideal si tiene picos de tráfico, se paga por uso y AWS se encarga de todo. 

## Explicaciones y conceptos
Las **EC2** (Elastic Compute Cloud) permiten alquilar capacidad de computación de manera flexible y escalable, proporcionando servidores virtuales completos donde se tiene control total sobre el SO, aplicaciones y configuración de red.
Las ventajas principales son que incluyen escalabilidad automática, pago por tiempo real y disponibilidad global a través de múltiples regiones y zonas de disponibilidad.
Para un inicio, sería recomendable un modelo EC2 de tipo _On-Demand_ (pago por segundo). Si la aplicación llegara a ser más estable y grande, de tipo _Reserved Instances_.


La **distribución de carga** permite que múltiples recursos trabajen de manera coordinada para atender peticiones de forma eficiente. Los balanceadores de carga son, precisamente, esos intermediarios inteligentes que dirigen el tráficohacia los servidores más apropiados según unos criterios indicados.
El Elastic Load Balancer (ELB) es un servicio de carga completamente gestionado por AWS. Existe el Application Load Balancer y el Network Load Balancer. Para peticiones HTTP/HTTPS interesa el Application Load Balancer (ALB), ya que es ideal para aplicaciones web. De todas formas, se usará el NLB porque está diseñado para un rendimiento alto y baja latencia.


Las **ECS** (Elastic Container Service) permiten el despligue y gestión de contenedores Docker en AWS de forma escalable y eficiente, funcionando como un balanceador de carga sobre las instancias EC2 disponibles previamente.


El **AWS Fargate** funciona como un ECS, pero es serverless, no necesita gestionar instancias EC2. Únicamente es necesaria la especificación de CPU y RAM deseadas.


Las **ECR** (Elastic Container Registry) es un repositorio de Docker donde se pueden guardar contenedores propios, posee una integración nativa con AWS y ofrece seguridad y control total. Básicamente, es el lugar donde se almacena, administra y distribuye las imágenes de software que contienen las aplicaciones.


Las **APIs** definen cómo los sistemas de software se comunican entre sí, actuando como intermediaro permitiendo que diferentes aplicaciones intercambien datos y funcionalidades de manera estructurada.

Una **pila** en CloudFormation es una colección de recursos que se gestionan como una única unidad, como si fuera un contenedor lógico para todos los componentes de infraestructura de la aplicación (ej. EC2, ELB, SG...).

Un **Endpoint** es un punt ode contacto o comunicación. En última instancia, es el dispositivo o servicio que se encuentra al final de un canal de comunicación. Puede ser una dirección física o una URL. Un API Endpoint es la URL específica de un servidor o servicio que una aplicación usa para interactuar con una API. Ejemplos de Endpoints: POST, GET, DELETE. Básiscamente, el Endpoint es la puerta de entrada a la funcionalidad de la aplicación, resultando en una coimbinación de la dirección base del servidor y la ruta específica que define la operación.


Las **lambdas** son capaces de ejecutar un código como funciones virtuales independientes, sin necesidad de la gestión de servidores, lo que se conoce como _serverless_. Las lambdas están diseñadas especialmente para procesos cortos y eficientes, ya que estas se ejecutan por un tiempo limitado bajo demanda o eventos específicos. 
Se paga por petición y por tiempo de computación (1M de peticiones gratuitas --> 0,2€/1M).


## Puesta en marcha
1) Primeramente, hay que crear una pila para la infraestructura de ECR en CloudFormation (archivo ecr.yml). Se tiene que especificar:
    - Nombre de la pila.
    - Nombre de rol de IAM.
2) En segundo lugar, hay que crear otra pila para la infraestructura de la base de datos (archivo *db_dynamodb.yml* o *db_postgres.yml*). Se tiene que especificar:
    - Nombre de la pila.
    - Nombre de rol de IAM.
3) En VS Code, hay que configurar aws (aws configure) y luego poner los comandos de envío para la aplicación (están en Amazon ECR).
4) Hay que crear otra pila para el main.yml, donde está el load balancer. Se tiene que especificar:
    - Tipo de base de datos. 
    - 2 subnets.
    - VPC.
    - Nombre de rol de IAM.
    - Nombre de la imagen: tickets-app:latest
5) Cuando termine de craerse la última pila con el Load Balancer, se busca _API Gateway_ y se entra en la de la aplicación, pudiendo acceder a la clave. Además, ir a Configuración de la API para copiar la URL (punto de enlace predeterminado).
6) Copiar la clave de API y la URL de la API en el Frontend para acceder. Añadirle a la URL de la API /prod.


Una vez creado todo lo anterior, se puede ver las tablas de la base de datos en DynamoDB/tablas y los elementos de ellas.

Para ejecutar la práctica localmente:
1) Crear entorno de python.
2) Permitir la ejecución de scripts `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.
3) Ejecutar comandos para ejecución local (readme P4).
4) Para ejecutar los comandos de Docker, en el caso que no funcionen los del readme de la práctica 4:
    - Definir variables de entorno:
 ``$env:DB_TYPE="postgres";$env:DB_HOST="localhost";$env:DB_NAME="ticketsdb";$env:DB_USER="postgres";$env:DB_PASS:"postgres``
    - Ejecutar docker:
 ``docker run --name tickets-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ticketsdb -p 5432:5432 -d postgres:15``
    - Compilar el proyecto:
    ``docker build -t tickets-app:latest``
    - Ejecutar aplicación:
    ``docker run --rm -p 8080:8080 -e DB_TYPE=postgres -e DB_HOST=host.docker.internal -e DB_NAME=ticketsdb -e DB_USER=postgres -e DB_PASS=postgres tickets-app:latest``
6) En la configuración del Front poner:
    - Donde se ejecute la aplicación, normalmente en https://127.0.0.1:8080.
    - Contraseña NO necesaria.


## Archivo _ecr.yml_
La propiedad `ImageScanningConfiguration` configura el escaneo de seguridad de las imágenes y el parámetro _SCanOnPush_ indica si se activa o desactiva el escaneo automático.

La propiedad `LifecyclePolicy` define cómo el ECR debe limpiar las imágenes del repositorio ayudando a controlar costos. `LifecyclePolicyText: |` indica que el valor es un bloque de texto multilínea y | preserva los saltos de línea y el formato.
- ``rulePriority: 1`` : prioridad, las reglas con menor número se evalúan primero.
- ``selection`` , ``tagStatus``: aplica la regla a imágenes con cualquier estado de etiqueta.
- ``countType: "imageCountMoreThan"``: condición es cuando el número de imágenes exceda un límite.
- ``countNumber: 2``: límite para que se cumpla la condición.
- ``type: expire``: acción es eliminar imágenes que cumplan la condición.

Básicamente, esta políotica mantiene las 2 imágenes más recientes y elimina automáticamente cualquiera adicional. La imagen es un paquete que contiene la infraestructura de la aplicación: código, dependencias, configuración del sistema y capa del SO.

Dentro de las salidas del .yml tenemos:
- ECR URI: URL completa para acceder al repositorio.

## Archivo _db_dynamo.yml_
Dentro de los recursos se pueden definir los siguientes aspectos:
- AttributeName: ticket_id: atributo clave.
- AttributeType: tipo de dato (S -> String, N -> número, B -> binario).
- KeySchema: qué atributos se usarán como claves primarias.
- KeyType: especifica cuál es la clave de partición (HASH) o de ordenación (RANGE).
- BillingMode: modo de facturación y capacidad de la tabla. PAY_PER_REQUEST (a demanda) o PROVISIONES (se especifican las unidades de r/w).

## Archivo _main.yml_
### Balanceador de carga
En la definición del balanceador de carga se especifica el tipo (network) y el Schema (internal) que indica que es interno, que solo será accesible dentro de la VPC.

### Grupo Objetivo
El grupo objetivo (Target Group) agrupa a los destinos y define cómo el balanceador de carga debe verificar el estado. El TargetType define de qué tipo son los destinos registrados (ip, en este caso).

### Listener

El listener es la parte del balanceador de carga que espera las peticiones en un puerto/protocolo específico y luego dirige el tráfico a un Grupo Objetivo. La propiedad DefaultActions define la acción que hacer con el tráfico que recibe el listener. El ``Type: forward`` especifica que se reenvíe el tráfico al grupo objetivo que se especifique en ``TargetGroupArn``. Se asocia al balanceador de carga al parámetro que se especifique en ``LoadBalancerArn``.

### Clúster ECS
Un clúster ECS es una agrupación lógica de servidores EC2 o Fargate donde se ejecutan contenedores. La definición de tarea es el plano que le dice a ECS cómo debe lanzar el contenedor (qué imagen, cantidad de CPU y memoria, puertos y roles de IAM necesarios). La propiedad ``NetworkMode: awsvpc`` indica que cada tarea tendrá su propia interfaz de red elástica y dirección IP privada (obligatorio para Fargate). ``RequiresCompatibilities: [FARGATE]`` especifica la necesidad de ejecución en el tipo de lanzamiento Fargate. ``ExecutionRoleArn`` es el rol que usa el agente ECS para tareas de infraestructura y ``TaskRoleArn`` es el rol que usa la aplicación dentro del contendor para interactuar con otros servicios. ContainerDefinitions es la lista de contenedores que se ejecutarán en la tarea que se está definiendo.
El servicio ECS es el que orquesta los contenedores y es administrado por AWS, permitiendo que se ejecuten contenedores en un clúster. Tiene el parámetro DependsOn: [] que indica que no debe intentar iniciarse hasta que el recurso especificado se haya creado correctamente. La propiedad DesiredCount: indica el número de instancias que debe mantener la tarea en ejecución en todo momento. La propiedad ``AssignPublicIP: ENABLED`` asigna una dirección IP pública a cada tarea.

### API
Primero se crea un VPC Link con ``VPCLink``, que actúa como túnel de red privado que permite que las integraciones de API Gateway accedan a recursos internos. La propiedad ``TargetArns`` especifica el ARN como destino de la conexión.

La propiedad ``RestAPI`` crea el contenedor principal de la API REST, ``ItemsResource`` crea el recurso /items, ``ParentId`` indica de qué es hijo, en este caso, /items es un hijo de la raíz de la API (/). ``ItemResource`` crea el recurso {id} y el ``ParentId`` en este caso indica que el recurso es hijo de /items, resultando al final en /items/{id}.

Posteriormente se definen las operaciones del CRUD (POST, GET, PUT, DELETE), el parámetro ``AuthorizationType: NONE`` indica que la API Key será elúnico control de acceso, ``ApiKeyRequired: true`` fuerza al cliente a incluir una API Key válida.

Dentro de la integración, ``Type: HTTP_PROXY`` hace que la solicitud se envía tal cual a la integración sin transformación, ``IntegrationHttpMethod`` el verbo HTTP con el que API Gateway llamará al Backend, ``Uri`` es la URL a la que la API Gateway enviará la solicitud. ``ConnectionType: VPC_LINK`` y ``ConnectionId: !Ref VPCLink`` especifica que debe usar VPC Link definido anteriormente. Dentro del manejo de parámetros ``RequestParameters:`` define los parámetros obligatorios, y ``integration.request.path.id`` le dice a la API Gateway qeu tome el valor del parámetro especificado lo pase como parte de la ruta al backend.

Los métodos CORS (_Cross-Origin Resource Sharing_) son las reglas y cabeceras que usan los servidores/navegadores para determinar si es seguro que una página pueda acceder a recursos de otro dominio. Dentro de los ``OptionItemsMethod`` y ``OptionItemMethod`` se especifica un tipo ``Type: MOCK``, que indica que la respuesta se devuelve directamente desde API Gateway sin lamar al backend. ``IntegrationResponses`` y ``MethodResponses`` configuran las cabeceras HTTP necesarias para CORS, permitiendo GET, POST, PUT, DELETE, OPTIONS y cualquier origen ``*``.

Por último, el despliegue para que la API sea accesible. ``APIDeployment`` representa una instantánea de la configuración actual de la API y el parámetro ``DependsOn: []`` niega el despliegue hasta que tdoso los métodos hayan sido definidos (CRUD+CORS). ``APIStage`` publica la implementación de la API y ``StageName: prod`` indica el nombre del entorno. La ``APIKey`` crea una clave de autenticación que los clientes deben usar si es requerido (``ApiKeyRequired: true``). ``UsagePlan`` define los límites de tasa y cuotas para la API y ``ApiStages`` asocia el plan de uso al Stage definido. ``UsagePlanKey`` asocia la APIKey con el UsagePlan, activando el requisito de la clave para el acceso.

### Outputs
En esta sección se exponen los valores imporantes de los recursos creados, que se podrán ver en la consola después de que el Stack se haya completado.

Primeramente, el Endpoint de la API, que es la salica que porporciona la URL completa y funcional para interactuar con la API REST. El ID de la API Key proporciona el identificador único de la clave que se acaba de crear para autenticar solicitudes.