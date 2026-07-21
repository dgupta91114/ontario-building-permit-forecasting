PYTHON ?= python

.PHONY: install inspect download data sample-size eda model explain report test reproduce clean demo

install:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

inspect:
	$(PYTHON) scripts/00_inspect_sources.py

download:
	$(PYTHON) scripts/01_download_data.py

data:
	$(PYTHON) scripts/02_build_dataset.py

sample-size:
	$(PYTHON) scripts/03_sample_size.py

eda:
	$(PYTHON) scripts/04_eda_rq1.py

model:
	$(PYTHON) scripts/05_train_evaluate.py

explain:
	$(PYTHON) scripts/06_explain_rq4.py

report:
	$(PYTHON) scripts/07_generate_results_report.py

test:
	pytest

reproduce:
	$(PYTHON) scripts/08_reproducibility_check.py

demo:
	$(PYTHON) scripts/99_generate_demo_data.py

clean:
	rm -rf data/interim/* data/processed/* outputs/figures/* outputs/tables/* outputs/models/*
