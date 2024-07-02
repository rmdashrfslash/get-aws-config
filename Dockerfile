FROM alpine:3.19

LABEL maintainer="Al Faller"

RUN apk update \
  && apk upgrade \
  && apk add python3 py3-boto3 py3-pip \
  && pip3 install --no-cache-dir --break-system-packages dynaconf \
  && rm -rf /var/cache/apk/*

ADD ./files/ /

RUN chmod +x /get-aws-config.py

CMD ["/get-aws-config.py"]

