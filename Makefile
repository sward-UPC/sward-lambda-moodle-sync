.PHONY: test lint deploy invoke

test:
	pip install -r requirements-dev.txt
	pytest tests/ -v

lint:
	ruff check . && ruff format --check .

deploy:
	sam build && sam deploy --guided

invoke:
	sam local invoke MoodleSyncFunction --event events/schedule.json
