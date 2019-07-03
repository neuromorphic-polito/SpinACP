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
// acp_sdp.cpp: SDP (SpiNNaker Datagram Protocol) functions for SpinACP
// ==========================================================================

#include "_acp.h"


// --- Declarations ---
void sdp_msg_swap_header(sdp_msg_t *msg);

// --- Functions ---
void acp_sdp_callback(uint mailbox, uint port) {
  int r;

  sdp_msg_t *sdp_msg;
  acp_msg_t acp_msg;
  acp_msg_bb_t acp_msg_bb;
  acp_msg_reply_t acp_msg_reply;

  // ---- Mailbox cast ---
  sdp_msg = (sdp_msg_t *) mailbox;

  // --- Extract SCP/ACP ---
  acp_msg.sdp_header = sdp_msg;

  acp_msg.cmd = sdp_msg->cmd_rc;
  acp_msg.seq = sdp_msg->seq;

  // --- Execute command ---
  io_printf(IO_BUF, "ACP!\n");
  switch (acp_msg.cmd) {
    case ACP_PKT_IMMEDIATE:

      /// Extract ACP Buffer Binding header
      acp_msg_bb.acp_header = &acp_msg;

      acp_msg_bb.offset =  sdp_msg->arg1 & 0x0000000F;
      acp_msg_bb.buffer_id = (sdp_msg->arg1 & 0x000FFF00) >> 8;
      acp_msg_bb.cmd = (sdp_msg->arg1 & 0x0FF00000) >> 20;
      acp_msg_bb.len = ((sdp_msg->arg1 & 0xF0000000) >> 28) << 2;

      /// Exec
      r = exec_bb(&acp_msg_bb, (uint8_t_p) &sdp_msg->arg2);
      break;

    case ACP_PKT_REPLY:
      acp_msg_reply.acp_header = &acp_msg;
      acp_msg_reply.reply = 0;

      r = exec_reply(&acp_msg_reply, (uint8_t_p) &sdp_msg->arg1);
      break;
  }

  //sdp_msg_t *msg = (sdp_msg_t *) mailbox;
  sark_msg_free(sdp_msg);

  return;
}

void sdp_msg_swap_header(sdp_msg_t *msg) {
  uint dest_port = msg->dest_port;
  uint dest_addr = msg->dest_addr;
  msg->dest_port = msg->srce_port;
  msg->srce_port = dest_port;
  msg->dest_addr = msg->srce_addr;
  msg->srce_addr = dest_addr;
}

//void sdp_msg_print(sdp_msg_t *msg){
//  debug_printf(" - Len:  %d Byte (SCP: %d Byte)\n", msg->length, msg->length - 8);
//  debug_printf(" - Flag: %02x\n", msg->flags);
//  debug_printf(" - Tag:  %02x\n", msg->tag);
//  debug_printf(" - Src:  %04x : %02x\n", msg->srce_addr, msg->srce_port);
//  debug_printf(" - Dst:  %04x : %02x\n", msg->dest_addr, msg->dest_port);
//}
