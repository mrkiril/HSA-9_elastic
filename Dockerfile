FROM python:3.9.2-slim
WORKDIR /app
RUN apt-get update \
    && apt-get install sysstat -y \
    && apt-get clean
RUN pip3 install --upgrade pip wheel

ADD requirements.txt .
RUN pip3 --no-cache-dir install -r requirements.txt

RUN rm -rf ~/.cache/pip
COPY . .
ENV PYTHONPATH "/app:${PYTHONPATH}"
ENV VERSION=0.0.1

CMD ["python3", "-u", "main.py"]