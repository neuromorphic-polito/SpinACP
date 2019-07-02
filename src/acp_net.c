#include "_acp.h"

typedef uint8_t *uint8_p;

bool cmd_net_variable_write(
    uint16_t var_code, uint8_t *value, uint16_t length, uint16_t address, uint8_t port) {
  sdp_msg_t *msg = sark_msg_get();
  uint8_t *msg_payload;
  uint8_t acp_length;

  if (msg == NULL) {
    debug_printf("[ACP-NET-WRITE] Error in get SDP buffer\n");
    rt_error(RTE_ABORT);
  }

  // Create the Packet
  msg->flags = 0x07;
  msg->tag = 0;
  msg->dest_port = port;
  msg->dest_addr = address;
  msg->srce_port = spin1_get_core_id();
  msg->srce_addr = spin1_get_chip_id();

  if (length % 4 == 0) {
    acp_length = length >> 2;
  } else {
    acp_length = (length >> 2) + 1;
  }
  msg->length = 16 + (acp_length << 2);

  msg->cmd_rc = (uint16_t) 0xF1;
  msg->seq = 0;

  msg->arg1 = (uint32_t)(
      ((acp_length & 0xF) << 28) |
          ((ACP_CMD_WRITE_VAR & 0xFF) << 20) |
          ((var_code & 0xFFFF) << 8) |
          ((0x0 & 0xF))
  );

  msg_payload = (uint8_p) &msg->arg2;

  sark_mem_cpy(msg_payload, value, length);
  if (!sark_msg_send(msg, 10)) {
    debug_printf("[ACP-NET-WRITE] Error, impossible send the SDP\n");
    rt_error(RTE_ABORT);
  }

  sark_msg_free(msg);
  return true;
}

bool acp_net_variable_read(
    uint16_t var_code, uint8_t *value, uint16_t *length, uint16_t address, uint8_t port) {

}

#ifdef ACP_SPIN2MC
bool cmd_net_variable_write_all(
    uint16_t var_code, uint8_t *value, uint16_t length) {
  uint8_t acp_length, i, k;
  uint16_t j;
  uint32_t payload;

  mc_msg_t *mc_msg;

  acp_length = length >> 2;
  if ((length & 0b11) != 0) {
    acp_length += 1;
  }

  mc_msg = spin2_mc_alloc();

  /// Send ACP header
  mc_msg->payload = 0x00F10000; // Immediate Write, PKT 0
  spin2_mc_send(mc_msg, false);

  /// Send BB header
  mc_msg->payload =
      0 | ((acp_length & 0xF) << 28) |
          ((ACP_CMD_WRITE_VAR & 0xFF) << 20) |
          ((var_code & 0xFFFF) << 8) |
          ((0x0 & 0xF));
  spin2_mc_send(mc_msg, false);

  /// Send Payload
  j=0;
  for(i=0; i<acp_length-1; i++){
    payload =
        0 | (value[j++]) |
            (value[j++] << 8) |
            (value[j++] << 16) |
            (value[j++] << 24);
    mc_msg->payload = payload;
    spin2_mc_send(mc_msg, false);
  }

  /// The last fragment can be partial, pad with zero k=0 z=0 k=1 z=8
  payload = 0;
  for(k=0; k<3 && j<length; k++){
      payload |= (value[j++] << (k<<3));
  }
  if(j<length){
    payload |= (value[j++] << 24);
  }

//  io_printf(IO_BUF, "[ACP-NET-SENDALL] %d %08x\n", *value, payload);
  mc_msg->payload = payload;
  spin2_mc_send(mc_msg, true);

  spin2_mc_free(mc_msg);
  return true;
}
#endif
