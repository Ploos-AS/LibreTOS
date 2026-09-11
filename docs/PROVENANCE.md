# Source Provenance and Compliance Policy

LibreTOS must remain redistributable and auditable.

## Rules

1. Do not commit proprietary Atari TOS ROM images, extracted ROM code, or other material without redistribution rights.
2. Every imported source component must have a documented origin, version/commit and license.
3. EmuTOS may be used as an upstream/reference baseline subject to its applicable license and attribution requirements.
4. LibreTOS-specific changes must remain identifiable in version control.
5. Compatibility research must prefer public documentation, independently written tests and observable behaviour.
6. CI and public release artifacts must not depend on privately supplied proprietary ROMs.
7. Third-party notices and corresponding source obligations must be preserved for releases.

## Clean implementation work

If LibreTOS later reimplements interfaces independently, implementation notes should identify the public specifications/tests used. Do not copy code from proprietary ROM disassemblies into LibreTOS.

## M0 status

No compatibility or independence claim is made by M0. M0 defines the policy and prepares for an audited upstream baseline in M1.
