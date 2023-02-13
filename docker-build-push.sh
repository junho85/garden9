TAG=$1
echo $TAG

docker build . -f Dockerfile --tag garden8:$TAG
docker tag garden8:$TAG junho85/garden8:$TAG
docker push junho85/garden8:$TAG
docker buildx build --platform linux/amd64,linux/arm64 -t junho85/garden8:$TAG --push .