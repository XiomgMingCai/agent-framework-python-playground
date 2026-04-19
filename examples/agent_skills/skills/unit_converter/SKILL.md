---
name: unit-converter
description: Convert between common units. Use when asked to convert miles, kilometers, pounds, or kilograms.
---
# Unit Converter Skill

Use this skill when the user asks to convert between units.

## Supported Conversions

| From | To | Factor |
|------|----|--------|
| miles | kilometers | 1.60934 |
| kilometers | miles | 0.621371 |
| pounds | kilograms | 0.453592 |
| kilograms | pounds | 2.20462 |

## Usage

Use the `convert` script with `value` and `factor` to perform the conversion.