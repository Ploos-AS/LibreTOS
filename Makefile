.PHONY: help check qualify-m0 fetch-toolchain build-m1 qualify-m1 qualify-m2-profile

help:
	@echo "LibreTOS"
	@echo "  make check              - run repository checks"
	@echo "  make qualify-m0         - verify M0 foundation"
	@echo "  make fetch-toolchain    - fetch pinned m68k-elf toolchain"
	@echo "  make build-m1           - build pinned Atari ST/68000 ROM baseline"
	@echo "  make qualify-m1         - build and boot-smoke-test M1 in Hatari"
	@echo "  make qualify-m2-profile - verify canonical M2 ST/68000 profile"

check: qualify-m0 qualify-m2-profile

qualify-m0:
	@python3 tools/check_m0.py

fetch-toolchain:
	@bash tools/fetch_toolchain.sh

build-m1:
	@bash tools/build_m1.sh

qualify-m1: build-m1
	@bash tools/qualify_m1_hatari.sh

qualify-m2-profile:
	@python3 tools/check_m2_profile.py
