# This script extends bb-runtimes to define the stm32f407 target

import sys
import os
import pathlib

# Add bb-runtimes to the search path so that we can include and extend it
sys.path.append(str(pathlib.Path(__file__).parent / "bb-runtimes"))

import arm.cortexm
import build_rts
from support import add_source_search_path


class ArmV7MArch_Patched(arm.cortexm.ArmV7MArch):
    def __init__(self):
        super(ArmV7MArch_Patched, self).__init__()
        # Use our own patched version of s-bbbosu.adb which has a fix that is
        # not yet merged upstream (the fix ensures that Interrupt_Wrapper is
        # called with interrupts disabled to avoid a race condition with
        # nested interrupts).
        # See: https://forum.ada-lang.io/t/a-bug-in-stm32-bareboard-runtimes/2168
        self.remove_source("s-bbbosu.adb")
        self.add_gnarl_sources("stm32f407_src/s-bbbosu.adb")


class Stm32F407(arm.cortexm.CortexM4F):
    @property
    def name(self):
        return "stm32f407"

    @property
    def parent(self):
        return ArmV7MArch_Patched

    @property
    def use_semihosting_io(self):
        return True

    @property
    def loaders(self):
        return ("ROM", "RAM")

    @property
    def system_ads(self):
        return {
            "light": "system-xi-arm.ads",
            "light-tasking": "system-xi-cortexm4-sfp.ads",
            "embedded": "system-xi-cortexm4-full.ads",
        }

    def __init__(self):
        super(Stm32F407, self).__init__()

        self.add_linker_script("stm32f407_src/ld/common-RAM.ld")
        self.add_linker_script("stm32f407_src/ld/common-ROM.ld")

        # Common source files
        self.add_gnat_sources(
            "bb-runtimes/arm/stm32/start-common.S",
            "bb-runtimes/arm/stm32/start-ram.S",
            "bb-runtimes/arm/stm32/start-rom.S",
            "stm32f407_src/setup_pll.ads",
            "stm32f407_src/setup_pll.adb",
            "stm32f407_src/s-bbpara.ads",
            "stm32f407_src/s-bbbopa.ads",
            "stm32f407_src/s-bbmcpa.ads",
            "stm32f407_src/svd/handler.S",
            "stm32f407_src/svd/i-stm32.ads",
            "stm32f407_src/svd/i-stm32-flash.ads",
            "stm32f407_src/svd/i-stm32-pwr.ads",
            "stm32f407_src/svd/i-stm32-rcc.ads",
        )

        self.add_gnarl_sources(
            "stm32f407_src/svd/a-intnam-F407.ads",
        )


def build_configs(target):
    if target == "stm32f407":
        return Stm32F407()
    else:
        assert False, "unexpected target: %s" % target

def patch_bb_runtimes():
    """Patch some parts of bb-runtimes to use our own targets and data"""
    add_source_search_path(os.path.dirname(__file__))

    build_rts.build_configs = build_configs

if __name__ == "__main__":
    patch_bb_runtimes()
    build_rts.main()