PYCODE = import flask.ext.statics as a; print a.__path__[0]

default:
	@echo "\nPython IoT data integrity app's make commands\n"
	@echo "Commands available:\n"
	@echo "    make install		# Starts a development IoT server/core."

install:
	docker-compose up -d --no-deps