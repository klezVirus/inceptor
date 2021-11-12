// Libraries: Ws2_32.lib
// Headers: <windows.h>

struct timeval tv;
tv.tv_sec = ####SECONDS####;
tv.tv_usec = ####MICROSECONDS####;

int ret = 0;

do
{
  ret = select(1, NULL, NULL, NULL, &tv);
}
while((ret == -1)&&(errno == EINTR));
