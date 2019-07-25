#include "_acp.h"


void acp_init() {
  uint cpsr;

  cpsr = cpu_int_disable();
  _acp_sdp_init();
  _acp_mc_init();
  acp_syn_init();
  memory_entity_init();
  cpu_int_restore(cpsr);

  return;
}


void acp_me_clear(){
  uint cpsr;

  cpsr = cpu_int_disable();
  memory_entity_clear();
  cpu_int_restore(cpsr);

  return;
}


void acp_me_create(
    uint16_t me_id, 
    uint16_t length, 
    acp_me_callback_t callback_write, 
    acp_me_callback_t callback_read) {

  uint cpsr;

  cpsr = cpu_int_disable();
  memory_entity_create(me_id, length, callback_write, callback_read);
  cpu_int_restore(cpsr);

  return;
}


uint16_t acp_me_read(
    uint16_t me_id, 
    uint8_t *buffer, 
    uint16_t length, 
    acp_channel_t channel, 
    spin2_core_t *core, 
    bool sync) {
  
  uint cpsr;
  uint16_t bytes_read;  
  memory_entity_t *var;
  
  var = memory_entity_get(me_id);

  if (memory_entity_is_virtual(var)) {
    cpsr = cpu_int_disable();
    memory_entity_set_buffer(var, buffer, length);
    cpu_int_restore(cpsr);
  }
  
  if (channel != ACP_CHANNEL_SELF) {
    if (sync && channel==ACP_CHANNEL_CORE) {
      spin2_mc_wfs_core(core);
    } 
    else if (sync && channel==ACP_CHANNEL_BROADCAST) {
      spin2_mc_wfs();
    } else if(sync && channel==ACP_CHANNEL_HOST) {
      acp_syn_wait();
      acp_remote_ack(ACP_CHANNEL_HOST, NULL);
    }

    // Polling on memory entity lock
    while(memory_entity_is_lock(var)) {
      spin1_delay_us(1);
    }
  }

  cpsr = cpu_int_disable();
  if (!memory_entity_is_virtual(var)) {
    // Atomic Read
    bytes_read = memory_entity_read(var, buffer, length);
  } else {
    // Unset buffer
    bytes_read = length;
    memory_entity_set_buffer(var, NULL, 0);
  }
  cpu_int_restore(cpsr);

  return bytes_read;
}


uint16_t acp_me_update(
    uint16_t me_id, 
    uint8_t *buffer, 
    uint16_t length, 
    acp_channel_t channel, 
    spin2_core_t *core, 
    bool sync) {

  switch (channel) {
    case ACP_CHANNEL_SELF:
      if(sync){
        // NOPE
      }
      return _acp_me_update_self(me_id, buffer, length);
    case ACP_CHANNEL_CORE:
      if(sync){ 
        spin2_mc_syn(core); 
      } 
      return _acp_me_update_core(me_id, buffer, length, core);
    case ACP_CHANNEL_BROADCAST:
      if(sync) { 
        spin2_mc_wfs(); 
      } 
      return _acp_me_update_broadcast(me_id, buffer, length);
    case ACP_CHANNEL_HOST:
      if(sync) {
        // TODO
      }
      return _acp_me_update_host(me_id, buffer, length);
  }

  return 0;
}

bool acp_me_delete(uint16_t me_id) {
  uint cpsr;

  cpsr = cpu_int_disable();
  memory_entity_delete(me_id);
  cpu_int_restore(cpsr);

  return true;
}


// --- Private ---

uint16_t _acp_me_update_self(
    uint16_t me_id, 
    uint8_t *value, uint16_t length) {

  uint16_t r;
  uint cpsr;

  memory_entity_t *me;
  me = memory_entity_get(me_id);

  cpsr = cpu_int_disable();
  r = memory_entity_update(me, value, length);
  cpu_int_restore(cpsr);

  return r;
}


uint16_t _acp_me_update_core(
    uint16_t me_id,
    uint8_t *buffer,
    uint16_t length,
    spin2_core_t *destination) {

  uint8_t head[8];

  uint16_t cmd;
  uint16_t seq;
  uint32_t hdr_lv2;

  cmd = ACP_COMMAND_ME_UPDATE;
  seq = 0 |  (length & 0x01FF);
  hdr_lv2 = (0 << 16) | (me_id);

  head[0] = ((uint8_t_p)&cmd)[0];
  head[1] = ((uint8_t_p)&cmd)[1];
  head[2] = ((uint8_t_p)&seq)[0];
  head[3] = ((uint8_t_p)&seq)[1];

  head[4] = ((uint8_t_p)&hdr_lv2)[0];
  head[5] = ((uint8_t_p)&hdr_lv2)[1];
  head[6] = ((uint8_t_p)&hdr_lv2)[2];
  head[7] = ((uint8_t_p)&hdr_lv2)[3];

  spin2_mc_send(
      &head[0], 8,
      buffer, length,
      NULL, 0,
      SPIN2_MC_P2P, destination);

  return length;
}


uint16_t _acp_me_update_broadcast(
    uint16_t me_id,
    uint8_t *buffer,
    uint16_t length) {

  uint8_t head[8];

  uint16_t cmd;
  uint16_t seq;
  uint32_t hdr_lv2;

  cmd = ACP_COMMAND_ME_UPDATE;
  seq = 0 |  (length & 0x01FF);
  hdr_lv2 = (0 << 16) | (me_id);

  head[0] = ((uint8_t_p)&cmd)[0];
  head[1] = ((uint8_t_p)&cmd)[1];
  head[2] = ((uint8_t_p)&seq)[0];
  head[3] = ((uint8_t_p)&seq)[1];

  head[4] = ((uint8_t_p)&hdr_lv2)[0];
  head[5] = ((uint8_t_p)&hdr_lv2)[1];
  head[6] = ((uint8_t_p)&hdr_lv2)[2];
  head[7] = ((uint8_t_p)&hdr_lv2)[3];

  spin2_mc_send(
      &head[0], 8,
      buffer, length,
      NULL, 0,
      SPIN2_MC_BD,  NULL);

  return length;
}


uint16_t _acp_me_update_host(
    uint16_t me_id,
    uint8_t *buffer,
    uint16_t length) {

  // Implementare ME on Host ed usare codice in mpi_sdp.c
  // TODO
  return length;
}


