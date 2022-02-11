FROM python:3.8

WORKDIR /instBot_v2
COPY . /instBot_v2/

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONPATH /instBot_v2

CMD ["python","/instBot_v2/bot_worker/main.py"]