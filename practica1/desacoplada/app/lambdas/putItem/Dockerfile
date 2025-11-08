FROM public.ecr.aws/lambda/python:3.12

WORKDIR /var/task

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY common.py .
COPY db/ /var/task/db
COPY models/ /var/task/models

COPY lambdas/putItem/putHandler.py .

CMD [ "putHandler.handler" ]