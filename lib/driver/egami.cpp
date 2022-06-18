#include <lib/driver/egami.h>
#include <sys/types.h>
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>
#include <fstream>

#include <sys/un.h>
#include <string.h>
#include <dirent.h>
#include <sys/reboot.h>

#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>

#include <lib/base/init.h>
#include <lib/base/init_num.h>
#include <lib/base/eerror.h>

eEGAMI *eEGAMI::instance;

eEGAMI::eEGAMI()
{
	_buffer = NULL;
	lcdfd = -1;
	locked = 0;
	instance = this;
}

eEGAMI *eEGAMI::getInstance()
{
	return instance;
}

eEGAMI::~eEGAMI()
{
	if (_buffer)
		delete [] _buffer;
	instance = NULL;
}

int eEGAMI::lock()
{
	if (locked)
		return -1;

	locked = 1;
	return lcdfd;
}

void eEGAMI::unlock()
{
	locked = 0;
}



