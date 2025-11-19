FROM python@sha256:ede46d7778a7ebac1e2f5253cdb9b59d3928c736b280636f68dcc60250619a03

COPY server.py /root

RUN pip install requests

RUN useradd -m -s /bin/bash agent
