FROM python:3.10-slim as python-base

WORKDIR /app
COPY . /app/

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential \
    curl \
    apt-utils \
    gnupg2 &&\
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip

RUN apt-get update
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list 
 
RUN exit
RUN apt-get update
RUN env ACCEPT_EULA=Y apt-get install -y msodbcsql18 

COPY requirements.txt .

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN env ACCEPT_EULA=Y apt-get install -y msodbcsql18
RUN pip install -r requirements.txt

RUN apt-get clean all
 
EXPOSE 8080
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "80"]
