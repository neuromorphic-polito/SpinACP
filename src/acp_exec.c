#include "_acp.h"


static inline bool exec_me_update(
    acp_msg_t *msg, acp_channel_t channel, spin2_core_t *source);


static inline bool exec_me_read(
    acp_msg_t *msg, acp_channel_t channel, spin2_core_t *source);


bool exec(
    acp_msg_t *acp_msg, 
    acp_channel_t channel, 
    spin2_core_t *source) {

  bool r;
 
  if (acp_msg->cmd <= 0xFF) { 
    // BUILTIN COMMAND
    if (acp_msg->cmd == ACP_COMMAND_ME_UPDATE) {
      r = exec_me_update(acp_msg, channel, source);
    } else if (acp_msg->cmd == ACP_COMMAND_ME_READ) {
      r = exec_me_read(acp_msg, channel, source);
    } else if (acp_msg->cmd == ACP_COMMAND_SYN) {
      acp_syn();
      r = true;
    } else if (acp_msg->cmd == ACP_COMMAND_ACK) {
      acp_ack();
      r = true;
    } else {
      r = false;
    }
  } else {
    // USER COMMAND
    // TODO
    r=false;
  }

  return r;
}


inline bool exec_me_update(
    acp_msg_t *acp_msg, 
    acp_channel_t channel, 
    spin2_core_t *source) {
  
  uint16_t me_id;
  memory_entity_t *var;
  
  me_id = (uint16_t)(acp_msg->header_lv2 & 0x0000FFFF);
  var = memory_entity_get(me_id); 

  memory_entity_update(var, acp_msg->payload, acp_msg->length);
  memory_entity_set_lock(var, false);
  
  return true;  
}


inline bool exec_me_read(
    acp_msg_t *msg, 
    acp_channel_t channel, 
    spin2_core_t *source) {

  int i;
  bool r;
  
  sdp_msg_t *sdp_msg;
  uint8_t buffer[256] = {0};
  uint16_t me_id;
  uint16_t me_length;
  memory_entity_t *var;


  if (channel == ACP_CHANNEL_HOST) {
    sdp_msg = sark_msg_get();
    if (sdp_msg == NULL) {
      debug_printf("[ACP-EXEC] exec_me_read: Error! sark_msg_get failed");
      return false;
    }

    me_id = msg->header_lv2 & 0xFFFF;

    var = memory_entity_get(me_id); 
    me_length = memory_entity_read(var, &buffer[0], 0);
    
    sdp_msg->flags = 0x07;
    sdp_msg->tag = 1;
    sdp_msg->dest_port = PORT_ETH;
    sdp_msg->dest_addr = sv->dbg_addr;
    sdp_msg->srce_port = spin1_get_core_id();
    sdp_msg->srce_addr = spin1_get_chip_id();
    sdp_msg->length = 16+me_length;

    sdp_msg->cmd_rc = ACP_COMMAND_ME_READ_REPLY;
    sdp_msg->seq = 0 | (me_length & 0x01FF);
    sdp_msg->arg1 = 0;
    sdp_msg->arg2 = buffer[3] << 24 | buffer[2] << 16 | buffer[1] << 8 | buffer[0];
    sdp_msg->arg3 = buffer[7] << 24 | buffer[6] << 16 | buffer[5] << 8 | buffer[4];

    for (i=8; i < me_length; i++){
      sdp_msg->data[i-8] = buffer[i];
    }

    if (!sark_msg_send(sdp_msg, 10)) {
      debug_printf("[ACP-EXEC] exec_me_read: Error! sark_msg_send failed\n");
      r = false;
    }

    sark_msg_free(sdp_msg);
    r = true;

  } else {
    // TODO -> implement with Spin2-MC
  }

  return r;
}
