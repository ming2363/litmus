SHELL := /bin/bash

RAW_SHARDS := $(wildcard data/shards/*.csv)
CLEANED := $(wildcard stage/cleaned/*.csv)
ENRICHED := $(wildcard stage/enriched/*.json)

all: output/report.tsv

stage/cleaned:
	mkdir -p $@

stage/enriched:
	mkdir -p $@

output:
	mkdir -p $@

stage/cleaned/%.csv: data/shards/%.csv stage/cleaned
	python3 scripts/clean_shard.py $< $@

stage/enriched/%.json: stage/cleaned/%.csv stage/enriched
	python3 scripts/enrich_shard.py $< data/lookup/currency_rates.json data/lookup/region_map.json $@

output/summary.json output/report.tsv: $(ENRICHED) output
	python3 scripts/aggregate.py -o output/summary.json $<
	python3 scripts/render_report.py output/summary.json output/report.tsv

clean:
	rm -rf output/*
