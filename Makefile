.PHONY: help check qualify-m0

help:
	@echo "LibreTOS M0"
	@echo "  make check       - run repository checks"
	@echo "  make qualify-m0  - verify M0 foundation"

check: qualify-m0

qualify-m0:
	@python3 tools/check_m0.py
