// ==========================================================================
//                                  SpinACP
// ==========================================================================
// This file is part of SpinACP.
//
// SpinACP is Free Software: you can redistribute it and/or modify it
// under the terms found in the LICENSE[.md|.rst] file distributed
// together with this file.
//
// SpinACP is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
//
// ==========================================================================
// Author: Francesco Barchi <francesco.barchi@polito.it>
// ==========================================================================
// acp.h: Main header file for SpinACP
// ==========================================================================

#ifndef __SPINN_ACP_H__
#define __SPINN_ACP_H__

#include "spin2_api.h"

#define ACP_SUCCESS 0
#define ACP_ERROR 0
#define ACP_PORT 7
#define ACP_SDP_CALLBACK_PRIORITY 0

#define ACP_SPIN2MC
//#define ACP_DEBUG
//#define ACP_TEST

// --- Enum ---
typedef enum {
  ACP_CMD_REGISTER_VAR = 0xFB,
  ACP_CMD_UNREGISTER_VAR = 0xBF,
  ACP_CMD_READ_VAR = 0xF0,
  ACP_CMD_WRITE_VAR = 0xF1,
  ACP_CMD_TOGGLE_VAR = 0xF2,
} ACP_CMD;

// --- Typedef ---
typedef struct variable variable_t;
typedef void (*var_callback)(uint16_t, uint8_t *, uint16_t);

// --- ACP Interface ---
bool acp_variable_init();
bool acp_variable_destroy();
bool acp_variable_register(uint16_t var_code, uint16_t length,
                           var_callback callback_write, var_callback callback_read);
bool acp_variable_write(uint16_t var_code, uint8_t *value, uint16_t length);
bool acp_variable_read(uint16_t var_code, uint8_t *value, uint16_t *length);
bool acp_variable_toggle(uint16_t var_code);

bool acp_variable_read_after_write(uint16_t var_code, uint8_t *value, uint16_t *length);

// --- NET Interface ---
bool acp_net_variable_write(
    uint16_t var_code, uint8_t *value, uint16_t length,
    uint16_t address, uint8_t port);

bool acp_net_variable_read(
    uint16_t var_code, uint8_t *value, uint16_t *length,
    uint16_t address, uint8_t port);

// --- SDP ---
void acp_sdp_callback(uint mailbox, uint port);

// --- MC ---
//#ifdef ACP_SPIN2MC
void acp_mc_init();
void acp_mc_callback(uint param0, uint param1);
bool cmd_net_variable_write_all(uint16_t var_code, uint8_t *value, uint16_t length);
//#endif

// --- MISC ---
#ifdef ACP_TEST
bool acp_test();
#endif

#endif //__SPINN_ACP_H__
