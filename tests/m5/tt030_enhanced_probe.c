#include <osbind.h>
#include <stdio.h>

#define COOKIE_VDO 0x5f56444fL
#define COOKIE_FPU 0x5f465055L
#define COOKIE_SND 0x5f534e44L
#define COOKIE_FRB 0x5f465242L

#define VDO_TT 0x00020000L
#define SND_PSG 0x01L
#define SND_8BIT 0x02L

#ifndef PROFILE_NAME
#define PROFILE_NAME "unknown"
#endif
#ifndef RESULT_FILE
#define RESULT_FILE "C:\\M5TTE.TXT"
#endif

static long vdo_value = -1L;
static long fpu_value = -1L;
static long snd_value = -1L;
static long frb_value = 0L;

static long read_cookies(void)
{
    long *jar = *(long **)0x5a0L;
    if (!jar)
        return 0L;

    while (jar[0] != 0L) {
        if (jar[0] == COOKIE_VDO)
            vdo_value = jar[1];
        else if (jar[0] == COOKIE_FPU)
            fpu_value = jar[1];
        else if (jar[0] == COOKIE_SND)
            snd_value = jar[1];
        else if (jar[0] == COOKIE_FRB)
            frb_value = jar[1];
        jar += 2;
    }
    return 0L;
}

static int write_result(const char *status, const char *stage)
{
    char buf[768];
    int len;
    int handle;

    len = sprintf(buf,
        "schema=1\r\n"
        "profile=%s\r\n"
        "status=%s\r\n"
        "stage=%s\r\n"
        "vdo=0x%08lx\r\n"
        "fpu=0x%08lx\r\n"
        "snd=0x%08lx\r\n"
        "frb=0x%08lx\r\n",
        PROFILE_NAME, status, stage,
        vdo_value, fpu_value, snd_value, frb_value);

    handle = Fcreate(RESULT_FILE, 0);
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
    Supexec(read_cookies);

    if (vdo_value != VDO_TT) {
        write_result("FAIL", "tt-video");
        return 2;
    }
    if (fpu_value < 0L) {
        write_result("FAIL", "fpu-cookie");
        return 3;
    }
    if ((snd_value & (SND_PSG | SND_8BIT)) != (SND_PSG | SND_8BIT)) {
        write_result("FAIL", "tt-dma-sound");
        return 4;
    }
    if (frb_value == 0L) {
        write_result("FAIL", "frb-cookie");
        return 5;
    }

    if (write_result("PASS", "complete"))
        return 6;
    return 0;
}
