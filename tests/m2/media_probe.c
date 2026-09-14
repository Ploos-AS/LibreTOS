#include <osbind.h>
#include <string.h>

#define RESULT_FILE "C:\\M2MEDIA.TXT"
#define FIXTURE_FILE "A:\\FIXTURE.TXT"
#define PERSIST_FILE "A:\\PERSIST.TXT"

static void write_result(const char *status, const char *stage, const char *marker)
{
    char buffer[512];
    long handle;
    long length;

    buffer[0] = '\0';
    strcat(buffer, "schema=1\r\nstatus=");
    strcat(buffer, status);
    strcat(buffer, "\r\nprofile=st-68000-1m-192k-us\r\nstage=");
    strcat(buffer, stage);
    strcat(buffer, "\r\nmedia_marker=");
    strcat(buffer, marker ? marker : "unknown");
    strcat(buffer, "\r\ntests=fixture-read,media-clean,write,readback,persist\r\n");

    handle = Fcreate(RESULT_FILE, 0);
    if (handle < 0)
        return;
    length = (long)strlen(buffer);
    (void)Fwrite((int)handle, length, buffer);
    (void)Fclose((int)handle);
}

static void fail(const char *stage, const char *marker)
{
    write_result("FAIL", stage, marker);
    Pterm(1);
}

int main(void)
{
    static const char payload[] = "LibreTOS M2.5 floppy write/readback\r\n";
    char fixture[64];
    char readback[sizeof(payload)];
    const char *marker = "unknown";
    long handle;
    long rc;

    memset(fixture, 0, sizeof(fixture));
    handle = Fopen(FIXTURE_FILE, 0);
    if (handle < 0)
        fail("fixture-open", marker);
    rc = Fread((int)handle, (long)(sizeof(fixture) - 1), fixture);
    (void)Fclose((int)handle);
    if (rc <= 0)
        fail("fixture-read", marker);

    if (strstr(fixture, "MEDIA-A") != 0)
        marker = "MEDIA-A";
    else if (strstr(fixture, "MEDIA-B") != 0)
        marker = "MEDIA-B";
    else
        fail("fixture-marker", marker);

    handle = Fopen(PERSIST_FILE, 0);
    if (handle >= 0) {
        (void)Fclose((int)handle);
        fail("media-not-clean", marker);
    }

    handle = Fcreate(PERSIST_FILE, 0);
    if (handle < 0)
        fail("write-create", marker);
    rc = Fwrite((int)handle, (long)(sizeof(payload) - 1), payload);
    if (rc != (long)(sizeof(payload) - 1))
        fail("write", marker);
    if (Fclose((int)handle) != 0)
        fail("write-close", marker);

    memset(readback, 0, sizeof(readback));
    handle = Fopen(PERSIST_FILE, 0);
    if (handle < 0)
        fail("readback-open", marker);
    rc = Fread((int)handle, (long)(sizeof(payload) - 1), readback);
    if (rc != (long)(sizeof(payload) - 1))
        fail("readback-read", marker);
    if (Fclose((int)handle) != 0)
        fail("readback-close", marker);
    if (memcmp(readback, payload, sizeof(payload) - 1) != 0)
        fail("readback-compare", marker);

    write_result("PASS", "complete", marker);
    Pterm(0);
    return 0;
}
