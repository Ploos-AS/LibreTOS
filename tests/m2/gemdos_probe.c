#include <osbind.h>
#include <string.h>

#define RESULT_FILE "C:\\M2GEMDOS.TXT"
#define TEMP_FILE   "C:\\M2TMP.DAT"
#define TEMP_DIR    "C:\\M2DIR"

static void write_result(const char *status, const char *stage)
{
    char buffer[512];
    long handle;
    long length;

    buffer[0] = '\0';
    strcat(buffer, "schema=1\r\nstatus=");
    strcat(buffer, status);
    strcat(buffer, "\r\nprofile=st-68000-1m-192k-us\r\nstage=");
    strcat(buffer, stage);
    strcat(buffer, "\r\ntests=Dgetdrv,Dcreate,Ddelete,Fcreate,Fwrite,Fclose,Fopen,Fread,Fdelete,Pterm\r\n");

    handle = Fcreate(RESULT_FILE, 0);
    if (handle < 0)
        return;

    length = (long)strlen(buffer);
    (void)Fwrite((int)handle, length, buffer);
    (void)Fclose((int)handle);
}

static void fail(const char *stage)
{
    write_result("FAIL", stage);
    Pterm(1);
}

int main(void)
{
    static const char payload[] = "LibreTOS M2.3 GEMDOS regression payload\r\n";
    char readback[sizeof(payload)];
    long handle;
    long rc;

    if (Dgetdrv() < 0)
        fail("Dgetdrv");

    rc = Dcreate(TEMP_DIR);
    if (rc != 0)
        fail("Dcreate");

    rc = Ddelete(TEMP_DIR);
    if (rc != 0)
        fail("Ddelete");

    handle = Fcreate(TEMP_FILE, 0);
    if (handle < 0)
        fail("Fcreate");

    rc = Fwrite((int)handle, (long)(sizeof(payload) - 1), payload);
    if (rc != (long)(sizeof(payload) - 1))
        fail("Fwrite");

    rc = Fclose((int)handle);
    if (rc != 0)
        fail("Fclose-write");

    handle = Fopen(TEMP_FILE, 0);
    if (handle < 0)
        fail("Fopen");

    memset(readback, 0, sizeof(readback));
    rc = Fread((int)handle, (long)(sizeof(payload) - 1), readback);
    if (rc != (long)(sizeof(payload) - 1))
        fail("Fread");

    rc = Fclose((int)handle);
    if (rc != 0)
        fail("Fclose-read");

    if (memcmp(readback, payload, sizeof(payload) - 1) != 0)
        fail("compare");

    rc = Fdelete(TEMP_FILE);
    if (rc != 0)
        fail("Fdelete");

    write_result("PASS", "complete");
    Pterm(0);
    return 0;
}
