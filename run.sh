docker build . -t bot
docker run --rm -e CONSUMER_KEY -e CONSUMER_SECRET \
-e ACCESS_TOKEN -e ACCESS_TOKEN_SECRET \
--device /dev/fuse --cap-add SYS_ADMIN --name SpeccyBot bot
