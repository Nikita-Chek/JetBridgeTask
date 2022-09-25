FROM python:3.10

LABEL MAINTAINER="Nikita Chekalinsky <nikitachekalinsky@gmail.com>"


ENV GROUP_ID=1000 \
    USER_ID=1000


WORKDIR /var/scrapperapp/

ADD . /var/scrapperapp/

RUN pip install -r requirements.txt

RUN addgroup -gid $GROUP_ID scrapperapp
RUN adduser -u $USER_ID --gid $GROUP_ID scrapperapp --shell /bin/sh

USER scrapperapp


CMD ["python3", "-u", "main.py"]
