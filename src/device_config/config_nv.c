#include "config_nv.h"
#include "reset.h"
#include "hal/nvm.h"
#include "hal/printf_selector.h"
#include "nvm_items.h"
#include <string.h>

#ifdef HAL_SILABS
#include "silabs_config.h"
#endif

#ifndef STRINGIFY
#define _STRINGIFY(x)    #x
#define STRINGIFY(x)     _STRINGIFY(x)
#endif

#ifndef DEFAULT_CONFIG
const char default_config_data[] = "unknown;TS0012-CUSTOM;";
#else
const char default_config_data[] = STRINGIFY(DEFAULT_CONFIG);
#endif

device_config_str_t device_config_str;

static void validate_and_terminate_config(void) {
    if (device_config_str.size >= sizeof(device_config_str.data) ||
        memchr(device_config_str.data, '\0', device_config_str.size) != NULL) {
        printf("Invalid configuration string length or embedded NUL\r\n");
        reset_all();
    }
    device_config_str.data[device_config_str.size] = '\0';
}

void device_config_write_to_nv() {
    validate_and_terminate_config();
    printf("Writing config to nv: %s\r\n", device_config_str.data);
    hal_nvm_status_t st = 0;

    printf("Size: %d\r\n", (int)sizeof(device_config_str));
    st = hal_nvm_write(NV_ITEM_DEVICE_CONFIG, sizeof(device_config_str),
                       (uint8_t *)&device_config_str);

    if (st != HAL_NVM_SUCCESS) {
        printf(
            "Failed to write DEVICE_CONFIG_DATA to NV, status: %d. (bytes: %d)\r\n",
            st, device_config_str.size);
    } else {
        printf("success!\r\n");
    }
}

void device_config_read_from_nv() {
    hal_nvm_status_t st = 0;

    st = hal_nvm_read(NV_ITEM_DEVICE_CONFIG, sizeof(device_config_str),
                      (uint8_t *)&device_config_str);

    if (st != HAL_NVM_SUCCESS) {
        printf("Failed to read NV_ITEM_DEVICE_CONFIG, using default config "
               "instead, status: %d. (bytes: %d)\r\n",
               st, device_config_str.size);
        if (sizeof(default_config_data) > sizeof(device_config_str.data)) {
            printf("Default configuration is too long\r\n");
            reset_all();
        }
        memcpy(device_config_str.data, default_config_data,
               sizeof(default_config_data));
        device_config_str.size = strlen((const char *)default_config_data);
    }

    validate_and_terminate_config();
    printf("Using config: %d chars from\r\n%s\r\n", device_config_str.size,
           device_config_str.data);
}
