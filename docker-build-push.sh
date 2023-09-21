TAG=$1
echo $TAG

docker build . -f Dockerfile --tag garden9:$TAG
docker tag garden9:$TAG junho85/garden9:$TAG
docker push junho85/garden9:$TAG
docker buildx build --platform linux/amd64,linux/arm64 -t junho85/garden9:$TAG --push .