docker rm -f some-rabbit
#docker run -d --hostname some-rabbit --name some-rabbit -e RABBITMQ_ERLANG_COOKIE='secret cookie here' rabbitmq
docker run -d --hostname some-rabbit --name some-rabbit -p 5672:5672 -e RABBITMQ_ERLANG_COOKIE='secret cookie here' rabbitmq

