deploy:
	appcfg.py update .

run:
	dev_appserver.py app.yaml

install:
	pip install -r requirements.txt -t lib/


.PHONY: deploy run
