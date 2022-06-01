ARG TARGET_PYTHON_VERSION=3.8
FROM python:${TARGET_PYTHON_VERSION}-alpine AS builder
ARG TARGET_PYTHON_VERSION
WORKDIR /build
RUN apk add alpine-sdk linux-headers iptables libffi-dev
RUN ln -s /usr/lib/libip6tc.so.2 /usr/lib/libip6tc.so && ln -s /usr/lib/libip4tc.so.2 /usr/lib/libip4tc.so
ENV XTABLES_LIBDIR "/usr/lib/xtables"
ENV PYTHON_IPTABLES_XTABLES_VERSION 12
ENV IPTABLES_LIBDIR "/usr/lib"

ENV DEBUG_TOOLBAR=False
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/manage.py .
COPY ./src/hidlroute ./hidlroute
RUN find . -type d -name "__pycache__" -prune -exec rm -rf "{}" \;
RUN python manage.py collectstatic --no-input
RUN find . -type d -name "static" -prune -exec rm -rf "{}" \;
RUN rm ./hidlroute/settings/dev.py;
RUN which gunicorn

FROM python:${TARGET_PYTHON_VERSION}-alpine as runner
ARG TARGET_PYTHON_VERSION
ARG VERSION
ARG RELEASE_DATE
ARG CHANNEL
WORKDIR /app
RUN apk add iptables
RUN ln -s /usr/lib/libip6tc.so.2 /usr/lib/libip6tc.so && ln -s /usr/lib/libip4tc.so.2 /usr/lib/libip4tc.so
ENV XTABLES_LIBDIR "/usr/lib/xtables"
ENV PYTHON_IPTABLES_XTABLES_VERSION 12
ENV IPTABLES_LIBDIR "/usr/lib"
ENV DJANGO_SETTINGS_MODULE=hidlroute.settings.prod
ENV PYTHON_PATH="/app/external"
EXPOSE 8000

VOLUME ["/app/external", "/app/hidlroute/settings", "/app/hidlroute/settings_override"]

COPY --from=builder /usr/local/lib/python${TARGET_PYTHON_VERSION}/site-packages /usr/local/lib/python${TARGET_PYTHON_VERSION}/site-packages
COPY --from=builder /usr/local/bin/* /usr/local/bin/
COPY --from=builder /build/manage.py .
COPY --from=builder /build/hidlroute ./hidlroute
COPY --from=builder /build/static-files /app/static-files

CMD gunicorn hidlroute.wsgi:application --bind 0.0.0.0:8000 --timeout=10 --workers=4 --log-file="-"

LABEL x.hidl.version="${VERSION}" \
      x.hidl.release-date="${RELEASE_DATE}" \
      x.hidl.channel="${CHANNEL}"