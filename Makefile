.PHONY: help check qualify-m0 fetch-toolchain build-m1 qualify-m1 qualify-m2-profile qualify-m2-boot qualify-m2-gemdos qualify-m2-aes-vdi qualify-m2-media qualify-m2 qualify-target-matrix qualify-m3-profile

help:
	@echo "LibreTOS"
	@echo "  make check              - run repository checks"
	@echo "  make qualify-m0         - verify M0 foundation"
	@echo "  make fetch-toolchain    - fetch pinned m68k-elf toolchain"
	@echo "  make build-m1           - build pinned Atari ST/68000 ROM baseline"
	@echo "  make qualify-m1         - build and boot-smoke-test M1 in Hatari"
	@echo "  make qualify-m2-profile - verify canonical M2 ST/68000 profile"
	@echo "  make qualify-m2-boot    - run M2.2 profile-driven Hatari boot regression"
	@echo "  make qualify-m2-gemdos  - run M2.3 guest-side GEMDOS regression"
	@echo "  make qualify-m2-aes-vdi - run M2.4 guest-side AES/VDI regression"
	@echo "  make qualify-m2-media   - run M2.5 floppy/media regression"
	@echo "  make qualify-m2         - run aggregate M2.6 Atari ST qualification"
	@echo "  make qualify-target-matrix - verify permanent Atari multi-target registry"
	@echo "  make qualify-m3-profile - verify canonical M3.1 Atari STe/68000 profile"

check: qualify-m0 qualify-m2-profile qualify-target-matrix qualify-m3-profile

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

qualify-m2-boot: qualify-m2-profile build-m1
	@python3 tools/qualify_m2_boot.py

qualify-m2-gemdos: qualify-m2-profile build-m1
	@python3 tools/qualify_m2_gemdos.py

qualify-m2-aes-vdi: qualify-m2-profile build-m1
	@python3 tools/qualify_m2_aes_vdi.py

qualify-m2-media: qualify-m2-profile build-m1
	@python3 tools/qualify_m2_media.py

qualify-m2:
	@python3 tools/qualify_m2.py

qualify-target-matrix:
	@python3 tools/check_targets.py

qualify-m3-profile:
	@python3 tools/check_m3_profile.py
