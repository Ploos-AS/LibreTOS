# M7.3 — Machine-specific BIOS/XBIOS regression coverage

M7.3 records the BIOS/XBIOS qualification boundary for every retained Atari target without flattening machine-specific capabilities.

## Policy

LibreTOS keeps one shared source base, but every Atari target retains its own machine profile, deterministic ROM build, qualification path, and separately published ROM artifact. A future universal/multi-machine ROM may be provided only as an additional convenience artifact; it must never replace, supersede, hide, or remove the canonical machine-specific ROMs.

## Coverage

The retained targets are Atari ST, STe, Mega ST, Mega STe, TT030, and Falcon030. All retain a common BIOS baseline for console/media behavior and a common XBIOS video boundary. Later machines additionally retain their already-qualified machine-specific platform/XBIOS expectations instead of being reduced to the ST baseline.

`tools/qualify_m7_bios_xbios.py` validates the six-target coverage contract, unique release artifacts, profile availability, proprietary-ROM independence, and the platform qualification path associated with each target. It writes deterministic evidence to `build/m7/bios-xbios/`.

This stage is an aggregate coverage gate over the machine-specific qualification work established in M2–M6. The existing guest-side platform probes remain the runtime authority for their respective machines.

## Exit criteria

M7.3 is complete when all six retained targets are represented, each keeps a unique canonical release artifact, BIOS/XBIOS coverage is explicit, machine-specific platform expectations are preserved, no proprietary Atari ROM is required, and the M7.3 CI gate passes.

The next stage is M7.4: compatibility matrix and qualification boundaries.
