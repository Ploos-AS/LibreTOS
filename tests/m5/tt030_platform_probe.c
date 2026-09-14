#include <osbind.h>
#include <stdio.h>

#define COOKIE_MCH 0x5f4d4348L
#define COOKIE_CPU 0x5f435055L

#ifndef PROFILE_NAME
#define PROFILE_NAME "unknown"
#endif
#ifndef RESULT_FILE
#define RESULT_FILE "C:\\M5TT.TXT"
#endif

static long mch_value = -1L;
static long cpu_value = -1L;
static long ramtop_value = 0L;

static long read_platform_state(void)
{
    long *jar = *(long **)0x5a0L;

    ramtop_value = *(long *)0x5a4L;
    if (!jar)
        return 0L;

    while (jar[0] != 0L) {
        if (jar[0] == COOKIE_MCH)
            mch_value = jar[1];
        else if (jar[0] == COOKIE_CPU)
            cpu_value = jar[1];
        jar += 2;
    }
    return 0L;
}

static int write_result(const char *status, const char *stage,
                        int rez, long physbase, long logbase)
{
    char buf[1024];
    int len;
    int handle;

    len = sprintf(buf,
        "schema=1\r\n"
        "profile=%s\r\n"
        "status=%s\r\n"
        "stage=%s\r\n"
        "mch=0x%08lx\r\n"
        "cpu=%ld\r\n"
        "ramtop=0x%08lx\r\n"
        "getrez=%d\r\n"
        "physbase=0x%08lx\r\n"
        "logbase=0x%08lx\r\n",
        PROFILE_NAME, status, stage,
        mch_value, cpu_value, ramtop_value,
        rez, physbase, logbase);

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
    int rez;
    long phys;
    long log;
    unsigned long family;

    Supexec(read_platform_state);
    rez = Getrez();
    phys = (long)Physbase();
    log = (long)Logbase();
    family = ((unsigned long)mch_value >> 16) & 0xffffUL;

    if (family != 2UL) {
        write_result("FAIL", "mch-tt-family", rez, phys, log);
        return 2;
    }
    if (cpu_value != 30L) {
        write_result("FAIL", "cpu-68030", rez, phys, log);
        return 3;
    }
    if (ramtop_value == 0L || (unsigned long)ramtop_value <= 0x01000000UL) {
        write_result("FAIL", "tt-ram", rez, phys, log);
        return 4;
    }
    if (rez != 0) {
        write_result("FAIL", "getrez", rez, phys, log);
        return 5;
    }
    if (phys == 0L || log == 0L || (phys & 1L) || (log & 1L)) {
        write_result("FAIL", "screen-base", rez, phys, log);
        return 6;
    }

    if (write_result("PASS", "complete", rez, phys, log))
        return 7;
    return 0;
}
