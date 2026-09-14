#include <osbind.h>
#include <stdio.h>

#define STE_HSCROLL (*(volatile unsigned char *)0xffff8265L)
#define STE_DMA_MODE (*(volatile unsigned char *)0xffff8921L)

static int hscroll_written = -1;
static int hscroll_read = -1;
static int dma_written = -1;
static int dma_read = -1;

static long probe_enhanced_registers(void)
{
    unsigned char old_scroll;
    unsigned char old_dma;
    unsigned char scroll_test;
    unsigned char dma_test;

    old_scroll = STE_HSCROLL;
    scroll_test = (unsigned char)((old_scroll & 0xf0U) | 0x07U);
    STE_HSCROLL = scroll_test;
    hscroll_written = scroll_test & 0x0f;
    hscroll_read = STE_HSCROLL & 0x0f;
    STE_HSCROLL = old_scroll;

    old_dma = STE_DMA_MODE;
    dma_test = (unsigned char)((old_dma & 0x80U) | 0x03U);
    STE_DMA_MODE = dma_test;
    dma_written = dma_test & 0x83;
    dma_read = STE_DMA_MODE & 0x83;
    STE_DMA_MODE = old_dma;

    return 0;
}

static int write_result(const char *status, const char *stage,
                        int blit_before, int blit_disabled, int blit_enabled,
                        int blit_restored)
{
    char buf[1024];
    int len;
    int handle;

    len = sprintf(buf,
        "schema=1\r\n"
        "profile=ste-68000-1m-256k-us\r\n"
        "status=%s\r\n"
        "stage=%s\r\n"
        "hscroll_written=%d\r\n"
        "hscroll_read=%d\r\n"
        "dma_mode_written=0x%02x\r\n"
        "dma_mode_read=0x%02x\r\n"
        "blit_before=0x%04x\r\n"
        "blit_disabled=0x%04x\r\n"
        "blit_enabled=0x%04x\r\n"
        "blit_restored=0x%04x\r\n",
        status, stage,
        hscroll_written, hscroll_read,
        dma_written & 0xff, dma_read & 0xff,
        blit_before & 0xffff, blit_disabled & 0xffff,
        blit_enabled & 0xffff, blit_restored & 0xffff);

    handle = Fcreate("C:\\M3ENH.TXT", 0);
    if (handle < 0)
        return 1;
    if (Fwrite(handle, len, buf) != len) {
        Fclose(handle);
        return 1;
    }
    Fclose(handle);
    return 0;
}

int main(void)
{
    int before;
    int disabled;
    int enabled;
    int restored;
    int restore_mode;

    Supexec(probe_enhanced_registers);

    if (hscroll_read != hscroll_written) {
        write_result("FAIL", "hardware-scroll", 0, 0, 0, 0);
        return 2;
    }

    if ((dma_read & 0x03) != 0x03) {
        write_result("FAIL", "dma-sound-mode", 0, 0, 0, 0);
        return 3;
    }

    before = Blitmode(-1);
    if ((before & 0x0002) == 0) {
        write_result("FAIL", "blitter-present", before, before, before, before);
        return 4;
    }

    restore_mode = before & 0x0001;
    (void)Blitmode(0);
    disabled = Blitmode(-1);
    (void)Blitmode(1);
    enabled = Blitmode(-1);
    (void)Blitmode(restore_mode);
    restored = Blitmode(-1);

    if ((disabled & 0x0002) == 0 || (disabled & 0x0001) != 0) {
        write_result("FAIL", "blitter-disable", before, disabled, enabled, restored);
        return 5;
    }

    if ((enabled & 0x0003) != 0x0003) {
        write_result("FAIL", "blitter-enable", before, disabled, enabled, restored);
        return 6;
    }

    if ((restored & 0x0001) != restore_mode) {
        write_result("FAIL", "blitter-restore", before, disabled, enabled, restored);
        return 7;
    }

    if (write_result("PASS", "complete", before, disabled, enabled, restored))
        return 8;

    return 0;
}
