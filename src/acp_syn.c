#include "_acp.h"


bool acp_syn_lock;
bool acp_ack_lock;


void acp_syn_init() {
    acp_syn_lock = true;
    acp_ack_lock = true;
    return;
}

void acp_syn_wait() {
    while(spin2_swap_bool(true, &acp_syn_lock)) {
        spin1_delay_us(1);
    }
    return;
}


void acp_ack_wait() {
    while(spin2_swap_bool(true, &acp_ack_lock)) {
        spin1_delay_us(1);
    }
    return;
}


void acp_syn(){
    spin2_swap_bool(false, &acp_syn_lock);
    return;
}


void acp_ack(){
    spin2_swap_bool(false, &acp_ack_lock);
    return;
}


void acp_remote_syn(acp_channel_t channel, spin2_core_t *destination) {
    sdp_msg_t *sdp_msg;

    if (channel == ACP_CHANNEL_HOST) {
        sdp_msg = sark_msg_get();
        if (sdp_msg == NULL) {
            debug_printf("[ACP-EXEC] exec_me_read: Error! sark_msg_get failed");
            return;
        }
        
        sdp_msg->flags = 0x07;
        sdp_msg->tag = 1;
        sdp_msg->dest_port = PORT_ETH;
        sdp_msg->dest_addr = sv->dbg_addr;
        sdp_msg->srce_port = spin1_get_core_id();
        sdp_msg->srce_addr = spin1_get_chip_id();
        sdp_msg->length = 16;
        sdp_msg->cmd_rc = ACP_COMMAND_SYN;
        sdp_msg->seq = 0;
        sdp_msg->arg1 = 0;

        if (!sark_msg_send(sdp_msg, 10)) {
            debug_printf("[ACP-EXEC] exec_me_read: Error! sark_msg_send failed\n");
        }

        sark_msg_free(sdp_msg);

    } else {
        // TODO
    }

    return;
}


void acp_remote_ack(acp_channel_t channel, spin2_core_t *destination) {
    sdp_msg_t *sdp_msg;

    if (channel == ACP_CHANNEL_HOST) {
        sdp_msg = sark_msg_get();
        if (sdp_msg == NULL) {
            debug_printf("[ACP-EXEC] exec_me_read: Error! sark_msg_get failed");
            return;
        }
        
        sdp_msg->flags = 0x07;
        sdp_msg->tag = 1;
        sdp_msg->dest_port = PORT_ETH;
        sdp_msg->dest_addr = sv->dbg_addr;
        sdp_msg->srce_port = spin1_get_core_id();
        sdp_msg->srce_addr = spin1_get_chip_id();
        sdp_msg->length = 16;
        sdp_msg->cmd_rc = ACP_COMMAND_ACK;
        sdp_msg->seq = 0;
        sdp_msg->arg1 = 0;

        if (!sark_msg_send(sdp_msg, 10)) {
            debug_printf("[ACP-EXEC] exec_me_read: Error! sark_msg_send failed\n");
        }

        sark_msg_free(sdp_msg);

    } else {
        // TODO
    }

    return;
}