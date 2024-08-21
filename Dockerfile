FROM python:3.12.5
COPY . /code
WORKDIR /code
ENV PYTHONUNBUFFERED 0
RUN pip install -r requirements.txt
EXPOSE 5566
EXPOSE 5577
CMD [ "shoeboxmail" ]
