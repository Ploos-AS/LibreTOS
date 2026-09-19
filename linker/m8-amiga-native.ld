OUTPUT_FORMAT("elf32-m68k")
OUTPUT_ARCH(m68k)
ENTRY(_start)

MEMORY
{
    RAM (rwx) : ORIGIN = 0x00000000, LENGTH = 512K
}

SECTIONS
{
    .vectors ORIGIN(RAM) : ALIGN(2)
    {
        KEEP(*(.vectors))
    } > RAM

    .text : ALIGN(2)
    {
        *(.text*)
        *(.rodata*)
    } > RAM

    .data : ALIGN(2)
    {
        *(.data*)
    } > RAM

    .bss (NOLOAD) : ALIGN(2)
    {
        *(.bss*)
        *(COMMON)
    } > RAM

    __stack_top = ORIGIN(RAM) + LENGTH(RAM) - 4;
}
