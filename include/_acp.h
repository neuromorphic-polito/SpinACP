#ifndef __SPINN_ACP_PRIVATE_H__
#define __SPINN_ACP_PRIVATE_H__

#include "acp.h"

#define ACP_PKT_IMMEDIATE 0xF1
#define ACP_PKT_REPLY 0xF4

#ifdef ACP_DEBUG
#define debug_printf(...) \
  do { io_printf(IO_BUF, __VA_ARGS__); } while (0)
#else
#define debug_printf(...) \
  do { } while (0)
#endif


// ---
typedef struct {
  // SDP
  sdp_msg_t *sdp_header;

  // ACP
  uint16_t cmd;
  uint16_t seq;
} acp_msg_t;

typedef struct {
  // SDP-ACP
  acp_msg_t *acp_header;

  // Buffer Binding header
  uint8_t len;      //  4bit
  uint8_t cmd;      //  8bit  Command
  uint16_t buffer_id;  // 12bit  Buffer id
  uint8_t offset;   //  8bit  Offset

} acp_msg_bb_t;

typedef struct {
  // SDP-ACP
  acp_msg_t *acp_header;

  // Buffer Binding header
  uint32_t reply;   //  32bit
} acp_msg_reply_t;

typedef uint8_t *uint8_t_p;

// --- CMD ---
bool cmd_variable_init();
bool cmd_variable_destroy();
bool cmd_variable_register(uint16_t var_code, uint16_t length,
                           var_callback callback_write, var_callback callback_read);
bool cmd_variable_write(uint16_t var_code, uint8_t *value, uint16_t length);
bool cmd_variable_read(uint16_t var_code, uint8_t *value, uint16_t *length);
bool cmd_variable_toggle(uint16_t var_code);

bool cmd_variable_test(uint16_t var_code, uint8_t *value);

bool cmd_net_variable_write(uint16_t var_code, uint8_t *value, uint16_t length,
                            uint16_t address, uint8_t port);

// --- EXEC ---
#ifdef ACP_SPIN2MC
void exec_bb_callback(uint connection_id, uint arg1);
#endif

bool exec_bb(acp_msg_bb_t *msg, uint8_t *payload);
bool exec_bb_write(acp_msg_bb_t *msg, uint8_t *payload);
bool exec_bb_read(acp_msg_bb_t *msg, uint8_t *payload);

bool exec_reply(acp_msg_reply_t *msg, uint8_t *msg_payload);
bool exec_reply_read(acp_msg_reply_t *msg, uint8_t *msg_payload);

// --- NET ---


// --- MC ---
void mc_free_connection(uint8_t connection);
acp_msg_bb_t *mc_get_msg(uint8_t connection_id);
uint8_t *mc_get_payload(uint8_t connection_id);


#endif //__SPINN_ACP_PRIVATE_H__
