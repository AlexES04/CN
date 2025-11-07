# Dockerfile para: lambdas/postItem/Dockerfile
# Base de AWS Lambda
FROM public.ecr.aws/lambda/python:3.12

# Directorio de trabajo
WORKDIR /var/task

# Copiar requirements de la raíz (el contexto '.')
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el código común de la raíz
COPY common.py .
COPY db/ /var/task/db
COPY models/ /var/task/models

# Copiar el handler específico de su subcarpeta
COPY lambdas/postItem/postHandler.py .

# El CMD apunta al fichero que acabamos de copiar
CMD [ "postHandler.handler" ]