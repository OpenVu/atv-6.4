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
	bool name = false;
	int age = 1;
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

int eEGAMI::checkkernel()
{
	if (age == 1)
	{	
		name = true;
	}	
	if (name)
	{
		eDebug("[eEGAMI] success ...");	
	}
	else
	{
		eDebug("[eEGAMI] Error ...");
	}

	return name;
}

