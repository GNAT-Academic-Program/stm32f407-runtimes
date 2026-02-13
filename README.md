# STM32F407 Runtimes

This repository generates GNAT bare-metal runtimes for STM32F407 targets.

Supported runtime profiles:
- `light`
- `light-tasking`
- `embedded`

## Using a runtime from Alire

Example using `light-tasking-stm32f407`:

1. Add the crate to your project's `alire.toml`:

```toml
[[depends-on]]
light_tasking_stm32f407 = "*"
```

2. In your project `.gpr`, reference and use the runtime project:

```ada
with "runtime_build.gpr";

project App is
   for Target use runtime_build'Target;
   for Runtime ("Ada") use runtime_build'Runtime ("Ada");

   package Linker is
      for Switches ("Ada") use Runtime_Build.Linker_Switches;
   end Linker;
end App;
```

## Runtime Clock Configuration (important)

Clock setup is controlled by crate configuration variables in your
application's `alire.toml`.

Default behavior is a 168 MHz SYSCLK from HSI through PLL.

For STM32F407 Discovery (8 MHz HSE crystal), a typical configuration is:

```toml
[configuration.values]
# HSE on Discovery board
light_tasking_stm32f407.HSE_Clock_Frequency = 8000000
light_tasking_stm32f407.HSE_Bypass = false

# Use PLL as SYSCLK source
light_tasking_stm32f407.SYSCLK_Src = "PLLCLK"
light_tasking_stm32f407.PLL_Src = "HSE"

# 8 MHz -> (N/M)=336/8 => 336 MHz VCO
light_tasking_stm32f407.PLL_M_Div = 8
light_tasking_stm32f407.PLL_N_Mul = 336

# SYSCLK = VCO / 2 = 168 MHz
light_tasking_stm32f407.PLL_P_Div = "DIV2"

# 48 MHz domain for USB/SDIO/RNG
light_tasking_stm32f407.PLL_Q_Div = 7

# Bus prescalers
light_tasking_stm32f407.AHB_Pre  = "DIV1"
light_tasking_stm32f407.APB1_Pre = "DIV4"
light_tasking_stm32f407.APB2_Pre = "DIV2"
```

## Note about timing accuracy

A timing issue where `delay 1.0` behaved like ~4 seconds was caused by an
incorrect PLLP register encoding in `setup_pll.adb`. This repository now uses
the correct STM32F4 encoding (`00=/2, 01=/4, 10=/6, 11=/8`) consistently.

## Generation templates

The generated crate metadata and examples are based on:
- `templates/alire.toml.in`
- `templates/stm32f407_runtime_config.ads.in`
- `stm32f407_src/setup_pll.adb`

If you regenerate runtimes, these sources carry the fixed behavior.