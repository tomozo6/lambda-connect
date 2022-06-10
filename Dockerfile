FROM public.ecr.aws/lambda/python:3.9
#FROM python:3.9-alpine
#ENV LAMBDA_TASK_ROOT /var/task

WORKDIR ${LAMBDA_TASK_ROOT}
COPY src ${LAMBDA_TASK_ROOT}
COPY Pipfile ${LAMBDA_TASK_ROOT}
COPY Pipfile.lock ${LAMBDA_TASK_ROOT}

RUN pip install pipenv && \
    pipenv sync --system && \
	pip uninstall --yes pipenv

CMD [ "app.handler" ]