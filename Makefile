# If SPINN_DIRS is not defined, this is an error!
ifndef SPINN_DIRS
    $(error SPINN_DIRS is not set.  Please define SPINN_DIRS (possibly by running "source setup" in the spinnaker tools folder))
endif

SPINN_ACP_BUILD = build
include $(SPINN_DIRS)/make/Makefile.common

#SPINN_COMMON_DEBUG := PRODUCTION_CODE

# Include our own include directory
CFLAGS += -I include $(OTIME) #-D$(SPINN_COMMON_DEBUG)

# Objects
OBJS = acp.o acp_syn.o acp_exec.o acp_mc.o acp_me.o acp_sdp.o
BUILD_OBJS = $(OBJS:%.o=$(SPINN_ACP_BUILD)/%.o)

# Headers
HEADERS = acp.h
INSTALL_HEADERS = $(HEADERS:%.h=$(SPINN_INC_DIR)/%.h)

# Build rules (default)
$(SPINN_ACP_BUILD)/libspinn_acp.a: $(BUILD_OBJS)
	$(RM) $@
	$(AR) $@ $(BUILD_OBJS)

$(SPINN_ACP_BUILD)/%.o: src/%.c $(SPINN_ACP_BUILD)
	$(CC) $(CFLAGS) -o $@ $<

$(SPINN_ACP_BUILD):
	$(MKDIR) $@

# Installing rules
install: $(SPINN_LIB_DIR)/libspinn_acp.a $(INSTALL_HEADERS)

$(SPINN_LIB_DIR)/libspinn_acp.a: $(SPINN_ACP_BUILD)/libspinn_acp.a
	$(CP) $< $@

$(SPINN_INC_DIR)/%.h: include/%.h
	$(CP) $< $@

clean:
	$(RM) $(SPINN_ACP_BUILD)/libspinn_acp.a $(BUILD_OBJS)
