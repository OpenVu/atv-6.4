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

eEGAMI *eEGAMI::instance= 0;

eEGAMI *eEGAMI::getInstance()
{
	return instance;
}

eEGAMI::~eEGAMI()
{
	return;
}

eEGAMI::eEGAMI()
{
	ASSERT(!instance);
	instance = this;

}

/** detecting whether base is starts with str
 */
bool eEGAMI::startsWith (char* base, char* str) 
{
	return (strstr(base, str) - base) == 0;
}

/** detecting whether base is ends with str
 */
bool eEGAMI::endsWith (char* base, char* str) 
{
	int blen = strlen(base);
	int slen = strlen(str);
	return (blen >= slen) && (0 == strcmp(base + blen - slen, str));
}

/**
* Check if a file exist using stat() function
* return 1 if the file exist otherwise return 0
*/
bool eEGAMI::fileExists(const char *filename) 
{
	std::ifstream ifile(filename);
	return (bool)ifile;
}

/** reading file and return value from it
 * */
char* eEGAMI::ReadProcEntry(char *filename)
{
	FILE *boxtype_file = fopen(filename,"r");
	char boxtype_name[30];
	char *real_boxtype_name = NULL;
	char c;
	int i = 0;
	
	if(boxtype_file)
	{
		while ((c = fgetc(boxtype_file)) != EOF && i < sizeof(boxtype_name) - 2)
		{
			if (c == '\n')
			{
				i--;
				break;
			}
			boxtype_name[i] = c;
			i++;
		}
		boxtype_name[i+1] = '\0';
		real_boxtype_name = (char*)malloc(strlen(boxtype_name) + 1);
		if (real_boxtype_name)
			strcpy(real_boxtype_name, boxtype_name);
		
		fclose(boxtype_file);
	}
	else
	{
		puts("[EGAMI] ERROR\n");
		return("Unknown");
	}
	
	return real_boxtype_name;
}

bool eEGAMI::checkkernel()		
{
	if(fileExists("/bin/emud"))
	{
		eDebug("[EGAMI] Starting EGAMI OS...");
	}
	else
	{
		sync();
		reboot(RB_AUTOBOOT);
	}
	
	char *boxtype_name = NULL;
	char *vuboxtype_name = NULL;
	char *boxmodel_name = NULL;
	boxtype_name = ReadProcEntry("/proc/stb/info/boxtype");
	vuboxtype_name = ReadProcEntry("/proc/stb/info/vumodel");
	boxmodel_name = ReadProcEntry("/proc/stb/info/model");
	if (((startsWith(boxtype_name, "ini")) && (endsWith(boxtype_name, "lx"))) || ((startsWith(boxtype_name, "ini")) && (endsWith(boxtype_name, "de"))))
	{
		puts("[EGAMI] Golden Interstar\n");
	}
	else if((startsWith(boxtype_name, "ini")) && (endsWith(boxtype_name, "sv")))
	{
		puts("[EGAMI] Miraclebox\n");
	}
	else if((startsWith(boxtype_name, "7000")) || (startsWith(boxtype_name, "7100")) || (startsWith(boxtype_name, "7300")) || (startsWith(boxtype_name, "7400")))
	{
		puts("[EGAMI] Ceryon\n");
	}
	else if(startsWith(boxtype_name, "g300"))
	{
		puts("[EGAMI] BroadMedia\n");
	}
	else if((startsWith(boxtype_name, "ini")) && (endsWith(boxtype_name, "ru")))
	{
		puts("[EGAMI] Sezam\n");
	}
	else if((startsWith(boxtype_name, "ini")) && (endsWith(boxtype_name, "am")))
	{
		puts("[EGAMI] Atemio\n");
	}
	else if((startsWith(boxtype_name, "ini")) && (endsWith(boxtype_name, "au")))
	{
		puts("[EGAMI] Beyonwiz\n");
	}
	else if((startsWith(boxtype_name, "ini")) || (startsWith(boxtype_name, "uni")))
	{
		puts("[EGAMI] UNiBOX\n");
	}
	else if(startsWith(boxtype_name, "ini"))
	{
		puts("[EGAMI] INI-OEM\n");
	}
	else if(startsWith(boxtype_name, "yhgd5034"))
	{
		puts("[EGAMI] INI-OEM 5034\n");
	}
	else if(startsWith(boxtype_name, "yhgd2580"))
	{
		puts("[EGAMI] INI-OEM 2584\n");
	}
	/*else if(startsWith(boxtype_name, "h"))
	{
		puts("[EGAMI] Zgemma H Series\n");
	}*/
	else if(startsWith(boxtype_name, "hd"))
	{
		puts("[EGAMI] SkyLake\n");
	}
	else if(startsWith(vuboxtype_name, "solo4"))
	{
		puts("[EGAMI] Solo4K\n");
	}
	else if(startsWith(vuboxtype_name, "solo2"))
	{
		puts("[EGAMI] Solo2\n");
	}
	else if(startsWith(vuboxtype_name, "zer"))
	{
		puts("[EGAMI] Zero4K\n");
	}
	else if(startsWith(boxmodel_name, "wetek"))
	{
		puts("[EGAMI] Wetek\n");
	}
	else
	{
		puts("[EGAMI] The Evolved Image...\n");
		sync();
		reboot(RB_AUTOBOOT);
		//reboot(RB_POWER_OFF);
	}
	return 1;
}