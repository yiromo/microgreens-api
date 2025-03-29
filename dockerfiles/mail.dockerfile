FROM python:3.10.12

WORKDIR /app/mail

RUN apt-get update && \
    apt-get install -y \
    wget 

ENV VIRTUAL_ENV=/home/packages/.venv

ADD https://astral.sh/uv/install.sh /install.sh

RUN chmod +x /install.sh && /install.sh && rm /install.sh && ls -l /root/.local/bin/
ENV PATH="/root/.local/bin:${PATH}"

COPY ./mail /app/mail/
COPY requirements.txt /app/mail

RUN /root/.local/bin/uv venv /home/packages/.venv
RUN /root/.local/bin/uv pip sync --index-url https://pypi.org/simple requirements.txt

EXPOSE 8000

CMD ["/root/.local/bin/uv", "run", "/app/mail/main.py"]