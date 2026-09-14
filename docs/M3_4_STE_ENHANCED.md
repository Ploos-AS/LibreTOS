# M3.4 — Atari STe enhanced-hardware regression

M3.4 extends the qualified STe baseline beyond machine identity and XBIOS presence. It verifies that the canonical LibreTOS STe image can exercise key enhanced STe hardware interfaces under Hatari without weakening the earlier ST or STe gates.

## Canonical target

- profile: `ste-68000-1m-256k-us`
- machine: Atari STe
- CPU: 68000
- ST-RAM: 1 MiB
- ROM: `LibreTOS-STe-68000-256k-us.img`
- emulator: Hatari `--machine ste`

## Guest checks

The native `STEENH.TOS` probe performs reversible checks and restores original hardware state before returning:

1. **Hardware scrolling** — writes and reads back the STe horizontal-scroll register at `0xffff8265`, then restores the previous value.
2. **DMA sound mode** — writes and reads back the STe DMA-sound mode register at `0xffff8921`, then restores the previous value. The test changes mode/rate bits only; it does not start DMA replay.
3. **Blitter control** — uses XBIOS `Blitmode()` to verify that the blitter is present, can be disabled, can be enabled, and can be restored to its original state.

The probe writes `C:\M3ENH.TXT`; the host qualifier independently validates its schema, profile, PASS verdict, readbacks, and blitter state transitions.

## Evidence

`make qualify-m3-enhanced` records evidence under `build/m3/ste-enhanced/`:

- `PROFILE.json`
- `ROM.sha256`
- `PROBE.sha256`
- `HATARI_PROFILE.json`
- `RESULT.txt`
- `hatari.log`
- guest hard-drive fixture and raw result

CI uploads the evidence and the exact 256 KiB STe ROM even when the qualification fails.

## Pass criteria

M3.4 passes only when:

- the dedicated 256 KiB STe ROM builds;
- Hatari completes without timeout or fatal ROM/emulator errors;
- the guest probe runs and produces a valid result;
- horizontal-scroll register readback matches the written test value;
- DMA sound mode readback exposes the selected rate bits;
- XBIOS reports a blitter, and disable/enable transitions work;
- all modified hardware state is restored by the guest before exit.

M3.4 does not claim analog audio quality, exact DMA timing, pixel-perfect scrolling, or blitter throughput. Those require deeper timing/output qualification and may be added later without changing this regression contract.
