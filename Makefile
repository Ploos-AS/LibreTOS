.PHONY: help check qualify-m0 fetch-toolchain build-m1 qualify-m1 qualify-m2-profile qualify-m2-boot qualify-m2-gemdos qualify-m2-aes-vdi qualify-m2-media qualify-m2 qualify-target-matrix qualify-m3-profile build-m3-ste qualify-m3-boot qualify-m3-platform qualify-m3-enhanced qualify-m3 qualify-m4-profiles build-m4-mega qualify-m4-boot qualify-m4-platform qualify-m4 qualify-m5-profile build-m5-tt030 qualify-m5-boot qualify-m5-platform qualify-m5-enhanced qualify-m5 qualify-m6-profile build-m6-falcon030 qualify-m6-boot qualify-m6-platform qualify-m6-enhanced qualify-m6 qualify-m7-profile-schema qualify-m7-common qualify-m7-bios-xbios qualify-m7-compatibility qualify-m8-amiga-profile qualify-m8-startup

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
	@echo "  make build-m3-ste       - build dedicated Atari STe ROM artifact"
	@echo "  make qualify-m3-boot    - run M3.2 Atari STe Hatari boot regression"
	@echo "  make qualify-m3-platform - run M3.3 guest-side STe platform/XBIOS probe"
	@echo "  make qualify-m3-enhanced - run M3.4 STe enhanced-hardware regression"
	@echo "  make qualify-m3         - run aggregate M3.5 Atari STe qualification"
	@echo "  make qualify-m4-profiles - verify canonical Mega ST / Mega STe profiles"
	@echo "  make build-m4-mega      - build dedicated Mega ST and Mega STe ROM artifacts"
	@echo "  make qualify-m4-boot    - run M4.2 Mega ST / Mega STe Hatari boot regressions"
	@echo "  make qualify-m4-platform - run M4.3 guest-side Mega ST / Mega STe platform probes"
	@echo "  make qualify-m4         - run aggregate M4.4 Mega ST family qualification"
	@echo "  make qualify-m5-profile - verify canonical M5.1 Atari TT030/68030 profile"
	@echo "  make build-m5-tt030     - build dedicated Atari TT030 512 KiB ROM artifact"
	@echo "  make qualify-m5-boot    - run M5.2 Atari TT030 Hatari boot regression"
	@echo "  make qualify-m5-platform - run M5.3 guest-side TT030 platform probe"
	@echo "  make qualify-m5-enhanced - run M5.4 TT030 enhanced hardware/interface qualification"
	@echo "  make qualify-m5         - run aggregate M5.5 Atari TT030 qualification"
	@echo "  make qualify-m6-profile - verify canonical M6.1 Atari Falcon030/68030 profile"
	@echo "  make build-m6-falcon030 - build dedicated Atari Falcon030 512 KiB ROM artifact"
	@echo "  make qualify-m6-boot    - run M6.2 Atari Falcon030 Hatari boot regression"
	@echo "  make qualify-m6-platform - run M6.3 guest-side Falcon030 platform probe"
	@echo "  make qualify-m6-enhanced - run M6.4 Falcon030 enhanced interface qualification"
	@echo "  make qualify-m6         - run aggregate M6.5 Atari Falcon030 qualification"
	@echo "  make qualify-m7-profile-schema - validate all retained Atari profiles against the M7.1 shared contract"
	@echo "  make qualify-m7-common  - validate M7.2 GEMDOS/AES/VDI coverage across all retained Atari targets"
	@echo "  make qualify-m7-bios-xbios - validate M7.3 machine-specific BIOS/XBIOS coverage"
	@echo "  make qualify-m7-compatibility - validate M7.4 compatibility and qualification boundaries"
	@echo "  make qualify-m8-amiga-profile - validate M8.1 native Amiga OCS/68000 profile"
	@echo "  make qualify-m8-startup - validate M8.2 native Amiga startup/HAL contract"

check: qualify-m0 qualify-m2-profile qualify-target-matrix qualify-m3-profile qualify-m4-profiles qualify-m5-profile qualify-m6-profile qualify-m7-profile-schema qualify-m7-common qualify-m7-bios-xbios qualify-m7-compatibility qualify-m8-amiga-profile qualify-m8-startup

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
build-m3-ste: qualify-m3-profile
	@bash tools/build_m3_ste.sh
qualify-m3-boot: qualify-m3-profile build-m3-ste
	@python3 tools/qualify_m3_ste_boot.py
qualify-m3-platform: qualify-m3-profile build-m3-ste
	@python3 tools/qualify_m3_ste_platform.py
qualify-m3-enhanced: qualify-m3-profile build-m3-ste
	@python3 tools/qualify_m3_ste_enhanced.py
qualify-m3:
	@python3 tools/qualify_m3.py
qualify-m4-profiles:
	@python3 tools/check_m4_profiles.py
build-m4-mega: qualify-m4-profiles
	@bash tools/build_m4_mega.sh
qualify-m4-boot: qualify-m4-profiles build-m4-mega
	@python3 tools/qualify_m4_mega_boot.py
qualify-m4-platform: qualify-m4-profiles build-m4-mega
	@python3 tools/qualify_m4_mega_platform.py
qualify-m4:
	@python3 tools/qualify_m4.py
qualify-m5-profile:
	@python3 tools/check_m5_profile.py
build-m5-tt030: qualify-m5-profile
	@bash tools/build_m5_tt030.sh
qualify-m5-boot: qualify-m5-profile build-m5-tt030
	@python3 tools/qualify_m5_tt030_boot.py
qualify-m5-platform: qualify-m5-profile build-m5-tt030
	@python3 tools/qualify_m5_tt030_platform.py
qualify-m5-enhanced: qualify-m5-profile build-m5-tt030
	@python3 tools/qualify_m5_tt030_enhanced.py
qualify-m5:
	@python3 tools/qualify_m5.py
qualify-m6-profile:
	@python3 tools/check_m6_profile.py
build-m6-falcon030: qualify-m6-profile
	@bash tools/build_m6_falcon030.sh
qualify-m6-boot: qualify-m6-profile build-m6-falcon030
	@python3 tools/qualify_m6_falcon030_boot.py
qualify-m6-platform: qualify-m6-profile build-m6-falcon030
	@python3 tools/qualify_m6_falcon030_platform.py
qualify-m6-enhanced: qualify-m6-profile build-m6-falcon030
	@python3 tools/qualify_m6_falcon030_enhanced.py
qualify-m6:
	@python3 tools/qualify_m6.py
qualify-m7-profile-schema:
	@python3 tools/qualify_m7_profile_schema.py
qualify-m7-common: qualify-m7-profile-schema qualify-target-matrix
	@python3 tools/qualify_m7_common_regressions.py
qualify-m7-bios-xbios: qualify-m7-common
	@python3 tools/qualify_m7_bios_xbios.py
qualify-m7-compatibility: qualify-m7-bios-xbios
	@python3 tools/qualify_m7_compatibility.py
qualify-m8-amiga-profile:
	@python3 tools/qualify_m8_amiga_profile.py
qualify-m8-startup: qualify-m8-amiga-profile
	@python3 tools/qualify_m8_amiga_startup.py
