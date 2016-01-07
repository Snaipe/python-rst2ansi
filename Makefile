PY := python3

export PATH := $(shell pwd)/bin:$(PATH)
export PYTHONPATH=$(shell pwd)

BUILD = $(PY) setup.py

build:
	$(BUILD) build

install:
	$(BUILD) install

test:
	cram test -v

clean:
	$(BUILD) clean

.PHONY: build install test clean
