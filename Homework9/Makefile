docker vespa:
	docker run -d --name vespa-hybrid --hostname vespa-container --publish 8082:8080 --publish 19071:19071 vespaengine/vespa

install:
	pip3 install --ignore-installed vespacli

config:
	vespa config set target local

deploy:
	vespa status deploy --wait 300

run:
	vespa deploy --wait 300 app

feed:
	vespa feed -t http://localhost:8082 clean_tmdb.jsonl