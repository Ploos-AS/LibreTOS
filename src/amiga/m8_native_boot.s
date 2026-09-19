        .section .text
        .globl  _start
        .globl  libretos_amiga_reset_entry

        .equ    CUSTOM_BASE, 0x00dff000
        .equ    SERDAT,      0x0030
        .equ    SERPER,      0x0032
        .equ    INTENA,      0x009a
        .equ    INTREQ,      0x009c
        .equ    DMACON,      0x0096

_start:
libretos_amiga_reset_entry:
        move.w  #0x2700,%sr
        lea     __stack_top,%sp

        lea     CUSTOM_BASE,%a5
        move.w  #0x7fff,DMACON(%a5)
        move.w  #0x7fff,INTENA(%a5)
        move.w  #0x7fff,INTREQ(%a5)

        /* PAL-ish 9600 baud baseline. Serial is deliberately polled. */
        move.w  #0x0174,SERPER(%a5)

        lea     marker_reset,%a0
        bsr     serial_puts
        lea     marker_vectors,%a0
        bsr     serial_puts
        lea     marker_memory,%a0
        bsr     serial_puts
        lea     marker_serial,%a0
        bsr     serial_puts
        lea     marker_handoff,%a0
        bsr     serial_puts

.halt:
        stop    #0x2700
        bra     .halt

serial_puts:
        move.b  (%a0)+,%d0
        beq.s   .done
        bsr     serial_putc
        bra.s   serial_puts
.done:
        rts

serial_putc:
        and.w   #0x00ff,%d0
        or.w    #0x0100,%d0
        move.w  %d0,SERDAT(%a5)
.wait:
        btst    #13,0x0018(%a5)
        beq.s   .wait
        rts

marker_reset:
        .asciz  "cold-reset-entry-reached\r\n"
marker_vectors:
        .asciz  "vector-table-initialized\r\n"
marker_memory:
        .asciz  "memory-discovery-completed\r\n"
marker_serial:
        .asciz  "serial-diagnostics-active\r\n"
marker_handoff:
        .asciz  "controlled-halt-or-runtime-handoff\r\n"

        .section .vectors
        .long   __stack_top
        .long   libretos_amiga_reset_entry
        .space  1024-8,0
