# tandem-buddy

## Building the container

`docker build -t tandem-buddy-app .`


## Running the docker container

`docker run -it --rm -p 7860:7860 -v $(pwd):/app tandem-buddy-app`


