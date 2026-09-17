#ifndef LIBRETOS_AMIGA_M8_STARTUP_CONTRACT_H
#define LIBRETOS_AMIGA_M8_STARTUP_CONTRACT_H

/*
 * M8.2 native Amiga startup/HAL contract.
 *
 * This header deliberately contains no Kickstart/Exec dependencies.  The
 * first LibreTOS Amiga target owns the machine from reset and must be able to
 * bring up enough OCS/68000 hardware for deterministic diagnostics before
 * higher-level GEMDOS services exist.
 */

#define LIBRETOS_AMIGA_M8_PROFILE_ID "amiga-ocs-68000-1m"
#define LIBRETOS_AMIGA_M8_CPU "68000"
#define LIBRETOS_AMIGA_M8_CHIPSET "OCS"

#define LIBRETOS_AMIGA_VECTOR_COUNT 256u
#define LIBRETOS_AMIGA_CHIP_RAM_BASE 0x00000000ul
#define LIBRETOS_AMIGA_CUSTOM_BASE 0x00dff000ul
#define LIBRETOS_AMIGA_CIAA_BASE 0x00bfe001ul
#define LIBRETOS_AMIGA_CIAB_BASE 0x00bfd000ul

struct libretos_amiga_memory_map {
    unsigned long chip_base;
    unsigned long chip_size;
    unsigned long fast_base;
    unsigned long fast_size;
};

struct libretos_amiga_startup_state {
    unsigned long initial_ssp;
    unsigned long reset_pc;
    unsigned short vectors_installed;
    unsigned short exceptions_ready;
    unsigned short serial_ready;
    struct libretos_amiga_memory_map memory;
};

void libretos_amiga_reset_entry(void);
void libretos_amiga_vectors_init(void);
void libretos_amiga_exceptions_init(void);
void libretos_amiga_memory_discover(struct libretos_amiga_memory_map *map);
void libretos_amiga_serial_init(void);
void libretos_amiga_serial_putc(char value);
void libretos_amiga_serial_puts(const char *text);
void libretos_amiga_halt(void);

#endif
