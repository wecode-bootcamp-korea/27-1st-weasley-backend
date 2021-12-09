## :: How to deploy server with Docker
0. install Docker on the server/computer you want to run this project
1. git clone https://github.com/wecode-bootcamp-korea/27-1st-weasley-backend.git 
2. run to build docker image -> docker build -f Dockerfile.web -t [your docker-hub name]/weasley:[tag] . / docker build -f Dockerfile.schedule -t [your docker-hub name]/weasley-schedule:[tag] . -> you have to build twice cause of background-scheduler
3. run to push on your docker hub -> docker push [your docker-hub name]/weasley:[tag] / docker push [your docker-hub name]/weasley-schedule:[tag]
4. request pull on server you want to make docker container -> docker run --name weasley -dp 8000:8000 [your docker-hub name]/weasley:[tag] / docker run --name weasley -d [your docker-hub name]/weasley-schedule:[tag]
5. you can see logs by -> docker logs -f weasley / docker logs -f weasley-schedlue

### ENJOY! :)
