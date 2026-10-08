# Third-party notices

## Application firmware and integrations

Firmware source, host simulation/test harness, device definitions, integration generators, and development helpers are derived from **romasku/tuya-zigbee-switch**, release source commit `ec57f81b89e7755c4a8833cc6cb081ba3cdda227`:

https://github.com/romasku/tuya-zigbee-switch/tree/ec57f81b89e7755c4a8833cc6cb081ba3cdda227

The exact upstream license is retained in [LICENSE](LICENSE). The focused application change is recorded in `patches/hold-off.patch`; deployment documentation and the target-only integration wrapper are additions in this repository.

## Telink Zigbee SDK

Compiled firmware incorporates SDK objects and libraries from **Telink Semiconductor**, Zigbee SDK tag **V3.7.2.0**:

https://github.com/telink-semi/telink_zigbee_sdk/tree/V3.7.2.0

The SDK is downloaded during the build rather than vendored as source here. Its applicable license and file inventory are retained in:

- [Telink SDK Apache License 2.0](licenses/TELINK-APACHE-2.0.txt), copied verbatim from `tl_zigbee_sdk/LICENSE.txt` at that tag.
- [Telink SDK license inventory](licenses/TELINK-SDK-license-list.txt), copied verbatim from the tag's `license_list.txt`.

The file inventory identifies the covered SDK files as `TELINK_APACHE`; the source files carry their own Telink copyright notices. The application build consumes the SDK without source modifications. Redistribute these notices and the SDK license together with any compiled firmware bundle. Do not describe the complete linked binary as exclusively covered by the application license.

## Build tools and Python dependencies

The TC32 GCC toolchain is downloaded separately from the URL in `src/telink/tools.mk`, verified by the checksum in `PROVENANCE.json`, and not distributed by this repository. GCC, its runtime libraries, and other toolchain components carry their own notices/licenses in the toolchain distribution. Docker base packages and dependencies listed in `requirements.txt` also retain their respective licenses. The application license does not relicense those dependencies.
