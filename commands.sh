# in the same folder as Dockerfile
docker build -t pedalpath-process .

# then run it with mounting the data folder
docker run -v `pwd`:/app -it pedalpath-process /bin/bash