.DEFAULT_GOAL := help
# .PHONY: tests

help:
	cat Makefile

setup:
	./run setup

agent_list:
	./run agent list

install:
	poetry install
	cd autogpts/FynAgent && poetry install

start:
	./run agent start FynAgent

stop:
	./run agent stop
