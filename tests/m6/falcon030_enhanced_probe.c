#include <osbind.h>
#include <stdio.h>

#define COOKIE_VDO 0x5f56444fL
#define COOKIE_SND 0x5f534e44L
#define COOKIE_FPU 0x5f465055L

#ifndef PROFILE_NAME
#define PROFILE_NAME "unknown"
#endif
#ifndef RESULT_FILE
#define RESULT_FILE "C:\\M6FALE.TXT"
#endif

static long vdo_value = -1L;
static long snd_value = -1L;
static long fpu_value = -1L;

static long read_cookies(void)
{
    long *jar = *(long **)0x5a0L;
    if (!jar) return 0L;
    while (jar[0] != 0L) {
        if (jar[0] == COOKIE_VDO) vdo_value = jar[1];
        else if (jar[0] == COOKIE_SND) snd_value = jar[1];
        else if (jar[0] == COOKIE_FPU) fpu_value = jar[1];
        jar += 2;
    }
    return 0L;
}

static int write_result(const char *status, const char *stage)
{
    char buf[768];
    int len, handle;
    len = sprintf(buf,
        "schema=1\r\nprofile=%s\r\nstatus=%s\r\nstage=%s\r\n"
        "vdo=0x%08lx\r\nsnd=0x%08lx\r\nfpu=0x%08lx\r\n",
        PROFILE_NAME, status, stage, vdo_value, snd_value, fpu_value);
    handle = Fcreate(RESULT_FILE, 0);
    if (handle < 0) return 1;
    if (Fwrite(handle, len, buf) != len) { Fclose(handle); return 1; }
    Fclose(handle);
    return 0;
}

int main(void)
{
    Supexec(read_cookies);
    if (((unsigned long)vdo_value >> 16) != 3UL) {
        write_result("FAIL", "videl-cookie"); return 2;
    }
    if (snd_value < 0L) {
        write_result("FAIL", "sound-cookie"); return 3;
    }
    if ((snd_value & 0x07L) == 0L) {
        write_result("FAIL", "sound-capabilities"); return 4;
    }
    if (write_result("PASS", "complete")) return 5;
    return 0;
}
