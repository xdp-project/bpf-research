KERNEL_VERSION := $(shell uname -r)
IDIR := /lib/modules/$(KERNEL_VERSION)/kernel/net/sched/
KDIR := /lib/modules/$(KERNEL_VERSION)/build
PWD := $(shell pwd)

default:
	@$(MAKE) -C $(KDIR) M=$(PWD) modules

install:
	install -v -m 644 sch_sample.ko $(IDIR)
	depmod "$(KERNEL_VERSION)"
	[ "$(KERNEL_VERSION)" != `uname -r` ] || modprobe sch_sample

clean:
	@$(MAKE) -C $(KDIR) M=$(PWD) clean
