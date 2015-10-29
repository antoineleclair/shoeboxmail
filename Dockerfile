FROM python:3.4
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
EXPOSE 5566
CMD [ "shoeboxsmtp" ]
