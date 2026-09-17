#ifndef LIBRETOS_AMIGA_M8_VIDEO_CONTRACT_H
#define LIBRETOS_AMIGA_M8_VIDEO_CONTRACT_H

/* M8.8 native Amiga OCS display HAL contract. No Kickstart/Exec dependency. */

#define LIBRETOS_AMIGA_VIDEO_CUSTOM_BASE 0x00dff000ul
#define LIBRETOS_AMIGA_DIWSTRT_OFFSET 0x008eul
#define LIBRETOS_AMIGA_DIWSTOP_OFFSET 0x0090ul
#define LIBRETOS_AMIGA_DDFSTRT_OFFSET 0x0092ul
#define LIBRETOS_AMIGA_DDFSTOP_OFFSET 0x0094ul
#define LIBRETOS_AMIGA_BPLCON0_OFFSET 0x0100ul
#define LIBRETOS_AMIGA_BPL1PTH_OFFSET 0x00e0ul
#define LIBRETOS_AMIGA_COLOR00_OFFSET 0x0180ul
#define LIBRETOS_AMIGA_VIDEO_MAX_BITPLANES 6u

struct libretos_amiga_video_mode {
    unsigned short width;
    unsigned short height;
    unsigned short depth;
    unsigned short interlaced;
};

struct libretos_amiga_video_state {
    struct libretos_amiga_video_mode mode;
    unsigned long bitplane[LIBRETOS_AMIGA_VIDEO_MAX_BITPLANES];
    unsigned short initialized;
};

void libretos_amiga_video_init(const struct libretos_amiga_video_mode *mode);
void libretos_amiga_video_set_bitplane(unsigned short plane, unsigned long address);
void libretos_amiga_video_set_color(unsigned short index, unsigned short rgb12);
void libretos_amiga_video_enable(void);
void libretos_amiga_video_disable(void);
void libretos_amiga_video_shutdown(void);

#endif
