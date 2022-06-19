#ifndef __egami_h
#define __egami_h

#include <lib/base/object.h>
#include <lib/python/connections.h>

class eEGAMI 
{
#ifdef SWIG
	eEGAMI();
	~eEGAMI();
#else
protected:
	static eEGAMI *instance;
#endif
public:
	bool is4digits();
	int checkkernel();
	static eEGAMI *getInstance();
#ifndef SWIG
	eEGAMI();
	~eEGAMI();
#endif	
};
#endif
