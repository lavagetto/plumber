FROM python_base:2015.1

ADD . /srv/application/
WORKDIR /srv/application
RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "{{ c.python.wsgi_runnable }}"]
CMD ["-b", "0.0.0.0:8080"]
{% if c.external.nfs %}
VOLUME /data/project/{{ c.name }}
{% endif %}
