#ifndef LIBRETOS_AMIGA_M8_CIA_TIMER_CONTRACT_H
#define LIBRETOS_AMIGA_M8_CIA_TIMER_CONTRACT_H

/* M8.4 native Amiga CIA/timer HAL contract. No Kickstart/Exec dependency. */

#define LIBRETOS_AMIGA_CIAA_BASE 0x00bfe001ul
#define LIBRETOS_AMIGA_CIAB_BASE 0x00bfd000ul
#define LIBRETOS_AMIGA_CIA_REG_STRIDE 0x100ul
#define LIBRETOS_AMIGA_CIA_TIMER_A 0u
#define LIBRETOS_AMIGA_CIA_TIMER_B 1u

struct libretos_amiga_cia_timer_state {
    unsigned short timer;
    unsigned short latch;
    unsigned short running;
    unsigned short irq_enabled;
};

void libretos_amiga_cia_init(void);
void libretos_amiga_timer_init(unsigned long ticks_per_second);
unsigned long libretos_amiga_timer_ticks(void);
void libretos_amiga_timer_ack(void);
void libretos_amiga_timer_shutdown(void);

#endif
