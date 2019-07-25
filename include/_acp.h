#ifndef __SPINN_ACP_PRIVATE_H__
#define __SPINN_ACP_PRIVATE_H__

#include "acp.h"

#ifdef ACP_DEBUG
#define debug_printf(...) \
  do { io_printf(IO_BUF, __VA_ARGS__); } while (0)
#else
#define debug_printf(...) \
  do { } while (0)
#endif

#define error_printf(...) \
  do { io_printf(IO_BUF, __VA_ARGS__); } while (0)


// --- Types ---
typedef enum {
  ACP_COMMAND_VERSION = 0x00,
  ACP_COMMAND_VERSION_REPLY = 0xFF,

  ACP_COMMAND_ME_CREATE = 0x01,
  ACP_COMMAND_ME_READ = 0x02,
  ACP_COMMAND_ME_UPDATE = 0x03,
  ACP_COMMAND_ME_DELETE = 0x04,

  ACP_COMMAND_ME_READ_REPLY = 0xF2,

  ACP_COMMAND_SYN = 0x0F,
  ACP_COMMAND_ACK = 0x0B
} acp_command_t;

typedef struct memory_entity memory_entity_t;


// --- Engine ---
bool exec(acp_msg_t *msg, acp_channel_t channel, spin2_core_t *source);


// --- Network Receive SDP ---
bool _acp_sdp_init();
void _acp_sdp_callback(uint mailbox, uint port);


// --- Network Receive MCM ---
bool _acp_mc_init();
void _acp_mc_callback(
  uint8_t *data, 
  uint16_t length, 
  spin2_mc_channel spin2_channel, 
  spin2_core_t *source);


// --- Memory Entity ---
void memory_entity_init();
void memory_entity_clear();

void memory_entity_create(
  uint16_t me_id, 
  uint16_t length, 
  acp_me_callback_t callback_write, 
  acp_me_callback_t callback_read);

void memory_entity_delete(
  uint16_t me_id);

uint16_t memory_entity_read(
  memory_entity_t *var, 
  uint8_t *buffer, 
  uint16_t length);

uint16_t memory_entity_update(
  memory_entity_t *var, 
  uint8_t *buffer, 
  uint16_t length);

memory_entity_t * memory_entity_get(
  uint16_t me_id);
  
bool memory_entity_is_lock(
  memory_entity_t *var);

bool memory_entity_is_virtual(
  memory_entity_t *var);

bool memory_entity_set_lock(
  memory_entity_t *var,
  bool lock);

void memory_entity_set_buffer(
  memory_entity_t *var, 
  uint8_t *buffer, 
  uint16_t length);


// ---ACP Interface ---
uint16_t _acp_me_update_self(
  uint16_t me_id, 
  uint8_t *buffer, 
  uint16_t length);

uint16_t _acp_me_update_core(
  uint16_t me_id, 
  uint8_t *buffer, 
  uint16_t length, 
  spin2_core_t *destination);

uint16_t _acp_me_update_broadcast(
  uint16_t me_id, 
  uint8_t *buffer, 
  uint16_t length);

uint16_t _acp_me_update_host(
  uint16_t me_id, 
  uint8_t *buffer, 
  uint16_t length);


#endif //__SPINN_ACP_PRIVATE_H__
