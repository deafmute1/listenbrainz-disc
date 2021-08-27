FROM python:3.9

ENV LBZ_DATA_DIR=/data 

RUN mkdir -p /tmp/lbz

COPY / /tmp/lbz

RUN pip install -r /tmp/lbz/requirements.txt && \
    pip install /tmp/lbz && \
    rm -r /tmp/lbz  

ENTRYPOINT [ "lbz" ]



