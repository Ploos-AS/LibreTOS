#ifndef LIBRETOS_AMIGA_M8_INTERRUPT_CONTRACT_H
#define LIBRETOS_AMIGA_M8_INTERRUPT_CONTRACT_H

/*
 * M8.6 native Amiga interrupt-controller HAL contract.
 *
 * The OCS/ECS baseline uses the custom-chip interrupt request/enable
 * registers directly. This layer remains independent of Kickstart/Exec and
 * gives the portable LibreTOS core a small, explicit interrupt interface.
 */

#define LIBRETOS_AMIGA_CUSTOM_BASE 0x00dff000ul
#define LIBRETOS_AMIGA_INTENA_OFFSET 0x009aul
#define LIBRETOS_AMIGA_INTREQ_OFFSET 0x009cul

#define LIBRETOS_AMIGA_INT_SETCLR 0x8000u
#define LIBRETOS_AMIGA_INT_MASTER 0x4000u
#define LIBRETOS_AMIGA_INT_PORTS 0x0008u
#define LIBRETOS_AMIGA_INT_VERTB 0x0020u

struct libretos_amiga_interrupt_state {
    unsigned short initialized;
    unsigned short master_enabled;
    unsigned short enabled_mask;
    unsigned short pending_mask;
};

void libretos_amiga_interrupt_init(void);
void libretos_amiga_interrupt_enable(unsigned short mask);
void libretos_amiga_interrupt_disable(unsigned short mask);
unsigned short libretos_amiga_interrupt_pending(void);
void libretos_amiga_interrupt_ack(unsigned short mask);
void libretos_amiga_interrupt_shutdown(void);

#endif
