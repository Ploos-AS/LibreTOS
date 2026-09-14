#include <osbind.h>
#include <stdio.h>
#include <string.h>

#define COOKIE_MCH 0x5f4d4348L
#define COOKIE_SND 0x5f534e44L

static long mch_value = -1;
static long snd_value = -1;

static long read_cookies(void)
{
    long *jar = *(long **)0x5a0L;

    if (!jar)
        return 0;

    while (jar[0] != 0L) {
        if (jar[0] == COOKIE_MCH)
            mch_value = jar[1];
        else if (jar[0] == COOKIE_SND)
            snd_value = jar[1];
        jar += 2;
    }

    return 0;
}

static int write_result(const char *status, const char *stage,
                        int rez, long physbase, long logbase, int blitmode)
{
    char buf[1024];
    int len;
    int handle;

    len = sprintf(buf,
        "schema=1\r\n"
        "profile=ste-68000-1m-256k-us\r\n"
        "status=%s\r\n"
        "stage=%s\r\n"
        "mch=0x%08lx\r\n"
        "snd=0x%08lx\r\n"
        "getrez=%d\r\n"
        "physbase=0x%08lx\r\n"
        "logbase=0x%08lx\r\n"
        "blitmode=0x%04x\r\n",
        status, stage,
        mch_value, snd_value,
        rez, physbase, logbase, blitmode & 0xffff);

    handle = Fcreate("C:\\M3STE.TXT", 0);
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
    int rez;
    int blit;
    long phys;
    long log;

    Supexec(read_cookies);
    rez = Getrez();
    phys = (long)Physbase();
    log = (long)Logbase();
    blit = Blitmode(-1);

    if (((unsigned long)mch_value >> 16) != 1UL) {
        write_result("FAIL", "mch", rez, phys, log, blit);
        return 2;
    }

    if ((snd_value & 0x0003L) != 0x0003L) {
        write_result("FAIL", "snd", rez, phys, log, blit);
        return 3;
    }

    if (rez != 0) {
        write_result("FAIL", "getrez", rez, phys, log, blit);
        return 4;
    }

    if (phys == 0L || log == 0L || (phys & 1L) || (log & 1L)) {
        write_result("FAIL", "screen-base", rez, phys, log, blit);
        return 5;
    }

    if ((blit & 0x0002) == 0) {
        write_result("FAIL", "blitter", rez, phys, log, blit);
        return 6;
    }

    if (write_result("PASS", "complete", rez, phys, log, blit))
        return 7;

    return 0;
}
