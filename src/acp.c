#include "_acp.h"

// --- Functions ---
bool acp_variable_init() {
  bool r;
  uint cpsr;

  cpsr = cpu_int_disable();
  r = cmd_variable_init();
  cpu_int_restore(cpsr);

  return r;
}

bool acp_variable_destroy() {
  bool r;
  uint cpsr;

  cpsr = cpu_int_disable();
  r = cmd_variable_destroy();
  cpu_int_restore(cpsr);

  return r;
}

bool acp_variable_register(uint16_t var_code, uint16_t length,
                           var_callback callback_write, var_callback callback_read) {
  bool r;
  uint cpsr;

  cpsr = cpu_int_disable();
  r = cmd_variable_register(var_code, length, callback_write, callback_read);
  cpu_int_restore(cpsr);

  return r;
}

bool acp_variable_write(uint16_t var_code, uint8_t *value, uint16_t length) {
  bool r;
  uint cpsr;

  cpsr = cpu_int_disable();
  r = cmd_variable_write(var_code, value, length);
  cpu_int_restore(cpsr);

  return r;
}

bool acp_variable_read(uint16_t var_code, uint8_t *value, uint16_t *length) {
  bool r;
  uint cpsr;

  cpsr = cpu_int_disable();
  r = cmd_variable_read(var_code, value, length);
  cpu_int_restore(cpsr);

  return r;
}

bool acp_variable_read_after_write(uint16_t var_code, uint8_t *value, uint16_t *length) {
  bool r, finish;
  uint cpsr;
  uint8_t write_after_read_counter;

  do {

    cpsr = cpu_int_disable();
    cmd_variable_test(var_code, &write_after_read_counter);
    finish = (write_after_read_counter != 0);
    if(finish){
      r = cmd_variable_read(var_code, value, length);
    }
    cpu_int_restore(cpsr);

    if(!finish){
      spin1_delay_us(1);
    }

  } while(!finish);

  return r;
}

bool acp_net_variable_write(uint16_t var_code, uint8_t *value, uint16_t length,
                            uint16_t address, uint8_t port) {
  bool r;
  uint cpsr;

  cpsr = cpu_int_disable();
  r = cmd_net_variable_write(var_code, value, length, address, port);
  cpu_int_restore(cpsr);

  return r;
}

bool acp_variable_toggle(uint16_t var_code) {
  bool r;
  uint cpsr;

  cpsr = cpu_int_disable();
  r = cmd_variable_toggle(var_code);
  cpu_int_restore(cpsr);

  return r;
}
