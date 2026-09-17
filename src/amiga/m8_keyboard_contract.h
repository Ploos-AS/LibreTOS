#ifndef LIBRETOS_AMIGA_M8_KEYBOARD_CONTRACT_H
#define LIBRETOS_AMIGA_M8_KEYBOARD_CONTRACT_H

/*
 * M8.5 native Amiga keyboard HAL contract.
 *
 * The baseline OCS/68000 target receives keyboard serial data through CIAA.
 * This contract remains independent of Kickstart/Exec and keeps raw Amiga
 * key handling below the portable LibreTOS input layer.
 */

#define LIBRETOS_AMIGA_KEYBOARD_CIA_BASE 0x00bfe001ul
#define LIBRETOS_AMIGA_KEYBOARD_RAW_RELEASE 0x80u
#define LIBRETOS_AMIGA_KEYBOARD_RAW_CODE_MASK 0x7fu
#define LIBRETOS_AMIGA_KEYBOARD_QUEUE_SIZE 32u

struct libretos_amiga_key_event {
    unsigned char raw_code;
    unsigned char released;
};

struct libretos_amiga_keyboard_state {
    unsigned short initialized;
    unsigned short irq_enabled;
    unsigned short queue_head;
    unsigned short queue_tail;
};

void libretos_amiga_keyboard_init(void);
void libretos_amiga_keyboard_irq(void);
int libretos_amiga_keyboard_poll(struct libretos_amiga_key_event *event);
void libretos_amiga_keyboard_ack(void);
void libretos_amiga_keyboard_shutdown(void);

#endif
