.PHONY: help check qualify-m0 fetch-toolchain build-m1 qualify-m1 qualify-m2-profile qualify-m2-boot qualify-m2-gemdos qualify-m2-aes-vdi qualify-m2-media qualify-m2 qualify-target-matrix qualify-m3-profile build-m3-ste qualify-m3-boot qualify-m3-platform qualify-m3-enhanced qualify-m3 qualify-m4-profiles build-m4-mega qualify-m4-boot qualify-m4-platform qualify-m4 qualify-m5-profile build-m5-tt030 qualify-m5-boot qualify-m5-platform qualify-m5-enhanced qualify-m5 qualify-m6-profile build-m6-falcon030 qualify-m6-boot qualify-m6-platform qualify-m6-enhanced qualify-m6 qualify-m7-profile-schema qualify-m7-common qualify-m7-bios-xbios qualify-m7-compatibility qualify-m8-amiga-profile qualify-m8-startup qualify-m8-boot qualify-m8-cia-timer qualify-m8-keyboard qualify-m8-interrupt qualify-m8-serial qualify-m8-video

help:
	@echo "LibreTOS"
	@echo "  make check              - run repository checks"
	@echo "  make qualify-m8-amiga-profile - validate M8.1 native Amiga OCS/68000 profile"
	@echo "  make qualify-m8-startup - validate M8.2 native Amiga startup/HAL contract"
	@echo "  make qualify-m8-boot    - validate M8.3 native Amiga boot/runtime contract"
	@echo "  make qualify-m8-cia-timer - validate M8.4 native Amiga CIA/timer HAL contract"
	@echo "  make qualify-m8-keyboard - validate M8.5 native Amiga keyboard HAL contract"
	@echo "  make qualify-m8-interrupt - validate M8.6 native Amiga interrupt HAL contract"
	@echo "  make qualify-m8-serial  - validate M8.7 native Amiga serial HAL contract"\n\t@echo "  make qualify-m8-video   - validate M8.8 native Amiga OCS display HAL contract"

check: qualify-m0 qualify-m2-profile qualify-target-matrix qualify-m3-profile qualify-m4-profiles qualify-m5-profile qualify-m6-profile qualify-m7-profile-schema qualify-m7-common qualify-m7-bios-xbios qualify-m7-compatibility qualify-m8-amiga-profile qualify-m8-startup qualify-m8-boot qualify-m8-cia-timer qualify-m8-keyboard qualify-m8-interrupt qualify-m8-serial

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
qualify-m8-boot: qualify-m8-startup
	@python3 tools/qualify_m8_amiga_boot.py
qualify-m8-cia-timer: qualify-m8-startup
	@python3 tools/qualify_m8_amiga_cia_timer.py
qualify-m8-keyboard: qualify-m8-cia-timer
	@python3 tools/qualify_m8_amiga_keyboard.py
qualify-m8-interrupt: qualify-m8-keyboard
	@python3 tools/qualify_m8_amiga_interrupt.py
qualify-m8-serial: qualify-m8-interrupt
	@python3 tools/qualify_m8_amiga_serial.py
qualify-m8-video: qualify-m8-serial
	@python3 tools/qualify_m8_amiga_video.py
