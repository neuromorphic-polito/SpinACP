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
// acp_cmd.cpp: Command functions for SpinACP
// ==========================================================================

#include "_acp.h"

// --- Internal types and structs ---
struct variable {
  uint16_t code;
  uint16_t length;
  uint8_t *bytes;

  bool lock_read;
  bool lock_write;

  var_callback callback_write;
  var_callback callback_read;

  uint8_t write_after_read_counter;
};

spin2_ht_t *internal_vars_ht = NULL;
spin2_ht_t *external_vars_ht = NULL;

// --- Hash table functions ---
int32_t variable_compare(void *a1, void *a2) {
  struct variable *v1 = (struct variable *) a1;
  struct variable *v2 = (struct variable *) a2;
  return (int32_t)(v1->code - v2->code);
}

uint32_t variable_key(void *a) {
  struct variable *v = (struct variable *) a;
  return (uint32_t) v->code;
}

spin2_ht_t *get_internal_vars_ht() {
  if (internal_vars_ht == NULL) {
    cmd_variable_init();
  }
  return internal_vars_ht;
}

// --- Functions ---
/**
 * ACP Initialize
 *
 * @return
 */
bool cmd_variable_init() {
  cmd_variable_destroy();

  spin2_ht_create(
      &internal_vars_ht,
      SPIN2_HT_TINY,
      variable_compare, variable_key
  );

  spin2_ht_create(
      &external_vars_ht,
      SPIN2_HT_TINY,
      variable_compare, variable_key
  );
}

/**
 * ACP Destroy
 * Destroy the entire ACP-Var contents
 *
 * @return
 */
bool cmd_variable_destroy() {
  struct variable *item;

  if (internal_vars_ht != NULL) {
    for (uint16_t i = 0; i < 0xFFFF; i++) {
      if (spin2_ht_remove(internal_vars_ht, i, (void **) &item)) {
        sark_free(item);
      }
    }
    spin2_ht_destroy(&internal_vars_ht);
  }

  if (external_vars_ht != NULL) {
    for (uint16_t i = 0; i < 0xFFFF; i++) {
      if (spin2_ht_remove(external_vars_ht, i, (void **) &item)) {
        sark_free(item);
      }
    }
    spin2_ht_destroy(&internal_vars_ht);
  }
  return true;
}

/**
 * ACP Variable register
 * register a new ACP-Var, all memory will be allocated
 *
 * @param var_code
 * @param value
 * @param length
 * @return
 */
bool cmd_variable_register(uint16_t var_code, uint16_t length,
                           var_callback callback_write, var_callback callback_read) {
  debug_printf("[ACP] Variable register %d\n", var_code);
  struct variable *var;

  var = (struct variable *) sark_alloc(1, sizeof(struct variable));

  var->code = var_code;
  var->length = length;
  var->lock_write = false;
  var->lock_read = false;
  var->callback_write = callback_write;
  var->callback_read = callback_read;
  var->write_after_read_counter = 0;

  var->bytes = (uint8_t *) sark_alloc(var->length, sizeof(uint8_t));
  if (var->bytes == NULL) {
    rt_error(RTE_MALLOC);
  }

  if (!spin2_ht_insert(get_internal_vars_ht(), var)) {
    debug_printf("[ACP] Error: impossible to add variable %i!\n", var_code);
    sark_free(var->bytes);
    sark_free(var);
    return false;
  }

  return true;
}

/**
 * ACP Variable write
 * write in the ACP-Var the content of value, if value contains too many bytes, only
 * the correct number of byte will be writed in the ACP-Var.
 *
 * @param var_code
 * @param value
 * @param length
 * @return
 */
bool cmd_variable_write(uint16_t var_code, uint8_t *value, uint16_t length) {
  int i;
  uint16_t min_length;
  struct variable *var;

  if (!spin2_ht_get(get_internal_vars_ht(), var_code, (void **) &var)) {
    debug_printf("[ACP] Impossible get variable %d!\n", var_code);
    return false;
  }

  if (var->write_after_read_counter > 0) {
    debug_printf("[ACP] WARNING Write without read %d!\n", var->write_after_read_counter);
  }

  min_length = var->length;
  if (min_length > length)
    min_length = length;

  for(i=0; i<min_length; i++){
   var->bytes[i] = value[i];
  }

  // Clean buffer -> to the word
  for(i=0; i < (var->length & 0b11); i++) {
    var->bytes[min_length + i] = 0;
  }

  var->write_after_read_counter += 1;

  if (var->callback_write != NULL && var->lock_write == false)
    var->callback_write(var_code, value, length);

  return true;
}

/**
 * ACP Variable Read
 * Read the content of an ACP-Var and write in value all its bytes
 * at the end of read, if exit with success, length contains the number of writed bytes in value
 *
 * @param var_code
 * @param value
 * @param length
 * @return
 */
bool cmd_variable_read(uint16_t var_code, uint8_t *value, uint16_t *length) {
  int i;
  uint16_t min_length;

  struct variable *var;
  if (!spin2_ht_get(get_internal_vars_ht(), var_code, (void **) &var)) {
    debug_printf("[ACP] Impossible get variable %d!\n", var_code);
    return false;
  }

  min_length = var->length;
  if (min_length > *length)
    min_length = *length;

  if (value != NULL) {
    for(i=0; i<min_length; i++){
      value[i] = var->bytes[i];
    }
    var->write_after_read_counter = 0;
  }
  *length = min_length;

  return true;
}

/**
 *
 * @param var_code
 * @param value
 * @return
 */
bool cmd_variable_test(uint16_t var_code, uint8_t *value) {
  struct variable *var;

  if (!spin2_ht_get(get_internal_vars_ht(), var_code, (void **) &var)) {
    debug_printf("[ACP] Impossible get variable %d!\n", var_code);
    return false;
  }
  *value = var->write_after_read_counter;
  return true;
}

/**
 * ACP Variable Toggle
 * Toggle the content of an ACP-Var
 *
 * @param var_code
 * @return
 */
bool cmd_variable_toggle(uint16_t var_code) {
  uint16_t i;
  struct variable *var;

  if (!spin2_ht_get(get_internal_vars_ht(), var_code, (void **) &var)) {
    debug_printf("[ACP] Impossible get variable %d!\n", var_code);
    return false;
  }

  for (i = 0; i < var->length; i++)
    var->bytes[i] = ~var->bytes[i];

  var->write_after_read_counter += 1;
  return true;
}
