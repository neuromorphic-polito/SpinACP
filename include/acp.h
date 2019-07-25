/**
 * @file acp.h
 * @author Barchi Francesco
 * @date 2017-2018
 * @brief The Application Command Protocol for SpiNNaker
 *
 * The ACP is a middle level interface for send data and commands
 * around the SpiNNaker machine. This library use the MCM format
 * for its packets, and permits to the Application Processors
 * to communicate.
 */

#ifndef __SPINN_ACP_H__
#define __SPINN_ACP_H__

#include "spin2_api.h"

//#define ACP_DEBUG
#define ACP_VERSION "19w19"

#define ACP_SDP_PORT 7


// ACP Struct
typedef struct {
  uint16_t cmd;
  uint16_t seq;
  uint16_t length; // length in Byte
  uint32_t header_lv2; // ME 16bit ME-Code, 16 ME-Offset
  uint8_t *payload;
} acp_msg_t;


// ACP Channel
typedef enum {
  ACP_CHANNEL_SELF,
  ACP_CHANNEL_CORE,
  ACP_CHANNEL_BROADCAST,
  ACP_CHANNEL_HOST
} acp_channel_t;


// Typedef
typedef uint32_t * uint32_t_p;
typedef uint16_t * uint16_t_p;
typedef uint8_t * uint8_t_p;


// ACP Callbacks
typedef void (*acp_cmd_callback_t)(acp_msg_t *acp_msg);
typedef void (*acp_me_callback_t)(uint16_t, uint8_t *, uint16_t);


// --- Init ---
void acp_init();


// --- User Commands ---
bool acp_cmd_create(
  uint16_t cmd_id, 
  acp_cmd_callback_t callback);

bool acp_cmd_delete(
  uint16_t cmd_id);


// --- Memory Entity ---
void acp_me_create(
    uint16_t me_id, 
    uint16_t length, 
    acp_me_callback_t callback_write, 
    acp_me_callback_t callback_read);

uint16_t acp_me_read(
    uint16_t me_id, 
    uint8_t *buffer, 
    uint16_t length, 
    acp_channel_t channel, 
    spin2_core_t *core, 
    bool sync);

uint16_t acp_me_update(
    uint16_t me_id, 
    uint8_t *buffer, 
    uint16_t length, 
    acp_channel_t channel, 
    spin2_core_t *core, 
    bool sync);

bool acp_me_delete(
    uint16_t me_id);

void acp_me_clear();


// --- ACP Sync ---
void acp_syn_init();

void acp_syn_wait();
void acp_ack_wait();

void acp_syn();
void acp_ack();

void acp_remote_syn(acp_channel_t channel, spin2_core_t *destination);
void acp_remote_ack(acp_channel_t channel, spin2_core_t *destination);



#endif //__SPINN_ACP_H__
