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
// acp_exec.cpp: Execution functions for SpinACP
// ==========================================================================

#include "_acp.h"

#ifdef ACP_SPIN2MC
void exec_bb_callback(uint connection_id, uint arg1){
  //io_printf(IO_BUF, "[ACP-CLBK] Hello %d\n", connection_id);
  exec_bb(mc_get_msg(connection_id), mc_get_payload(connection_id));
  mc_free_connection(connection_id);
}
#endif

/**
 * Exec a buffer binding command
 * @param msg
 * @param payload
 * @return
 */
bool exec_bb(acp_msg_bb_t *msg, uint8_t *payload) {
  // --- Exec ---
  switch (msg->cmd) {
    case ACP_CMD_WRITE_VAR:
      return exec_bb_write(msg, payload);

    case ACP_CMD_READ_VAR:
      return exec_bb_read(msg, payload);
  }

  return false;
}


/**
 * Exec a Buffer Binding write command
 * @param msg
 * @param payload
 * @return
 */
bool exec_bb_write(acp_msg_bb_t *msg, uint8_t *payload) {
  uint16_t length = msg->len;  // <- value in Byte
  cmd_variable_read(msg->buffer_id, (uint8_t *) NULL, &length);
  cmd_variable_write(msg->buffer_id, payload, length);
  return true;
}

/**
 * Exec a Buffer Binding read command
 * @param msg
 * @param payload
 * @return
 */
bool exec_bb_read(acp_msg_bb_t *msg, uint8_t *payload) {
  // TODO: Send to host or send internally
  uint16_t length;
  sdp_msg_t *sdp_msg = msg->acp_header->sdp_header;

  // --- SDP Header [SEND TO HOST] ---
  sdp_msg->flags = 0x07;
  sdp_msg->tag = 1;
  sdp_msg->dest_port = PORT_ETH;
  sdp_msg->dest_addr = sv->dbg_addr;
  sdp_msg->srce_port = spin1_get_core_id();
  sdp_msg->srce_addr = spin1_get_chip_id();

  // --- SCP/ACP Header ---
  sdp_msg->cmd_rc = 0xF4;
//  sdp_msg->seq = sdp_msg->seq;

  cmd_variable_read(msg->buffer_id, payload, &length);
  sdp_msg->arg1 = length;

  // --- Send ---
  if (!sark_msg_send(sdp_msg, 10)) {
    debug_printf("[ACP-NET] Error, impossible send the SDP\n");
    return false;
  }

  return true;
}

bool exec_reply(acp_msg_reply_t *msg, uint8_t *msg_payload) {
  return false;
}

bool exec_reply_read(acp_msg_reply_t *msg, uint8_t *msg_payload) {
  return false;
}
