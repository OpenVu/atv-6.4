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
	int locked;
#endif
public:
	virtual int lock();
	virtual void unlock();
	static eEGAMI *getInstance();
#ifndef SWIG
	eEGAMI();
	virtual ~eEGAMI();
#endif	
};
#endif
