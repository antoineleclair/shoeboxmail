# Shoebox Mail

Shoebox Mail is an SMTP server and an HTML inbox application to use in automated browser testing.

## Running

Make sure you have `Docker`, and then:

```bash
docker build -t shoeboxmail .
docker run -P -e "PYTHONUNBUFFERED=0" shoeboxmail
```
