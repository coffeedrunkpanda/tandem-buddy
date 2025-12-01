# tandem-buddy

## Environment
### Docker compose
`docker-compose up`

### Using docker container

#### Building: 
`docker build -t tandem-buddy-app .`


#### Running the container: 

Running the docker container with the env parameter. Bare in mind that the
docker needs a very specific formatting. If possible opt to use the docker-compose
instead.

`docker run -it --rm -p 7860:7860 --env-file $(pwd)/.env tandem-buddy-app`

### local env

```bash
python -m venv .venv
source .venv/bin/activate
pip install .

python app.py
```

