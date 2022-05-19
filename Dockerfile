FROM python:3.8-alpine AS builder
WORKDIR /build
RUN apk add alpine-sdk linux-headers
COPY ./requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.8-alpine as runner
WORKDIR /app
RUN apk add iptables
RUN ln -s /usr/lib/libip6tc.so.2 /usr/lib/libip6tc.so && ln -s /usr/lib/libip4tc.so.2 /usr/lib/libip4tc.so
ENV XTABLES_LIBDIR "/usr/lib/xtables"
ENV PYTHON_IPTABLES_XTABLES_VERSION 12
ENV IPTABLES_LIBDIR "/usr/lib"
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY ./src/main.py .

CMD ["python3", "main.py"]