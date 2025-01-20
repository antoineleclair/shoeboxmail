FROM python:3.12.5
ENV PYTHONUNBUFFERED=0
WORKDIR /code
ADD setup.py /code/.
ADD requirements.txt /code/.
RUN pip install -r requirements.txt
ADD . /code/.
RUN python setup.py develop
EXPOSE 5566
EXPOSE 5577
CMD [ "shoeboxmail" ]
