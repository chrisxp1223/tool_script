#!/usr/bin/env python3
"""
SPD Format Converter - Working Version
Converts LPDDR5 SPD data between continuous format and detailed block format.
"""

import re
import sys


def convert_continuous_to_block(input_file: str, output_file: str):
    """Convert continuous SPD format to detailed block format"""
    print(f"Converting {input_file} to block format...")
    
    # Read input file
    with open(input_file, 'r') as f:
        content = f.read()
    
    print(f"File size: {len(content)} characters")
    
    # Extract module name
    module_match = re.search(r'#define\s+([A-Z0-9_]+)_SPD_DATA', content)
    if not module_match:
        raise ValueError("Could not find module name")
    
    module_name = module_match.group(1)
    print(f"Module name: {module_name}")
    
    # Extract SPD data
    spd_pattern = rf'#define\s+{re.escape(module_name)}_SPD_DATA\s*\\(.*?)(?=#endif|\Z)'
    spd_match = re.search(spd_pattern, content, re.DOTALL)
    
    if not spd_match:
        raise ValueError("Could not find SPD data")
    
    spd_content = spd_match.group(1)
    print(f"SPD content length: {len(spd_content)}")
    
    # Extract hex values
    hex_matches = re.findall(r'0x([0-9A-Fa-f]{2})', spd_content)
    print(f"Found {len(hex_matches)} hex values")
    
    if len(hex_matches) != 512:
        raise ValueError(f"Expected 512 bytes, found {len(hex_matches)}")
    
    # Convert to integers
    spd_data = [int(h, 16) for h in hex_matches]
    print(f"Converted to {len(spd_data)} integers")
    
    # Generate output
    output_lines = []
    
    # Header
    output_lines.append("/*******************************************************************************")
    output_lines.append("*")
    output_lines.append("* Copyright (C) 2021-2023 Advanced Micro Devices, Inc. All rights reserved.")
    output_lines.append("*")
    output_lines.append("*******************************************************************************/")
    output_lines.append("")
    output_lines.append(f"#ifndef _APCB_LPDDR5_SPD_{module_name}_H_")
    output_lines.append(f"#define _APCB_LPDDR5_SPD_{module_name}_H_")
    output_lines.append("")
    
    # Generate each block
    block_descriptions = [
        "[0-63] Base Configuration and DRAM Parameters",
        "[64-127] Base Configuration and DRAM Parameters", 
        "[128-191] Module Specific Parameters",
        "[192-255] Module Specific Parameters",
        "[256-319] Hybrid Memory Parameters",
        "[320-383] Module Manufaturing Information",
        "[384-447] End User Programable",
        "[448-511] End User Programable"
    ]
    
    for block_num in range(8):
        start_byte = block_num * 64
        block_data = spd_data[start_byte:start_byte + 64]
        
        print(f"Generating block {block_num}...")
        
        output_lines.append(f"#define {module_name}_BLOCK_{block_num}/*  //< {block_descriptions[block_num]}                                              */ \\")
        
        if block_num == 0:
            # Block 0: Individual bytes with comments
            byte_descriptions = [
                "Number of Serial PD Bytes Written / SPD Device Size  512bytes total but 384bytes used",
                "SPD Rev Version of SPD Documen: 1.1",
                "Key Byte / DRAM Device  See DRAM Configuration Tab",
                "Module Type Not Hybrid // Not Hybrid // Non Dimm solution",
                "SDRAM Density and Banks See DRAM Configuration Tab",
                "SDRAM Addressing See DRAM Configuration Tab",
                "SDRAM Packing Type See DRAM Configuration Tab",
                "SDRAM Optional Features Max Act Window = 4096 * tREF// Max Act Count = Unlimited MAC",
                "SDRAM Thremal and Refresh Options Reserved",
                "Other SDRAM Optional Features PPR Supported 1 row per Bank Groups // Soft PPR not Support",
                "Reserved -- must be coded as 0x00 Reserved",
                "Module Nominal Voltage, VDD VDD2 Voltage Supply (for MR13 OP[7])",
                "Module Organization See DRAM Configuration Tab",
                "Bus Width See DRAM Configuration Tab",
                "Module Thermal Sensor  Thermal sensor not  incorporated onto this assem",
                "Extended module type Reserved",
                "Signal Loading See DRAM Configuration Tab",
                "Timebases MTB = 125ps FTB = 1ps",
                "SDRAM Minimum Cycle time(tckAVGmin) See DRAM Configuration Tab",
                "SDRAM Maximum Cycle time(tckAVGmmax) See DRAM Configuration Tab",
                "CAS Latencies Supported, First Byte CL = 14, 10, 6",
                "CAS Latencies Supported, Second Byte CL = 28, 24, 20",
                "CAS Latencies Supported, Third Byte  CL = 36, 32",
                "CAS Latencies Supported, Fourth Byte Reserved",
                "Minimum CAS Latency Time (t AA min) See DRAM Configuration Tab",
                "Read & Write Latency Set Options Reserved",
                "Minimum RAS to CAS Delay Time (t RCD min) See DRAM Configuration Tab",
                "Minimum Row Precharge Delay Time (t RPab min) See DRAM Configuration Tab",
                "Minimum Row Precharge Delay Time (t RPpb min) See DRAM Configuration Tab",
                "Minimum Refresh Recovery Delay Time (t RFCab min), LSB See DRAM Configuration Tab",
                "Minimum Refresh Recovery Delay Time (t RFCab min), MSB See DRAM Configuration Tab",
                "Minimum Refresh Recovery Delay Time (t RFCpb min), LSB See DRAM Configuration Tab",
                "Minimum Refresh Recovery Delay Time (t RFCpb min), MSB See DRAM Configuration Tab"
            ]
            
            # First 33 bytes individually
            for i in range(33):
                byte_val = block_data[i]
                desc = byte_descriptions[i] if i < len(byte_descriptions) else "Reserved"
                output_lines.append(f"  0x{byte_val:02X},                    /*  //< {start_byte + i} {desc}       */ \\")
            
            # Rest as groups
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [33-36] Reserved -- must be coded as 0x00 Reserved                                            */ \\")
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [37-40] Reserved -- must be coded as 0x00 Reserved                                            */ \\")
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [41-44] Reserved -- must be coded as 0x00 Reserved                                            */ \\")
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [45-48] Reserved -- must be coded as 0x00 Reserved                                            */ \\")
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [49-52] Reserved -- must be coded as 0x00 Reserved                                            */ \\")
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [53-56] Reserved -- must be coded as 0x00 Reserved                                            */ \\")
            output_lines.append("  0x00, 0x00, 0x00,        /*  //< [57-59] Reserved -- must be coded as 0x00 Reserved                                            */ \\")
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [60-63] Connector to SDRAM Bit Mapping Reserved                                               */ \\")
            
        elif block_num == 1:
            # Block 1: Some reserved, some timing data
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [64-67] Connector to SDRAM Bit Mapping Reserved                                               */ \\")
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [68-71] Connector to SDRAM Bit Mapping Reserved                                               */ \\")
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [72-75] Connector to SDRAM Bit Mapping Reserved                                               */ \\")
            output_lines.append("  0x00, 0x00,              /*  //< [76-77] Connector to SDRAM Bit Mapping Reserved                                               */ \\")
            
            # Reserved sections
            for i in range(78, 120, 4):
                output_lines.append(f"  0x00, 0x00, 0x00, 0x00,  /*  //< [{i}-{i+3}] Reserved -- must be coded as 0x00 Reserved                                            */ \\")
            
            output_lines.append("  0x00, 0x00,              /*  //< [118-119] Reserved -- must be coded as 0x00 Reserved                                          */ \\")
            
            # Fine timing offsets (actual data)
            for i in range(56, 60):  # bytes 120-123 in the data
                byte_val = block_data[i]
                timing_descs = [
                    "Fine Offset for Minimum Row Precharge Delay Time (t RPpb min) See DRAM Configuration Tab",
                    "Fine Offset for Minimum Row Precharge Delay Time (t RPab min) See DRAM Configuration Tab",
                    "Fine Offset for Minimum RAS to CAS Delay Time (t RCD min) See DRAM Configuration Tab", 
                    "Fine Offset for Minimum CAS Latency Time (t AA min) See DRAM Configuration Tab"
                ]
                desc = timing_descs[i-56]
                output_lines.append(f"  0x{byte_val:02X},                    /*  //< {120+(i-56)} {desc}  */ \\")
            
            # Cycle time fine offsets
            byte_124 = block_data[60]
            byte_125 = block_data[61]
            output_lines.append(f"  0x{byte_124:02X},                    /*  //< 124 Fine Offset for SDRAM Maximum Cycle Time (t CKAVG max) See DRAM Configuration Tab         */ \\")
            output_lines.append(f"  0x{byte_125:02X},                    /*  //< 125 Fine Offset for SDRAM Minimum Cycle Time (t CKAVG min) See DRAM Configuration Tab         */ \\")
            output_lines.append("  0x00,                    /*  //< 126 CRC for Base Configuration Section, Least Significant Byte Reserved                       */ \\")
            output_lines.append("  0x00,                    /*  //< 127 CRC for Base Configuration Section, Most Significant Byte Reserved                        */ \\")
            
        elif block_num == 5:
            # Block 5: Manufacturing info (actual data)
            mfg_lsb = block_data[0]
            mfg_msb = block_data[1]
            output_lines.append(f"  0x{mfg_lsb:02X},                    /*  //< 320 Module Manufacturer ID Code, LSB Reserved                                                 */ \\")
            output_lines.append(f"  0x{mfg_msb:02X},                    /*  //< 321 Module Manufacturer ID Code, MSB Reserved                                                 */ \\")
            output_lines.append("  0x00,                    /*  //< 322 Module Manufacturing Location Reserved                                                    */ \\")
            output_lines.append("  0x00, 0x00,              /*  //< [323-324] Module Manufacturing Date Reserved                                                  */ \\")
            output_lines.append("  0x00, 0x00, 0x00, 0x00,  /*  //< [325-328] Module Serial Number Reserved                                                       */ \\")
            
            # Part number (actual data)
            for i in range(9, 29):
                if i < len(block_data):
                    byte_val = block_data[i]
                    char_desc = chr(byte_val) if 32 <= byte_val <= 126 else ""
                    output_lines.append(f"  0x{byte_val:02X},                    /*  //< {329+(i-9)} Module Part Number {char_desc}                                                                      */ \\")
            
            output_lines.append("  0x00,                    /*  //< 349 Module Revision Code None                                                                 */ \\")
            
            # DRAM info
            dram_lsb = block_data[30] if len(block_data) > 30 else 0x80
            dram_msb = block_data[31] if len(block_data) > 31 else 0x2C
            dram_step = block_data[32] if len(block_data) > 32 else 0x41
            output_lines.append(f"  0x{dram_lsb:02X},                    /*  //< 350 DRAM Manufacturer ID Code, LSB # continuation codes                                       */ \\")
            output_lines.append(f"  0x{dram_msb:02X},                    /*  //< 351 DRAM Manufacturer ID Code, MSB MCRN                                                       */ \\")
            output_lines.append(f"  0x{dram_step:02X},                    /*  //< 352 DRAM Stepping A-Die                                                                       */ \\")
            
            # Rest reserved
            for i in range(353, 381, 4):
                output_lines.append(f"  0x00, 0x00, 0x00, 0x00,  /*  //< [{i}-{i+3}] Manufacturer's Specific Data Reserved                                               */ \\")
            
            output_lines.append("  0x00,                    /*  //< 381 Manufacturer's Specific Data Reserved                                                     */ \\")
            output_lines.append("  0x00, 0x00,              /*  //< [382-383] Reserved Reserved                                                                   */ \\")
            
        else:
            # Other blocks: mostly reserved or end user programmable
            if block_num in [2, 3]:
                # Module specific
                for i in range(0, 64, 4):
                    byte_start = start_byte + i
                    output_lines.append(f"  0x00, 0x00, 0x00, 0x00,  /*  //< [{byte_start}-{byte_start+3}] Module-Specific Section Reserved                                                    */ \\")
            elif block_num == 4:
                # Hybrid memory
                for i in range(0, 64, 4):
                    byte_start = start_byte + i
                    output_lines.append(f"  0x00, 0x00, 0x00, 0x00,  /*  //< [{byte_start}-{byte_start+3}] Hybrid Memory Architecture Specific Parameters Reserved                             */ \\")
            else:
                # End user programmable (blocks 6-7)
                for i in range(0, 64, 16):
                    hex_line = ", ".join([f"0x{block_data[i+j]:02X}" for j in range(16)])
                    output_lines.append(f"  {hex_line},\\")
        
        output_lines.append("")
    
    # Footer
    output_lines.append(f"#endif  //_APCB_LPDDR5_SPD_{module_name}_H_")
    
    # Write output
    print(f"Writing {len(output_lines)} lines to {output_file}...")
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Successfully converted {input_file} to {output_file}")
    print(f"Module: {module_name}")
    print(f"SPD Data: {len(spd_data)} bytes")


