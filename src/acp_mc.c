#include "_acp.h"

#ifdef ACP_SPIN2MC
#define MC_CONNECTIONS 8
#define MC_BUFFER_SIZE 16 // 64 Byte [the maximum length of an ACP-BBv1 is 60Byte]

inline void mc_init(mc_msg_t *mc_msg, uint8_t connection_id);
inline void mc_continue(mc_msg_t *mc_msg, uint8_t connection_id);
inline void mc_finalize(mc_msg_t *mc_msg, uint8_t connection_id);

// --- Prototypes ---
uint8_t connection_next;
bool connection_free[MC_CONNECTIONS];
uint32_t connection_keys[MC_CONNECTIONS];

acp_msg_t acp_msgbox[MC_CONNECTIONS];
acp_msg_bb_t acp_msgbox_bb[MC_CONNECTIONS];
uint32_t acp_msgbox_payload[MC_CONNECTIONS][MC_BUFFER_SIZE];


// --- Functions ---
void acp_mc_init(){
  uint32_t i;

  connection_next = 0;
  for (i=0; i<MC_CONNECTIONS; i++){
    connection_free[i] = true;
    connection_keys[i] = 0xFFFFFFFF;
  }

  spin1_callback_on(USER_EVENT, exec_bb_callback, 0);
  return;
}


void acp_mc_callback(uint param0, uint param1) {
  mc_msg_t *mc_msg;
  bool connection_find;
  uint8_t connection_id, i;
  uint32_t connection_key;

  /// Cast param0
  mc_msg = (mc_msg_t *) param0;

  /// Connection key [x y p]
  connection_key = 0 | mc_msg->x << 24 | mc_msg->y << 16 | mc_msg->p;

  if (mc_msg->ctrl == 0b00) {

    /// New connection
    if(!connection_free[connection_next]){
      io_printf(IO_BUF, "[ERR] No more multicast connections available\n");
      rt_error(RTE_ABORT);
    }

    /// Circular index
    connection_id = connection_next;
    if (connection_next == MC_CONNECTIONS-1){
      connection_next = 0;
    }
    else{
      connection_next += 1;
    }

    /// INIT
    connection_free[connection_id] = false;
    connection_keys[connection_id] = connection_key;

    mc_init(mc_msg, connection_id);
  }
  else {
    /// Find connection id
    connection_find = false;
    for (i = 0;  i < MC_CONNECTIONS && !connection_find; i++) {
      if (connection_key == connection_keys[i]) {
        connection_id = i;
        connection_find = true;
      }
    }
    if (!connection_find) {
      io_printf(IO_BUF, "[ERR] Not find multicast connection\n");
      rt_error(RTE_ABORT);
      return;
    }

    if (mc_msg->ctrl == 0b01 || mc_msg->ctrl == 0b10) {
      mc_continue(mc_msg, connection_id);
    }
    else {
      mc_finalize(mc_msg, connection_id);
    }
  }

  return;
}

void mc_init(mc_msg_t *mc_msg, uint8_t connection_id) {
  if(mc_msg->id == 0){
    acp_msgbox[connection_id].cmd = mc_msg->payload >> 16;
    acp_msgbox[connection_id].seq = mc_msg->payload & 0xFFFF;
  }
  return;
}

void mc_continue(mc_msg_t *mc_msg, uint8_t connection_id) {
  uint i = mc_msg->id-2;

  if(mc_msg->id == 1){
    acp_msgbox_bb[connection_id].acp_header = &acp_msgbox[connection_id];
    acp_msgbox_bb[connection_id].offset =  mc_msg->payload & 0x000000FF;
    acp_msgbox_bb[connection_id].buffer_id = (mc_msg->payload & 0x000FFF00) >> 8;
    acp_msgbox_bb[connection_id].cmd = (mc_msg->payload & 0x0FF00000) >> 20;
    acp_msgbox_bb[connection_id].len = ((mc_msg->payload & 0xF0000000) >> 28) << 2;

  } else {
    if(i<MC_BUFFER_SIZE){
      acp_msgbox_payload[connection_id][i] = mc_msg->payload;
    }
    else{
      io_printf(IO_BUF, "[ACP-MC] Warning %d out of buffer", i);
    }
  }

  return;
}

void mc_finalize(mc_msg_t *mc_msg, uint8_t connection_id) {
  uint i = mc_msg->id-2;

  // Save last fragment

  if(i<MC_BUFFER_SIZE){
    acp_msgbox_payload[connection_id][i] = mc_msg->payload;
  }
  else{
    io_printf(IO_BUF, "[ACP-MC] Warning %d out of buffer", i);
  }

  // Throw event
  spin1_trigger_user_event(connection_id, 0);

}

void mc_free_connection(uint8_t connection_id){
  connection_free[connection_id] = true;
  connection_keys[connection_id] = 0xFFFFFFFF;
  return;
}

acp_msg_bb_t *mc_get_msg(uint8_t connection_id){
  return &acp_msgbox_bb[connection_id];
}

uint8_t *mc_get_payload(uint8_t connection_id){
  return (uint8_t_p)acp_msgbox_payload[connection_id];
}

#endif