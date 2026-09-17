#ifndef LIBRETOS_AMIGA_M8_SERIAL_CONTRACT_H
#define LIBRETOS_AMIGA_M8_SERIAL_CONTRACT_H

/*
 * M8.7 native Amiga serial diagnostics HAL contract.
 *
 * Paula's serial registers provide the early diagnostic channel used before
 * higher-level LibreTOS device services exist. No Kickstart/Exec dependency.
 */

#define LIBRETOS_AMIGA_SERIAL_CUSTOM_BASE 0x00dff000ul
#define LIBRETOS_AMIGA_SERDATR_OFFSET 0x0018ul
#define LIBRETOS_AMIGA_SERDAT_OFFSET 0x0030ul
#define LIBRETOS_AMIGA_SERPER_OFFSET 0x0032ul
#define LIBRETOS_AMIGA_SERIAL_TX_READY 0x2000u
#define LIBRETOS_AMIGA_SERIAL_STOP_BIT 0x0100u

struct libretos_amiga_serial_state {
    unsigned short initialized;
    unsigned short period;
    unsigned long baud;
};

void libretos_amiga_serial_hal_init(unsigned long baud);
int libretos_amiga_serial_tx_ready(void);
void libretos_amiga_serial_hal_putc(unsigned char value);
void libretos_amiga_serial_hal_puts(const char *text);
void libretos_amiga_serial_hal_shutdown(void);

#endif