def convert_block_to_continuous(input_file: str, output_file: str):
    """Convert detailed block format to continuous SPD format"""
    print(f"Converting {input_file} to continuous format...")
    
    # Read input file
    with open(input_file, 'r') as f:
        content = f.read()
    
    print(f"File size: {len(content)} characters")
    
    # Extract module name
    module_match = re.search(r'#define\s+([A-Z0-9_]+)_BLOCK_0', content)
    if not module_match:
        # Try alternative pattern
        module_match = re.search(r'_APCB_LPDDR5_SPD_([A-Z0-9_]+)_H_', content)
        if not module_match:
            raise ValueError("Could not find module name in block format file")
    
    module_name = module_match.group(1)
    print(f"Module name: {module_name}")
    
    # Extract data from all 8 blocks
    all_spd_data = []
    
    for block_num in range(8):
        print(f"Processing block {block_num}...")
        block_name = f"{module_name}_BLOCK_{block_num}"
        
        # Find the block definition
        block_pattern = rf'#define\s+{re.escape(block_name)}\s*/\*.*?\*/\s*\\(.*?)(?=#define|\Z)'
        block_match = re.search(block_pattern, content, re.DOTALL)
        
        if not block_match:
            raise ValueError(f"Could not find block {block_num} ({block_name}) in file")
        
        block_content = block_match.group(1)
        
        # Extract hex values from this block
        hex_matches = re.findall(r'0x([0-9A-Fa-f]{2})', block_content)
        
        # Handle blocks that may have extra values due to formatting
        if len(hex_matches) > 64:
            print(f"Block {block_num} has {len(hex_matches)} values, taking first 64")
            hex_matches = hex_matches[:64]
        
        if len(hex_matches) != 64:
            raise ValueError(f"Block {block_num} should contain 64 bytes, found {len(hex_matches)}")
        
        block_data = [int(h, 16) for h in hex_matches]
        all_spd_data.extend(block_data)
    
    if len(all_spd_data) != 512:
        raise ValueError(f"Expected 512 bytes total, found {len(all_spd_data)}")
    
    print(f"Extracted {len(all_spd_data)} bytes from all blocks")
    
    # Generate output
    output_lines = []
    
    # Header
    output_lines.append("/*******************************************************************************")
    output_lines.append("*")
    output_lines.append(" * Copyright (C) 2021-2025 Advanced Micro Devices, Inc. All rights reserved.")
    output_lines.append(" *")
    output_lines.append("*******************************************************************************/")
    output_lines.append("")
    output_lines.append(f"#ifndef _APCB_LPDDR5_SPD_{module_name}_H_")
    output_lines.append(f"#define _APCB_LPDDR5_SPD_{module_name}_H_")
    output_lines.append("")
    
    # Generate continuous SPD data
    output_lines.append(f"#define {module_name}_SPD_DATA  \\")
    
    # Format data as 16 bytes per line
    for i in range(0, 512, 16):
        line_data = all_spd_data[i:i+16]
        hex_values = ", ".join([f"0x{b:02X}" for b in line_data])
        
        if i + 16 < 512:  # Not the last line
            output_lines.append(f"  {hex_values},\\")
        else:  # Last line
            output_lines.append(f"  {hex_values}")
    
    output_lines.append("")
    output_lines.append(f"#endif  //ifndef  _APCB_LPDDR5_SPD_{module_name}_H_")
    
    # Write output
    print(f"Writing {len(output_lines)} lines to {output_file}...")
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Successfully converted {input_file} to {output_file}")
    print(f"Module: {module_name}")
    print(f"SPD Data: {len(all_spd_data)} bytes")


def main():
    """Main function"""
    if len(sys.argv) != 4:
        print("SPD Format Converter")
        print("Usage:")
        print("  python3 spd_converter.py --to-block <continuous.h> <blocks.h>")
        print("  python3 spd_converter.py --to-continuous <blocks.h> <continuous.h>")
        return
    
    command = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    try:
        if command == "--to-block":
            convert_continuous_to_block(input_file, output_file)
        elif command == "--to-continuous":
            convert_block_to_continuous(input_file, output_file)
        else:
            print(f"Unknown command: {command}")
            print("Use --to-block or --to-continuous")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()