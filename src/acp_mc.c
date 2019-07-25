#include "_acp.h"


bool _acp_mc_init(){
  spin2_mc_callback_register(_acp_mc_callback);
  return true;
}


void _acp_mc_callback(
    uint8_t *data, uint16_t length,
    spin2_mc_channel spin2_channel, spin2_core_t *source) {

  bool r;
  acp_msg_t acp_msg;
  acp_channel_t acp_msg_channel;

  acp_msg.cmd = *( (uint16_t_p) &data[0]);
  acp_msg.seq = *( (uint16_t_p) &data[2]) >> 9;
  acp_msg.length = *( (uint16_t_p) &data[2]) & 0x01FF;
  acp_msg.header_lv2 = *( (uint32_t_p) &data[4]);
  acp_msg.payload = &data[8];

  switch (spin2_channel){
    case SPIN2_MC_P2P:
      acp_msg_channel = ACP_CHANNEL_CORE;
      debug_printf("[ACP] Received ACPoverMC (PP) \n");
      break;
    case SPIN2_MC_BD:
      acp_msg_channel = ACP_CHANNEL_BROADCAST;
      debug_printf("[ACP] Received ACPoverMC (BC) \n");
      break;
  }
  debug_printf("      cmd: %04x\n", acp_msg.cmd);
  debug_printf("      seq: %04x\n", acp_msg.seq);
  debug_printf("      len: %04x\n", acp_msg.length);
  debug_printf("      hl2: %08x\n", acp_msg.header_lv2);

  r = exec(&acp_msg, acp_msg_channel, source);

  return;
}
