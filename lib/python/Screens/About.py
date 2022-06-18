from Screen import Screen
from skin import isVTISkin
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Harddisk import Harddisk, harddiskmanager
from Components.NimManager import nimmanager
from Components.About import about
from Components.ScrollLabel import ScrollLabel
from Components.Console import Console
from Components.SystemInfo import SystemInfo
from Components.config import config
from enigma import eTimer, getEnigmaVersionString, getDesktop
from boxbranding import getBoxType, getMachineBuild, getMachineBrand, getMachineName, getImageVersion, getImageBuild, getDriverDate

from Components.Pixmap import MultiPixmap
from Components.Network import iNetwork

from Tools.StbHardware import getFPVersion
from Tools.Multiboot import GetCurrentImage, GetCurrentImageMode

from os import path, popen
from re import search

import time


def parse_ipv4(ip):
	ret = ""
	idx = 0
	if ip is not None:
		for x in ip:
			if idx == 0:
				ret += str(x)
			else:
				ret += "." + str(x)
			idx += 1
	return ret


def parseFile(filename):
	ret = "N/A"
	try:
		f = open(filename, "rb")
		ret = f.read().strip()
		f.close()
	except IOError:
		print "[ERROR] failed to open file %s" % filename
	return ret


def parseLines(filename):
	ret = ["N/A"]
	try:
		f = open(filename, "rb")
		ret = f.readlines()
		f.close()
	except IOError:
		print "[ERROR] failed to open file %s" % filename
	return ret


def MyDateConverter(StringDate):
	## StringDate must be a string "YYYY-MM-DD" or "YYYYMMDD"
	try:
		if len(StringDate) == 8:
			year = StringDate[0:4]
			month = StringDate[4:6]
			day = StringDate[6:8]
			StringDate = ' '.join((year, month, day))
		else:
			StringDate = StringDate.replace("-", " ")
		StringDate = time.strftime(config.usage.date.full.value, time.strptime(StringDate, "%Y %m %d"))
		return StringDate
	except:
		return _("unknown")


