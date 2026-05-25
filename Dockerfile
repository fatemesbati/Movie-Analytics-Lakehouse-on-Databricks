FROM eclipse-temurin:17-jdk-jammy

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir \
    pyspark==4.1.1 \
    delta-spark==4.2.0 \
    jupyterlab \
    matplotlib \
    pandas \
    pytest

WORKDIR /home/jovyan
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--allow-root", "--ServerApp.token=''", "--notebook-dir=/home/jovyan/work"]
