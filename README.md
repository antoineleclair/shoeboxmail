# Shoebox Mail

Shoebox Mail is an SMTP server and an HTML inbox application to use in automated browser testing.

## Using

The two exposed ports are `5566` for SMTP and `5577` for HTTP. When the application is running, you can send emails to `localhost:5566` and see the inbox web application running at `http://localhost:5577`.

### With Docker Compose

In your `docker-compose.yml` file, declare the `mail` service, and add a link in your service that sends emails:

```yml
mail:
  image: antoineleclair/shoeboxmail:0.11.0
  ports:
    - "5566:5566"
    - "5577:5577"
your_app:
  foo: bar
  links:
    - mail
    - baz
```

### With Docker

```bash
docker run -p 5566:5566 -p 5577:5577 antoineleclair/shoeboxmail:0.11.0
```

## Current Limitations

At this time, Shoeboxmail does not support authentication and SSL/TLS encryption.

## Development

Build:

```bash
docker build -t shoeboxmail .
```

Make sure to run this command once to create the `egg-info` directory on the host file system:

```bash
docker run -p 5566:5566 -p 5577:5577 -v $(pwd):/code shoeboxmail python setup.py develop
```

Then you can run the app using the host file system directory:

```bash
docker run -p 5566:5566 -p 5577:5577 -v $(pwd):/code shoeboxmail
```
