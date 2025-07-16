FROM python:3.9-slim

#Install required dependencies
RUN apt-get update && apt-get install -y \
    postgresql  postgresql-contrib libpq-dev curl && \
    rm -fr /var/lib/apt/lists*

# Environment variables

ENV POSTGRES_DB=vulneradb
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=vulnera

#Working directory
WORKDIR /app

COPY . .

#Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

#Expose flask port
EXPOSE 5000

CMD ["/entrypoint.sh"]
