# Práctica 4 - Modelo acoplado

**Autor:** Alejandro de Olózaga Ramírez

**Fecha:** Noviembre del 2025

## Introducción
Este modelo (acoplado) cuenta con una instancia EC2 o ECS que ejecutará la acción pedida (CRUD).

## Explicaciones y conceptos
Las **EC2** (Elastic Compute Cloud) permiten alquilar capacidad de computación de manera flexible y escalable, proporcionando servidores virtuales completos donde se tiene control total sobre el SO, aplicaciones y configuración de red.
Las ventajas principales son que incluyen escalabilidad automática, pago por uso real y disponibilidad global a través de múltiples regiones y zonas de disponibilidad.
Para un inicio, sería recomendable un modelo EC2 de tipo _On-Demand_ (pago por segundo). Si la aplicación llegara a ser más estable y grande, de tipo _Reserved Instances_.


La **distribución de carga** permite que múltiples recursos trabajen de manera coordinada para atender peticiones de forma eficiente. Los balanceadores de carga son, precisamente, esos intermediarios inteligentes que dirigen el tráficohacia los servidores más apropiados según unos criterios indicados.
El Elastic Load Balancer (ELB) es un servicio de carga completamente gestionado por AWS. Existe el Application Load Balancer y el Network Load Balancer. Nos interesa el Application Load Balancer (ALB) para peticiones HTTP/HTTPS, ya que es ideal para aplicaciones web.


Las **ECS** (Elastic Container Service) permiten el despligue y gestión de contenedores Docker en AWS de forma escalable y eficiente, funcionando como un balanceador de carga sobre las instancias EC2 disponibles previamente.


El **AWS Fargate** funciona como un ECS, pero es serverless, no necesita gestionar instancias EC2. Únicamente es necesaria la especificación de CPU y RAM deseadas.


Las **ECR** (Elastic Container Registry) es un repositorio de Docker donde se pueden guardar contenedores propios, posee una integración nativa con AWS y ofrece seguridad y control total. Básicamente, es el lugar donde se almacena, administra y distribuye las imágenes de software que contienen las aplicaciones.


Las **APIs** definen cómo los sistemas de software se comunican entre sí, actuando como intermediaro permitiendo que diferentes aplicaciones intercambien datos y funcionalidades de manera estructurada.

Una **pila** en CloudFormation es una colección de recursos que se gestionan como una única unidad, como si fuera un contenedor lógico para todos los componentes de infraestructura de la aplicación (ej. EC2, ELB, SG...).


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
5) Cuando termine de craerse la última pila con el Load Balancer, se busca _API Gateway_ y se entra en la de la aplicación, pudiendo acceder a la clave. Además, ir a Configuración de la API para copiar la URL (punto de enlace predeterminado).
6) Copiar la clave de API y la URL de la API en el Frontend para acceder.

Una vez creado todo lo anterior, se puede ver las tablas de la base de datos en DynamoDB/tablas y los elementos de ellas.

Para ejecutar la práctica localmente:
1) Crear entorno de python.
2) Permitir la ejecución de scripts `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.
3) 
