#include <osbind.h>
#include <stdio.h>

#define COOKIE_MCH 0x5f4d4348L
#define COOKIE_CPU 0x5f435055L
#define COOKIE_VDO 0x5f56444fL

#ifndef PROFILE_NAME
#define PROFILE_NAME "unknown"
#endif
#ifndef RESULT_FILE
#define RESULT_FILE "C:\\M6FAL.TXT"
#endif

static long mch_value = -1L;
static long cpu_value = -1L;
static long vdo_value = -1L;

static long read_platform_state(void)
{
    long *jar = *(long **)0x5a0L;
    if (!jar)
        return 0L;
    while (jar[0] != 0L) {
        if (jar[0] == COOKIE_MCH) mch_value = jar[1];
        else if (jar[0] == COOKIE_CPU) cpu_value = jar[1];
        else if (jar[0] == COOKIE_VDO) vdo_value = jar[1];
        jar += 2;
    }
    return 0L;
}

static int write_result(const char *status, const char *stage,
                        int rez, long physbase, long logbase)
{
    char buf[1024];
    int len, handle;
    len = sprintf(buf,
        "schema=1\r\nprofile=%s\r\nstatus=%s\r\nstage=%s\r\n"
        "mch=0x%08lx\r\ncpu=%ld\r\nvdo=0x%08lx\r\ngetrez=%d\r\n"
        "physbase=0x%08lx\r\nlogbase=0x%08lx\r\n",
        PROFILE_NAME, status, stage, mch_value, cpu_value, vdo_value,
        rez, physbase, logbase);
    handle = Fcreate(RESULT_FILE, 0);
    if (handle < 0) return 1;
    if (Fwrite(handle, len, buf) != len) { Fclose(handle); return 1; }
    Fclose(handle);
    return 0;
}

int main(void)
{
    int rez;
    long phys, log;
    unsigned long family;
    Supexec(read_platform_state);
    rez = Getrez();
    phys = (long)Physbase();
    log = (long)Logbase();
    family = ((unsigned long)mch_value >> 16) & 0xffffUL;

    if (family != 3UL) { write_result("FAIL", "mch-falcon-family", rez, phys, log); return 2; }
    if (cpu_value != 30L) { write_result("FAIL", "cpu-68030", rez, phys, log); return 3; }
    if (((unsigned long)vdo_value >> 16) != 3UL) { write_result("FAIL", "vdo-falcon", rez, phys, log); return 4; }
    if (phys == 0L || log == 0L || (phys & 1L) || (log & 1L)) {
        write_result("FAIL", "screen-base", rez, phys, log); return 5;
    }
    if (write_result("PASS", "complete", rez, phys, log)) return 6;
    return 0;
}