def getAboutText():
	AboutText = ""
	AboutText += _("Model:\t\t%s %s\n") % (getMachineBrand(), getMachineName())
	AboutText += _("OEM Model:\t\t%s\n") % getMachineBuild()

	bootloader = ""
	if path.exists('/sys/firmware/devicetree/base/bolt/tag'):
		f = open('/sys/firmware/devicetree/base/bolt/tag', 'r')
		bootloader = f.readline().replace('\x00', '').replace('\n', '')
		f.close()
		AboutText += _("Bootloader:\t\t%s\n") % (bootloader)

	if path.exists('/proc/stb/info/chipset'):
		AboutText += _("Chipset:\t\t%s") % about.getChipSetString() + "\n"

	AboutText += _("CPU:\t\t%s  (%s)  %s cores") % (about.getCPUString(), about.getCPUSpeedString(), about.getCpuCoresString()) + "\n"

	imagestarted = ""
	bootname = ''
	if path.exists('/boot/bootname'):
		f = open('/boot/bootname', 'r')
		bootname = f.readline().split('=')[1]
		f.close()
	if SystemInfo["canMultiBoot"]:
		slot = image = GetCurrentImage()
		bootmode = ""
		part = _("eMMC slot %s") % slot
		if SystemInfo["canMode12"]:
			bootmode = _(" bootmode = %s") % GetCurrentImageMode()
		if SystemInfo["HasHiSi"] and "sda" in SystemInfo["canMultiBoot"][slot]['device']:
			if slot > 4:
				image -= 4
			else:
				image -= 1
			part = "SDcard slot %s (%s) " % (image, SystemInfo["canMultiBoot"][slot]['device'])
		AboutText += _("Selected Image:\t\t%s") % _("STARTUP_") + str(slot) + "  (" + part + bootmode + ")\n"

	AboutText += _("Version / Build:\t\t%s  (%s)") % (getImageVersion(), MyDateConverter(getImageBuild())) + "\n"
	AboutText += _("Kernel:\t\t%s") % about.getKernelVersionString() + "\n"
	AboutText += _("Drivers:\t\t%s") % MyDateConverter(getDriverDate()) + "\n"

	skinWidth = getDesktop(0).size().width()
	skinHeight = getDesktop(0).size().height()

	AboutText += _("Skin:\t\t%s") % config.skin.primary_skin.value.split("/")[0] + _("  (%s x %s)") % (skinWidth, skinHeight) + "\n"

	AboutText += _("GStreamer:\t\t%s") % about.getGStreamerVersionString() + "\n"
	AboutText += _("Python:\t\t%s") % about.getPythonVersionString() + "\n"

	MyFlashDate = about.getFlashDateString()
	if MyFlashDate != _("unknown"):
		AboutText += _("Installed:\t\t%s") % MyDateConverter(MyFlashDate) + "\n"

	AboutText += _("Last E2 update:\t\t%s") % MyDateConverter(getEnigmaVersionString()) + "\n"

	fp_version = getFPVersion()
	if fp_version is None:
		fp_version = ""
	elif fp_version != 0:
		fp_version = _("Frontprocessor version:\t%s") % fp_version
		AboutText += fp_version + "\n"

	tempinfo = ""
	if path.exists('/proc/stb/sensors/temp0/value'):
		f = open('/proc/stb/sensors/temp0/value', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/fp/temp_sensor'):
		f = open('/proc/stb/fp/temp_sensor', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/sensors/temp/value'):
		f = open('/proc/stb/sensors/temp/value', 'r')
		tempinfo = f.read()
		f.close()
	if tempinfo and int(tempinfo.replace('\n', '')) > 0:
		mark = str('\xc2\xb0')
		AboutText += _("System temperature:\t%s") % tempinfo.replace('\n', '').replace(' ', '') + mark + "C\n"

	tempinfo = ""
	if path.exists('/proc/stb/fp/temp_sensor_avs'):
		f = open('/proc/stb/fp/temp_sensor_avs', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/proc/stb/power/avs'):
		f = open('/proc/stb/power/avs', 'r')
		tempinfo = f.read()
		f.close()
	elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
		try:
			f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
			tempinfo = f.read()
			tempinfo = tempinfo[:-4]
			f.close()
		except:
			tempinfo = ""
	elif path.exists('/proc/hisi/msp/pm_cpu'):
		try:
			for line in open('/proc/hisi/msp/pm_cpu').readlines():
				line = [x.strip() for x in line.strip().split(":")]
				if line[0] in ("Tsensor"):
					temp = line[1].split("=")
					temp = line[1].split(" ")
					tempinfo = temp[2]
					if getMachineBuild() in ('u41', 'u42', 'u43', 'u45'):
						tempinfo = str(int(tempinfo) - 15)
		except:
			tempinfo = ""
	if tempinfo and int(tempinfo.replace('\n', '')) > 0:
		mark = str('\xc2\xb0')
		AboutText += _("Processor temperature:\t%s") % tempinfo.replace('\n', '').replace(' ', '') + mark + "C\n"
	AboutLcdText = AboutText.replace('\t', ' ')

	return AboutText, AboutLcdText


class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Image Information"))
		self.skinName = ["AboutOE", "About"]
		self.populate()

		self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Translations"))
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"log": self.showAboutReleaseNotes,
				"up": self.pageUp,
				"down": self.pageDown,
				"red": self.close,
				"green": self.showTranslationInfo,
				"0": self.showID,
			})

	def populate(self):
		if isVTISkin:
			self["EnigmaVersion"] = StaticText(_("Version") + ": " + about.getEnigmaVersionString())
			self["ImageVersion"] = StaticText(_("Image") + ": " + about.getImageVersionString())

			self["TunerHeader"] = StaticText(_("Detected NIMs:"))

			fp_version = getFPVersion()
			if fp_version is None:
				fp_version = ""
			else:
				fp_version = _("Frontprocessor version: %s") % str(fp_version)

			self["FPVersion"] = StaticText(fp_version)

			nims = nimmanager.nimList()
			self.tuner_list = []
			if len(nims) <= 4:
				for count in (0, 1, 2, 3, 4, 5, 6, 7):
					if count < len(nims):
						self["Tuner" + str(count)] = StaticText(nims[count])
						self.tuner_list.append((nims[count] + "\n"))
					else:
						self["Tuner" + str(count)] = StaticText("")
			else:
				desc_list = []
				count = 0
				cur_idx = -1
				while count < len(nims):
					data = nims[count].split(":")
					idx = data[0].strip('Tuner').strip()
					desc = data[1].strip()
					if desc_list and desc_list[cur_idx]['desc'] == desc:
						desc_list[cur_idx]['end'] = idx
					else:
						desc_list.append({'desc': desc, 'start': idx, 'end': idx})
						cur_idx += 1
					count += 1

				for count in (0, 1, 2, 3, 4, 5, 6, 7):
					if count < len(desc_list):
						if desc_list[count]['start'] == desc_list[count]['end']:
							text = "Tuner %s: %s" % (desc_list[count]['start'], desc_list[count]['desc'])
						else:
							text = "Tuner %s-%s: %s" % (desc_list[count]['start'], desc_list[count]['end'], desc_list[count]['desc'])
					else:
						text = ""

					self["Tuner" + str(count)] = StaticText(text)
					if text != "":
						self.tuner_list.append(text + "\n")

			self["HDDHeader"] = StaticText(_("Detected HDD:"))
			hddlist = harddiskmanager.HDDList()
			hdd = hddlist and hddlist[0][1] or None
			if hdd is not None and hdd.model() != "":
				self["hddA"] = StaticText(_("%s\n(%s, %d MB free)") % (hdd.model(), hdd.capacity(), hdd.free()))
			else:
				self["hddA"] = StaticText(_("none"))

			self.enigma2_version = _("Version") + ": " + about.getEnigmaVersionString()
			self.image_version = _("Image") + ": " + about.getImageVersionString()
			cpu_info = parseLines("/proc/cpuinfo")
			cpu_name = "N/A"
			for line in cpu_info:
				if line.find('model') != -1:
					cpu_name = line.split(':')
					if len(cpu_name) >= 2:
						cpu_name = cpu_name[1].strip()
					break

			self.cpu = _("CPU") + ": " + cpu_name
			self.chipset = _("Chipset") + ": " + parseFile("/proc/stb/info/chipset")
			self.tuner_header = _("Detected NIMs:")
			self.hdd_header = _("Detected HDD:")
			self.hdd_list = []
			if len(hddlist):
				for hddX in hddlist:
					hdd = hddX[1]
					if hdd.model() != "":
						self.hdd_list.append((hdd.model() + "\n   %.2f GB - %.2f GB" % (hdd.diskSize() / 1000.0, hdd.free() / 1000.0) + " " + _("free") + "\n\n"))

			ifaces = iNetwork.getConfiguredAdapters()
			iface_list = []
			for iface in ifaces:
				iface_list.append((_("Interface") + " : " + iNetwork.getAdapterName(iface) + " (" + iNetwork.getFriendlyAdapterName(iface) + ")\n"))
				iface_list.append((_("IP") + " : " + parse_ipv4(iNetwork.getAdapterAttribute(iface, "ip")) + "\n"))
				iface_list.append((_("Netmask") + " : " + parse_ipv4(iNetwork.getAdapterAttribute(iface, "netmask")) + "\n"))
				iface_list.append((_("Gateway") + " : " + parse_ipv4(iNetwork.getAdapterAttribute(iface, "gateway")) + "\n"))
				if iNetwork.getAdapterAttribute(iface, "dhcp"):
					iface_list.append((_("DHCP") + " : " + _("Yes") + "\n"))
				else:
					iface_list.append((_("DHCP") + " : " + _("No") + "\n"))
				iface_list.append((_("MAC") + " : " + iNetwork.getAdapterAttribute(iface, "mac") + "\n"))
				iface_list.append(("\n"))

			my_txt = self.enigma2_version + "\n"
			my_txt += self.image_version + "\n"
			my_txt += "\n"
			my_txt += self.cpu + "\n"
			my_txt += self.chipset + "\n"
			my_txt += "\n"
			my_txt += self.tuner_header + "\n"
			for x in self.tuner_list:
				my_txt += "   " + x
			my_txt += "\n"
			my_txt += _("Network") + ":\n"
			for x in iface_list:
				my_txt += "   " + x
			my_txt += self.hdd_header + "\n"
			for x in self.hdd_list:
				my_txt += "   " + x
			my_txt += "\n"

			self["FullAbout"] = ScrollLabel(my_txt)
		else:
			self["lab1"] = StaticText(_("openATV"))
			self["lab2"] = StaticText(_("By openATV Image Team"))
			self["lab3"] = StaticText(_("Support at") + " www.opena.tv")
			model = None
			AboutText = getAboutText()[0]
			self["AboutScrollLabel"] = ScrollLabel(AboutText)

	def populate_vti(self):
		pass

	def showID(self):
		if SystemInfo["HaveID"]:
			try:
				f = open("/etc/.id")
				id = f.read()[:-1].split('=')
				f.close()
				from Screens.MessageBox import MessageBox
				self.session.open(MessageBox, id[1], type=MessageBox.TYPE_INFO)
			except:
				pass

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

	def showAboutReleaseNotes(self):
		self.session.open(ViewGitLog)

	def createSummary(self):
		return AboutSummary

	def pageUp(self):
		if isVTISkin:
			self["FullAbout"].pageUp()
		else:
			self["AboutScrollLabel"].pageUp()

	def pageDown(self):
		if isVTISkin:
			self["FullAbout"].pageDown()
		else:
			self["AboutScrollLabel"].pageDown()


class Devices(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Device Information"))
		self["TunerHeader"] = StaticText(_("Detected NIMs:"))
		self["HDDHeader"] = StaticText(_("Detected Devices:"))
		self["MountsHeader"] = StaticText(_("Network Servers:"))
		self["nims"] = StaticText()
		self["hdd"] = StaticText()
		self["mounts"] = StaticText()
		self["allinonedevices"] = ScrollLabel()
		self.list = []
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.populate2)
		self["actions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
			{
				"up": self["allinonedevices"].pageUp,
				"down": self["allinonedevices"].pageDown,
				"cancel": self.close,
				"ok": self.close,
			})
		self.onLayoutFinish.append(self.populate)

	def populate(self):
		self.mountinfo = ''
		self["actions"].setEnabled(False)
		scanning = _("Wait please while scanning for devices...")
		self["nims"].setText(scanning)
		self["hdd"].setText(scanning)
		self['mounts'].setText(scanning)
		self['allinonedevices'].setText(scanning)
		self.activityTimer.start(1)

	def populate2(self):
		self.activityTimer.stop()
		self.Console = Console()
		niminfo = ""
		nims = nimmanager.nimList()
		for count in range(len(nims)):
			if niminfo:
				niminfo += "\n"
			niminfo += nims[count]
		self["nims"].setText(niminfo)

		self.list = []
		list2 = []
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
			if not search('sd[a-z][1-9]', device):
				continue
			if device in list2:
				continue

			mount = '/dev/' + device
			f = open('/proc/mounts', 'r')
			for line in f.readlines():
				if device in line:
					parts = line.strip().split()
					mount = str(parts[1])
					break
			f.close()

			if not mount.startswith('/dev/'):
				size = Harddisk(device).diskSize()
				free = Harddisk(device).free()

				if ((float(size) / 1024) / 1024) >= 1:
					sizeline = _("Size: ") + str(round(((float(size) / 1024) / 1024), 2)) + " " + _("TB")
				elif (size / 1024) >= 1:
					sizeline = _("Size: ") + str(round((float(size) / 1024), 2)) + " " + _("GB")
				elif size >= 1:
					sizeline = _("Size: ") + str(size) + " " + _("MB")
				else:
					sizeline = _("Size: ") + _("unavailable")

				if ((float(free) / 1024) / 1024) >= 1:
					freeline = _("Free: ") + str(round(((float(free) / 1024) / 1024), 2)) + " " + _("TB")
				elif (free / 1024) >= 1:
					freeline = _("Free: ") + str(round((float(free) / 1024), 2)) + " " + _("GB")
				elif free >= 1:
					freeline = _("Free: ") + str(free) + " " + _("MB")
				else:
					freeline = _("Free: ") + _("full")
				self.list.append(mount + '\t' + sizeline + ' \t' + freeline)
			else:
				self.list.append(mount + '\t' + _('Not mounted'))

			list2.append(device)
		self.list = '\n'.join(self.list)
		self["hdd"].setText(self.list)
		self["allinonedevices"].setText(
			self["TunerHeader"].getText() + "\n\n" +
			self["nims"].getText() + "\n\n" +
			self["HDDHeader"].getText() + "\n\n" +
			self["hdd"].getText() + "\n\n"
			)

		self.Console.ePopen("df -mh | grep -v '^Filesystem'", self.Stage1Complete)

	def Stage1Complete(self, result, retval, extra_args=None):
		result = result.replace('\n                        ', ' ').split('\n')
		self.mountinfo = ""
		for line in result:
			self.parts = line.split()
			if line and self.parts[0] and (self.parts[0].startswith('192') or self.parts[0].startswith('//192')):
				line = line.split()
				try:
					ipaddress = line[0]
				except:
					ipaddress = ""
				try:
					mounttotal = line[1]
				except:
					mounttotal = ""
				try:
					mountfree = line[3]
				except:
					mountfree = ""
				if self.mountinfo:
					self.mountinfo += "\n"
				self.mountinfo += "%s (%sB, %sB %s)" % (ipaddress, mounttotal, mountfree, _("free"))

		if self.mountinfo:
			self["mounts"].setText(self.mountinfo)
		else:
			self["mounts"].setText(_('none'))

		self["allinonedevices"].setText(
			self["allinonedevices"].getText() +
			self["MountsHeader"].getText() + "\n\n" +
			self["mounts"].getText()
			)
		self["actions"].setEnabled(True)

	def createSummary(self):
		return AboutSummary


class SystemMemoryInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Memory Information"))
		self.skinName = ["SystemMemoryInfo", "About"]
		self["AboutScrollLabel"] = ScrollLabel()
		self["lab1"] = StaticText()
		self["lab2"] = StaticText()

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown,
			})

		out_lines = file("/proc/meminfo").readlines()
		self.AboutText = _("RAM") + '\n\n'
		RamTotal = "-"
		RamFree = "-"
		for lidx in range(len(out_lines) - 1):
			tstLine = out_lines[lidx].split()
			if "MemTotal:" in tstLine:
				MemTotal = out_lines[lidx].split()
				self.AboutText += '{:<35}'.format(_("Total Memory:")) + "\t" + MemTotal[1] + "\n"
			if "MemFree:" in tstLine:
				MemFree = out_lines[lidx].split()
				self.AboutText += '{:<35}'.format(_("Free Memory:")) + "\t" + MemFree[1] + "\n"
			if "Buffers:" in tstLine:
				Buffers = out_lines[lidx].split()
				self.AboutText += '{:<35}'.format(_("Buffers:")) + "\t" + Buffers[1] + "\n"
			if "Cached:" in tstLine:
				Cached = out_lines[lidx].split()
				self.AboutText += '{:<35}'.format(_("Cached:")) + "\t" + Cached[1] + "\n"
			if "SwapTotal:" in tstLine:
				SwapTotal = out_lines[lidx].split()
				self.AboutText += '{:<35}'.format(_("Total Swap:")) + "\t" + SwapTotal[1] + "\n"
			if "SwapFree:" in tstLine:
				SwapFree = out_lines[lidx].split()
				self.AboutText += '{:<35}'.format(_("Free Swap:")) + "\t" + SwapFree[1] + "\n\n"

		self["actions"].setEnabled(False)
		self.Console = Console()
		self.Console.ePopen("df -mh / | grep -v '^Filesystem'", self.Stage1Complete)

	def MySize(self, RamText):
		RamText_End = RamText[len(RamText) - 1]
		RamText_End2 = RamText_End
		if RamText_End == "G":
			RamText_End = _("GB")
		elif RamText_End == "M":
			RamText_End = _("MB")
		elif RamText_End == "K":
			RamText_End = _("KB")
		if RamText_End != RamText_End2:
			RamText = RamText[0:len(RamText) - 1] + " " + RamText_End
		return RamText

	def Stage1Complete(self, result, retval, extra_args=None):
		flash = str(result).replace('\n', '')
		flash = flash.split()
		RamTotal = self.MySize(flash[1])
		RamFree = self.MySize(flash[3])

		self.AboutText += _("FLASH") + '\n\n'
		self.AboutText += _("Total:") + "\t" + RamTotal + "\n"
		self.AboutText += _("Free:") + "\t" + RamFree + "\n\n"

		self["AboutScrollLabel"].setText(self.AboutText)
		self["actions"].setEnabled(True)

	def createSummary(self):
		return AboutSummary


class SystemNetworkInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Network Information"))
		self.skinName = ["SystemNetworkInfo", "WlanStatus"]
		self["LabelBSSID"] = StaticText()
		self["LabelESSID"] = StaticText()
		self["LabelQuality"] = StaticText()
		self["LabelSignal"] = StaticText()
		self["LabelBitrate"] = StaticText()
		self["LabelEnc"] = StaticText()
		self["BSSID"] = StaticText()
		self["ESSID"] = StaticText()
		self["quality"] = StaticText()
		self["signal"] = StaticText()
		self["bitrate"] = StaticText()
		self["enc"] = StaticText()

		self["IFtext"] = StaticText()
		self["IF"] = StaticText()
		self["Statustext"] = StaticText()
		self["statuspic"] = MultiPixmap()
		self["statuspic"].setPixmapNum(1)
		self["statuspic"].show()

		self.iface = None
		self.createscreen()
		self.iStatus = None

		if iNetwork.isWirelessInterface(self.iface):
			try:
				from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
				self.iStatus = iStatus
			except:
				pass
			self.resetList()
			self.onClose.append(self.cleanup)
		self.updateStatusbar()

		self["key_red"] = StaticText(_("Close"))

		self["actions"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			})

	def createscreen(self):
		def netspeed():
			netspeed = ""
			for line in popen('ethtool eth0 |grep Speed', 'r'):
				line = line.strip().split(":")
				line = line[1].replace(' ', '')
				netspeed += line
				return str(netspeed)

		def netspeed_eth1():
			netspeed = ""
			for line in popen('ethtool eth1 |grep Speed', 'r'):
				line = line.strip().split(":")
				line = line[1].replace(' ', '')
				netspeed += line
				return str(netspeed)

		self.AboutText = ""
		self.iface = "eth0"
		eth0 = about.getIfConfig('eth0')
		if 'addr' in eth0:
			if 'ifname' in eth0:
				self.AboutText += '{:<35}'.format(_('Interface:')) + "\t" + " /dev/" + eth0['ifname'] + "\n"
			self.AboutText += '{:<35}'.format(_("IP:")) + "\t" + eth0['addr'] + "\n"
			if 'netmask' in eth0:
				self.AboutText += '{:<35}'.format(_("Netmask:")) + "\t" + eth0['netmask'] + "\n"
			if 'hwaddr' in eth0:
				self.AboutText += '{:<35}'.format(_("MAC:")) + "\t" + eth0['hwaddr'] + "\n"
			self.AboutText += '{:<35}'.format(_("Network Speed:")) + "\t" + netspeed() + "\n"
			self.iface = 'eth0'

		eth1 = about.getIfConfig('eth1')
		if 'addr' in eth1:
			if 'ifname' in eth1:
				self.AboutText += '{:<35}'.format(_('Interface:')) + "\t" + " /dev/" + eth1['ifname'] + "\n"
			self.AboutText += '{:<35}'.format(_("IP:")) + "\t" + eth1['addr'] + "\n"
			if 'netmask' in eth1:
				self.AboutText += '{:<35}'.format(_("Netmask:")) + "\t" + eth1['netmask'] + "\n"
			if 'hwaddr' in eth1:
				self.AboutText += '{:<35}'.format(_("MAC:")) + "\t" + eth1['hwaddr'] + "\n"
			self.AboutText += '{:<35}'.format(_("Network Speed:")) + "\t" + netspeed_eth1() + "\n"
			self.iface = 'eth1'

		ra0 = about.getIfConfig('ra0')
		if 'addr' in ra0:
			if 'ifname' in ra0:
				self.AboutText += '{:<35}'.format(_('Interface:')) + "\t" + " /dev/" + ra0['ifname'] + "\n"
			self.AboutText += '{:<35}'.format(_("IP:")) + "\t" + ra0['addr'] + "\n"
			if 'netmask' in ra0:
				self.AboutText += '{:<35}'.format(_("Netmask:")) + "\t" + ra0['netmask'] + "\n"
			if 'hwaddr' in ra0:
				self.AboutText += '{:<35}'.format(_("MAC:")) + "\t" + ra0['hwaddr'] + "\n"
			self.iface = 'ra0'

		wlan0 = about.getIfConfig('wlan0')
		if 'addr' in wlan0:
			if 'ifname' in wlan0:
				self.AboutText += '{:<35}'.format(_('Interface:')) + "\t" + " /dev/" + wlan0['ifname'] + "\n"
			self.AboutText += '{:<35}'.format(_("IP:")) + "\t" + wlan0['addr'] + "\n"
			if 'netmask' in wlan0:
				self.AboutText += '{:<35}'.format(_("Netmask:")) + "\t" + wlan0['netmask'] + "\n"
			if 'hwaddr' in wlan0:
				self.AboutText += '{:<35}'.format(_("MAC:")) + "\t" + wlan0['hwaddr'] + "\n"
			self.iface = 'wlan0'

		wlan1 = about.getIfConfig('wlan1')
		if 'addr' in wlan1:
			if 'ifname' in wlan1:
				self.AboutText += '{:<35}'.format(_('Interface:')) + "\t" + " /dev/" + wlan1['ifname'] + "\n"
			self.AboutText += '{:<35}'.format(_("IP:")) + "\t" + wlan1['addr'] + "\n"
			if 'netmask' in wlan1:
				self.AboutText += '{:<35}'.format(_("Netmask:")) + "\t" + wlan1['netmask'] + "\n"
			if 'hwaddr' in wlan1:
				self.AboutText += '{:<35}'.format(_("MAC:")) + "\t" + wlan1['hwaddr'] + "\n"
			self.iface = 'wlan1'

		rx_bytes, tx_bytes = about.getIfTransferredData(self.iface)
		self.AboutText += "\n" + '{:<35}'.format(_("Bytes received:")) + "\t" + rx_bytes + "\n"
		self.AboutText += '{:<35}'.format(_("Bytes sent:")) + "\t" + tx_bytes + "\n"

		hostname = file('/proc/sys/kernel/hostname').read()
		self.AboutText += "\n" + '{:<35}'.format(_("Hostname:")) + "\t" + hostname + "\n"
		self["AboutScrollLabel"] = ScrollLabel(self.AboutText)

	def cleanup(self):
		if self.iStatus:
			self.iStatus.stopWlanConsole()

	def resetList(self):
		if self.iStatus:
			self.iStatus.getDataForInterface(self.iface, self.getInfoCB)

	def getInfoCB(self, data, status):
		self.LinkState = None
		if data is not None:
			if data is True:
				if status is not None:
					if self.iface == 'wlan0' or self.iface == 'wlan1' or self.iface == 'ra0':
						if status[self.iface]["essid"] == "off":
							essid = _("No Connection")
						else:
							essid = str(status[self.iface]["essid"])
						if status[self.iface]["accesspoint"] == "Not-Associated":
							accesspoint = _("Not-Associated")
							essid = _("No Connection")
						else:
							accesspoint = str(status[self.iface]["accesspoint"])
						if "BSSID" in self:
							self.AboutText += _('Accesspoint:') + '\t' + accesspoint + '\n'
						if "ESSID" in self:
							self.AboutText += _('SSID:') + '\t' + essid + '\n'

						quality = str(status[self.iface]["quality"])
						if "quality" in self:
							self.AboutText += _('Link Quality:') + '\t' + quality + '\n'

						if status[self.iface]["bitrate"] == '0':
							bitrate = _("Unsupported")
						else:
							bitrate = str(status[self.iface]["bitrate"]) + " Mb/s"
						if "bitrate" in self:
							self.AboutText += _('Bitrate:') + '\t' + bitrate + '\n'

						signal = str(status[self.iface]["signal"])
						if "signal" in self:
							self.AboutText += _('Signal Strength:') + '\t' + signal + '\n'

						if status[self.iface]["encryption"] == "off":
							if accesspoint == "Not-Associated":
								encryption = _("Disabled")
							else:
								encryption = _("Unsupported")
						else:
							encryption = _("Enabled")
						if "enc" in self:
							self.AboutText += _('Encryption:') + '\t' + encryption + '\n'

						if status[self.iface]["essid"] == "off" or status[self.iface]["accesspoint"] == "Not-Associated" or status[self.iface]["accesspoint"] is False:
							self.LinkState = False
							self["statuspic"].setPixmapNum(1)
							self["statuspic"].show()
						else:
							self.LinkState = True
							iNetwork.checkNetworkState(self.checkNetworkCB)
						self["AboutScrollLabel"].setText(self.AboutText)

	def exit(self):
		self.close(True)

	def updateStatusbar(self):
		self["IFtext"].setText(_("Network:"))
		self["IF"].setText(iNetwork.getFriendlyAdapterName(self.iface))
		self["Statustext"].setText(_("Link:"))
		if iNetwork.isWirelessInterface(self.iface):
			try:
				self.iStatus.getDataForInterface(self.iface, self.getInfoCB)
			except:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		else:
			iNetwork.getLinkState(self.iface, self.dataAvail)

	def dataAvail(self, data):
		self.LinkState = None
		for line in data.splitlines():
			line = line.strip()
			if 'Link detected:' in line:
				if "yes" in line:
					self.LinkState = True
				else:
					self.LinkState = False
		if self.LinkState:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()

	def checkNetworkCB(self, data):
		try:
			if iNetwork.getAdapterAttribute(self.iface, "up") is True:
				if self.LinkState is True:
					if data <= 2:
						self["statuspic"].setPixmapNum(0)
					else:
						self["statuspic"].setPixmapNum(1)
					self["statuspic"].show()
				else:
					self["statuspic"].setPixmapNum(1)
					self["statuspic"].show()
			else:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		except:
			pass

	def createSummary(self):
		return AboutSummary


class AboutSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self["selected"] = StaticText("openATV:" + getImageVersion())

		AboutText = getAboutText()[1]

		self["AboutText"] = StaticText(AboutText)


class ViewGitLog(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.skinName = "SoftwareUpdateChanges"
		self.setTitle(_("OE Changes"))
		self.logtype = 'oe'
		self["text"] = ScrollLabel()
		self['title_summary'] = StaticText()
		self['text_summary'] = StaticText()
		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("OK"))
		self["key_yellow"] = Button(_("Show E2 Log"))
		self["myactions"] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'],
		{
			'cancel': self.closeRecursive,
			'green': self.closeRecursive,
			"red": self.closeRecursive,
			"yellow": self.changelogtype,
			"left": self.pageUp,
			"right": self.pageDown,
			"down": self.pageDown,
			"up": self.pageUp
		}, -1)
		self.onLayoutFinish.append(self.getlog)

	def changelogtype(self):
		if self.logtype == 'e2':
			self["key_yellow"].setText(_("Show E2 Log"))
			self.setTitle(_("OE Changes"))
			self.logtype = 'oe'
		else:
			self["key_yellow"].setText(_("Show OE Log"))
			self.setTitle(_("Enigma2 Changes"))
			self.logtype = 'e2'
		self.getlog()

	def pageUp(self):
		self["text"].pageUp()

	def pageDown(self):
		self["text"].pageDown()

	def getlog(self):
		fd = open('/etc/' + self.logtype + '-git.log', 'r')
		releasenotes = fd.read()
		fd.close()
		releasenotes = releasenotes.replace('\nopenatv: build', "\n\nopenatv: build")
		self["text"].setText(releasenotes)
		summarytext = releasenotes
		try:
			if self.logtype == 'e2':
				self['title_summary'].setText(_("E2 Log"))
				self['text_summary'].setText(_("Enigma2 Changes"))
			else:
				self['title_summary'].setText(_("OE Log"))
				self['text_summary'].setText(_("OE Changes"))
		except:
			self['title_summary'].setText("")
			self['text_summary'].setText("")

	def unattendedupdate(self):
		self.close((_("Unattended upgrade without GUI and reboot system"), "cold"))

	def closeRecursive(self):
		self.close((_("Cancel"), ""))


class TranslationInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Translation Information"))
		# don't remove the string out of the _(), or it can't be "translated" anymore.

		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == "TRANSLATOR_INFO":
			info = ""

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value
		print infomap

		self["key_red"] = Button(_("Cancel"))
		self["TranslationInfo"] = StaticText(info)

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["TranslatorName"] = StaticText(translator_name)

		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			})
