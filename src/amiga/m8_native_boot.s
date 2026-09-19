        .section .text
        .globl  _start
        .globl  libretos_amiga_reset_entry

_start:
libretos_amiga_reset_entry:
        lea     __stack_top,%sp
        move.l  #0x00000000,%d0
        move.l  %d0,%d1
        move.w  #0x0000,%d2
        bra     .halt

.halt:
        stop    #0x2700
        bra     .halt

        .section .vectors
        .long   __stack_top
        .long   libretos_amiga_reset_entry
        .space  1024-8,0
