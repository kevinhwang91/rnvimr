ifeq ($(XDG_CONFIG_HOME),)
RANGER_CONFIG ?= $(HOME)/.config/ranger
endif

RANGER_CONFIG ?= $(XDG_CONFIG_HOME)/ranger
RANGER_PLUGINS ?= $(RANGER_CONFIG)/plugins
RNVIMR_CONFIG ?= ranger
RNVIMR_PLUGINS ?= $(RNVIMR_CONFIG)/plugins
RNVIMR_LIB := lib

all: sync

install: clean
	mkdir -p $(RNVIMR_PLUGINS)
	cp $(RNVIMR_LIB)/[^_]*.py $(RNVIMR_PLUGINS)

sync: install
	mkdir -p $(RNVIMR_PLUGINS)
	-cp $(RANGER_PLUGINS)/[^_]*.py $(RNVIMR_PLUGINS)
	-cp $(RANGER_CONFIG)/[^_]*.conf $(RNVIMR_CONFIG)
	-cp $(RANGER_CONFIG)/[^_]*.py $(RNVIMR_CONFIG)
	-cp $(RANGER_CONFIG)/[^_]*.sh $(RNVIMR_CONFIG)

clean:
	$(RM) -r $(RNVIMR_CONFIG)

.PHONY: all install sync clean
