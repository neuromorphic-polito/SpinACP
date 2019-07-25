#include "_acp.h"


// --- Internal types and structs ---
struct memory_entity {
  acp_me_callback_t callback_write;
  acp_me_callback_t callback_read;
  uint8_t *buffer;
  uint16_t code;
  uint16_t buffer_length; 
  uint16_t buffer_bytes;
  bool virtual;
  bool lock;
};


// --- Global Variables ---
spin2_ht_t *internal_vars_ht = NULL;


// --- Hash table functions ---
int32_t variable_compare(void *a1, void *a2) {
  memory_entity_t *v1 = (memory_entity_t *) a1;
  memory_entity_t *v2 = (memory_entity_t *) a2;
  return (int32_t)(v1->code - v2->code);
}


uint32_t variable_key(void *a) {
  memory_entity_t *v = (memory_entity_t *) a;
  return (uint32_t) v->code;
}


// --- Functions ---
void memory_entity_init() {
  if (internal_vars_ht != NULL){
    memory_entity_clear();
  }

  spin2_ht_create(
      &internal_vars_ht,
      SPIN2_HT_TINY,
      variable_compare,
      variable_key,
      NULL
  );

  return;
}

void memory_entity_create(
    uint16_t me_id, 
    uint16_t length,
    acp_me_callback_t callback_write,
    acp_me_callback_t callback_read) {

  memory_entity_t *var;

  debug_printf("[ACP] Variable register %d\n", me_id);
  
  var = (memory_entity_t *) sark_alloc(1, sizeof(memory_entity_t));
  if (var == NULL) {
    error_printf("[ACP-ME] Cannot allocate ME Struct %d Byte\n", 
        sizeof(memory_entity_t));
    rt_error(RTE_ABORT);
  }

  var->code = me_id;
  var->buffer_length = length;
  var->buffer_bytes = 0;
  var->lock = true;
  var->callback_write = callback_write;
  var->callback_read = callback_read;

  if (var->buffer_length == 0){
    var->virtual = true;
    var->buffer = NULL;
  }
  else {
    var->virtual = false;
    var->buffer = (uint8_t *) sark_alloc(
      1, var->buffer_length * sizeof(uint8_t));
    if (var->buffer == NULL) {
      io_printf(IO_BUF, "[ACP-ME] Cannot allocate DTCM %d Byte\n", 
        var->buffer_length);
      rt_error(RTE_ABORT);
    }
  }

  if (!spin2_ht_insert(internal_vars_ht, var)) {
    error_printf("[ACP] Error: impossible to add variable %i\n", 
      me_id);
    rt_error(RTE_ABORT);
  }

  return;
}

memory_entity_t * memory_entity_get(uint16_t me_id){
    memory_entity_t *var;

    if (!spin2_ht_get(internal_vars_ht, (uint32_t)me_id, (void **)&var)) {
      error_printf("[ACP] Cannot get memory entity %d!\n", me_id);
      return NULL;
    }

    return var;
}

uint16_t memory_entity_read(
    memory_entity_t *var,
    uint8_t *buffer, 
    uint16_t length) {
  
  int i;

  if (length == 0){
    length = var->buffer_bytes;
  }

  if (length > var->buffer_bytes){
    error_printf("[ACP] Warning! Try to read %d, available %d\n", 
      length, var->buffer_bytes);
    length = var->buffer_bytes;
  }

  if (buffer != NULL) {
    for(i=0; i<length; i++) {
      buffer[i] = var->buffer[i];
    }
  }

  if (var->callback_read != NULL){
    var->callback_read(var->code, buffer, length);
  }

  return length;
}


uint16_t memory_entity_update(
    memory_entity_t *var, 
    uint8_t *buffer, 
    uint16_t length) {

  int i;

  if (length > var->buffer_length){
    error_printf("[ACP] Warning! Try to write %d, available %d\n", 
      length, var->buffer_length);
    length = var->buffer_length;
  }

  for(i=0; i < length; ++i) {
    var->buffer[i] = buffer[i];
  }
  var->buffer_bytes = length;

  if (var->callback_write != NULL) {
    var->callback_write(var->code, buffer, length);
  }

  return length;
}

bool memory_entity_set_lock(
  memory_entity_t *var,
  bool lock) {
  
  return spin2_swap_bool(lock, &(var->lock));
}


bool memory_entity_is_virtual(
    memory_entity_t *var) {

  return var->virtual;
}


void memory_entity_set_buffer(
    memory_entity_t *var, 
    uint8_t *buffer, 
    uint16_t length) {

  var->buffer = buffer;
  var->buffer_length = length;
  var->buffer_bytes = 0;
  
  return;
}


void memory_entity_delete(uint16_t me_id) {
  // TODO
  return;
}


void memory_entity_clear() {
  // TODO
  return;
}


bool memory_entity_is_lock(memory_entity_t *var) {
  return spin2_swap_bool(true, &(var->lock));
}
