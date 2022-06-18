#ifndef __egami_h
#define __egami_h

#include <lib/base/object.h>
#include <lib/python/connections.h>

class eEGAMI 
{
	static eEGAMI *instance;

#ifdef SWIG
	eEGAMI();
	~eEGAMI();
#endif
public:
#ifndef SWIG
	eEGAMI();
	~eEGAMI();
#endif	
	//eEGAMI();
	static eEGAMI *getInstance();
	bool fileExists(const char *filename);
	bool endsWith(char* base, char* str);
	bool startsWith(char* base, char* str);
	char* ReadProcEntry(char *filename);
	bool checkkernel();
};

#endif