#include <osbind.h>
#include <string.h>

#define RESULT_FILE "C:\\M2AESVD.TXT"

struct AESPB {
    short *control;
    short *global;
    short *intin;
    short *intout;
    long *addrin;
    long *addrout;
};

struct VDIPB {
    short *control;
    short *intin;
    short *ptsin;
    short *intout;
    short *ptsout;
};

static void aes_trap(struct AESPB *pb)
{
    register long d0 __asm__("d0") = 200;
    register unsigned long d1 __asm__("d1") = (unsigned long)pb;
    __asm__ volatile("trap #2" : "+d"(d0), "+d"(d1) : : "memory", "cc");
}

static void vdi_trap(struct VDIPB *pb)
{
    register long d0 __asm__("d0") = 115;
    register unsigned long d1 __asm__("d1") = (unsigned long)pb;
    __asm__ volatile("trap #2" : "+d"(d0), "+d"(d1) : : "memory", "cc");
}

static void append_long(char *buffer, long value)
{
    char tmp[16];
    char *p = tmp + sizeof(tmp);
    unsigned long magnitude;
    int negative = value < 0;

    *--p = '\0';
    if (negative)
        magnitude = 0UL - (unsigned long)value;
    else
        magnitude = (unsigned long)value;

    do {
        *--p = (char)('0' + (magnitude % 10UL));
        magnitude /= 10UL;
    } while (magnitude != 0UL);

    if (negative)
        *--p = '-';
    strcat(buffer, p);
}

static void write_result(const char *status, const char *stage, int app_id, int phys_handle, int vdi_handle)
{
    char buffer[512];
    long handle;
    long length;

    buffer[0] = '\0';
    strcat(buffer, "schema=1\r\nstatus=");
    strcat(buffer, status);
    strcat(buffer, "\r\nprofile=st-68000-1m-192k-us\r\nstage=");
    strcat(buffer, stage);
    strcat(buffer, "\r\ntests=appl_init,graf_handle,v_opnvwk,v_pline,v_clsvwk,appl_exit\r\n");

    strcat(buffer, "aes_app_id=");
    append_long(buffer, (long)app_id);
    strcat(buffer, "\r\nphys_handle=");
    append_long(buffer, (long)phys_handle);
    strcat(buffer, "\r\nvdi_handle=");
    append_long(buffer, (long)vdi_handle);
    strcat(buffer, "\r\n");

    handle = Fcreate(RESULT_FILE, 0);
    if (handle < 0)
        return;
    length = (long)strlen(buffer);
    (void)Fwrite((int)handle, length, buffer);
    (void)Fclose((int)handle);
}

static void fail(const char *stage, int app_id, int phys_handle, int vdi_handle)
{
    write_result("FAIL", stage, app_id, phys_handle, vdi_handle);
    Pterm(1);
}

static int aes_call(short opcode, short nintin, short nintout, short naddrin, short naddrout,
                    short *global, short *intin, short *intout, long *addrin, long *addrout)
{
    short control[5];
    struct AESPB pb;

    control[0] = opcode;
    control[1] = nintin;
    control[2] = nintout;
    control[3] = naddrin;
    control[4] = naddrout;

    pb.control = control;
    pb.global = global;
    pb.intin = intin;
    pb.intout = intout;
    pb.addrin = addrin;
    pb.addrout = addrout;
    aes_trap(&pb);
    return intout[0];
}

int main(void)
{
    short global[15] = {0};
    short aes_intin[16] = {0};
    short aes_intout[16] = {0};
    long aes_addrin[8] = {0};
    long aes_addrout[8] = {0};
    short vdi_control[12] = {0};
    short vdi_intin[128] = {0};
    short vdi_ptsin[128] = {0};
    short vdi_intout[128] = {0};
    short vdi_ptsout[128] = {0};
    struct VDIPB vpb;
    int app_id = -1;
    int phys_handle = -1;
    int vdi_handle = -1;
    int i;

    app_id = aes_call(10, 0, 1, 0, 0, global, aes_intin, aes_intout, aes_addrin, aes_addrout);
    if (app_id < 0)
        fail("appl_init", app_id, phys_handle, vdi_handle);

    memset(aes_intout, 0, sizeof(aes_intout));
    phys_handle = aes_call(77, 0, 5, 0, 0, global, aes_intin, aes_intout, aes_addrin, aes_addrout);
    if (phys_handle <= 0)
        fail("graf_handle", app_id, phys_handle, vdi_handle);

    vpb.control = vdi_control;
    vpb.intin = vdi_intin;
    vpb.ptsin = vdi_ptsin;
    vpb.intout = vdi_intout;
    vpb.ptsout = vdi_ptsout;

    memset(vdi_control, 0, sizeof(vdi_control));
    memset(vdi_intin, 0, sizeof(vdi_intin));
    for (i = 0; i < 10; ++i)
        vdi_intin[i] = 1;
    vdi_intin[10] = 2;
    vdi_control[0] = 100;
    vdi_control[3] = 11;
    vdi_control[6] = (short)phys_handle;
    vdi_trap(&vpb);
    vdi_handle = vdi_control[6];
    if (vdi_handle <= 0)
        fail("v_opnvwk", app_id, phys_handle, vdi_handle);

    memset(vdi_control, 0, sizeof(vdi_control));
    vdi_ptsin[0] = 10;
    vdi_ptsin[1] = 10;
    vdi_ptsin[2] = 40;
    vdi_ptsin[3] = 40;
    vdi_control[0] = 6;
    vdi_control[1] = 2;
    vdi_control[6] = (short)vdi_handle;
    vdi_trap(&vpb);

    memset(vdi_control, 0, sizeof(vdi_control));
    vdi_control[0] = 101;
    vdi_control[6] = (short)vdi_handle;
    vdi_trap(&vpb);

    memset(aes_intout, 0, sizeof(aes_intout));
    if (aes_call(19, 0, 1, 0, 0, global, aes_intin, aes_intout, aes_addrin, aes_addrout) <= 0)
        fail("appl_exit", app_id, phys_handle, vdi_handle);

    write_result("PASS", "complete", app_id, phys_handle, vdi_handle);
    Pterm(0);
    return 0;
}
