# Run this script with PACKER_LOG=1 set to get verbose logs.

BASE_DIR=iso-centos6_64-minimal
BASE_OVA=$(BASE_DIR)/output-virtualbox-iso/packer-virtualbox-iso.ova

OPENVZ_DIR=ova-centos6_64-openvz
OPENVZ_OVA=$(OPENVZ_DIR)/output-virtualbox-ovf/packer-virtualbox-ovf.ova

VBGUEST_DIR=ova-centos6_64-vbadditions
VBGUEST_OVA=$(VBGUEST_DIR)/output-virtualbox-ovf/packer-virtualbox-ovf.ova

VAGRANTBOX_DIR=ova-vagrantbox
VAGRANTBOX_BOX=./centos6_64_vz.box

.PHONY: all clean
all: $(VAGRANTBOX_BOX)

$(BASE_OVA): $(BASE_DIR)/packer-config.json
	cd $(BASE_DIR); packer build packer-config.json

$(OPENVZ_OVA): $(OPENVZ_DIR)/packer-config.json $(BASE_OVA)
	ln -f $(BASE_OVA) $(OPENVZ_DIR)/source.ova
	cd $(OPENVZ_DIR); packer build packer-config.json
	mv $(OPENVZ_DIR)/output-virtualbox-ovf/* $(OPENVZ_OVA)

$(VBGUEST_OVA): $(VBGUEST_DIR)/packer-config.json $(OPENVZ_OVA)
	ln -f $(OPENVZ_OVA) $(VBGUEST_DIR)/source.ova
	cd $(VBGUEST_DIR); packer build packer-config.json
	mv $(VBGUEST_DIR)/output-virtualbox-ovf/* $(VBGUEST_OVA)

$(VAGRANTBOX_BOX): $(VAGRANTBOX_DIR)/packer-config.json $(VBGUEST_OVA)
	ln -f $(VBGUEST_OVA) $(VAGRANTBOX_DIR)/source.ova
	cd $(VAGRANTBOX_DIR); packer build packer-config.json
	mv $(VAGRANTBOX_DIR)/*.box $(VAGRANTBOX_BOX)