#include "_acp.h"


bool _acp_sdp_init(){
  spin2_sdp_callback_on(ACP_SDP_PORT, _acp_sdp_callback);
  return true;
}


void _acp_sdp_callback(uint mailbox, uint port) {
  int r;

  sdp_msg_t *sdp_msg = (sdp_msg_t *) mailbox;

  acp_msg_t acp_msg;
  acp_channel_t acp_msg_channel;
  spin2_core_t acp_msg_source;


  // --- Debug SDP ---
  /*
  debug_printf("[ACP-SDP] Received Packet\n");
  debug_printf("          cmd: %x\n",  sdp_msg->cmd_rc);
  debug_printf("          seq: %x\n",  sdp_msg->seq);
  debug_printf("          arg1: %x\n", sdp_msg->arg1);
  debug_printf("          arg2: %x\n", sdp_msg->arg2);
  debug_printf("          arg3: %x\n", sdp_msg->arg3);
  */

  // --- Extract SCP/ACP ---
  acp_msg.cmd = sdp_msg->cmd_rc;
  acp_msg.seq = sdp_msg->seq >> 9;
  acp_msg.length = sdp_msg->seq & 0x01FF;
  acp_msg.header_lv2 = sdp_msg->arg1;
  acp_msg.payload = (uint8_t_p) &sdp_msg->arg2;

  acp_msg_channel = ACP_CHANNEL_HOST;

  r = exec(&acp_msg, acp_msg_channel, NULL);
  
  sark_msg_free(sdp_msg);

  return;
}

/*
void sdp_msg_swap_header(sdp_msg_t *msg) {
  uint dest_port = msg->dest_port;
  uint dest_addr = msg->dest_addr;
  msg->dest_port = msg->srce_port;
  msg->srce_port = dest_port;
  msg->dest_addr = msg->srce_addr;
  msg->srce_addr = dest_addr;
}
*/
