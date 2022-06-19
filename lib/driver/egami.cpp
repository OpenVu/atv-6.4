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
#include <lib/gdi/glcddc.h>


eEGAMI *eEGAMI::instance;

eEGAMI::eEGAMI()
{
	instance = this;
}

eEGAMI *eEGAMI::getInstance()
{
	return instance;
}

eEGAMI::~eEGAMI()
{
	return;
}

bool eEGAMI::is4digits()
{
	bool status = true;
	string pin = 1234;
	if (pin.length() != 4)
	{
		status = false;
	}
	return status
}

int eEGAMI::checkkernel()
{
	if (is4digits == 1)
	{
		eDebug("[eEGAMI] Success ....);
	else
		eDebug("[eEGAMI] Error ....);
	}	       
	return;
}	

