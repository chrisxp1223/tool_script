import datetime

class DQMapGenerator:
    def __init__(self):
        self.includes = []
        
    def add_include(self, include_name, is_system=True):
        """Add an include directive"""
        if is_system:
            self.includes.append(f'#include <{include_name}>')
        else:
            self.includes.append(f'#include "{include_name}"')
    
    def generate_dq_pins(self):
        """Generate DQ PIN enum definition"""
        lines = []
        
        for channel in ['MA', 'MB', 'MC', 'MD']:
            # Generate for subchannel 0 (values 0x00-0x0F)
            line = '  '
            for i in range(8):
                line += f'{channel}0_DQ_{i:02d} = 0x{i:02X}, '
            lines.append(line.rstrip())
            
            line = '  '
            for i in range(8, 16):
                line += f'{channel}0_DQ_{i:02d} = 0x{i:02X}, '
            lines.append(line.rstrip())
            
            # Generate for subchannel 1 (values 0x10-0x1F)
            line = '  '
            for i in range(8):
                line += f'{channel}1_DQ_{i:02d} = 0x{i+16:02X}, '
            lines.append(line.rstrip())
            
            line = '  '
            for i in range(8, 16):
                line += f'{channel}1_DQ_{i:02d} = 0x{i+16:02X}, '
            lines.append(line.rstrip())
        
        return '\n'.join(lines)

    def generate_dram_dq_pin_struct(self):
        """Generate DRAM_DQ_PIN struct definition"""
        lines = ['typedef struct DRAM_DQ_PIN {']
        
        # Generate DQ pins for A
        line = '  '
        for i in range(8):
            line += f'UINT8 DQ_{i:02d}_A; '
        lines.append(line.rstrip())
        
        line = '  '
        for i in range(8, 16):
            line += f'UINT8 DQ_{i:02d}_A; '
        lines.append(line.rstrip())
        
        # Generate DQ pins for B
        line = '  '
        for i in range(8):
            line += f'UINT8 DQ_{i:02d}_B; '
        lines.append(line.rstrip())
        
        line = '  '
        for i in range(8, 16):
            line += f'UINT8 DQ_{i:02d}_B; '
        lines.append(line.rstrip())
        
        lines.append('} DRAM_DQ_PIN;')
        return '\n'.join(lines)

    def generate_board_dram_map_struct(self):
        """Generate BOARD_DRAM_DQ_PIN_MAP struct definition"""
        return 'typedef struct BOARD_DRAM_DQ_PIN_MAP {\n' + \
               '  DRAM_DQ_PIN DRAM_MD;\n' + \
               '  DRAM_DQ_PIN DRAM_MC;\n' + \
               '  DRAM_DQ_PIN DRAM_MB;\n' + \
               '  DRAM_DQ_PIN DRAM_MA;\n' + \
               '} BOARD_DRAM_DQ_PIN_MAP;'
    
    def generate(self, filename):
        """Generate the complete header file"""
        guard_name = f'{filename.upper().replace(".", "_")}_H'
        
        header = [
            '/**',
            f' * @file {filename}',
            f' * @brief Auto-generated header file',
            f' * @generated {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            ' */',
            '',
            f'#ifndef {guard_name}',
            f'#define {guard_name}',
            ''
        ]
        
        # Add includes
        if self.includes:
            header.extend(self.includes)
            header.append('')
        
        # Add DQ pins enum
        header.append('typedef enum APU_DQ_PIN {')
        header.append(self.generate_dq_pins())
        header.append('} APU_DQ_PIN;')
        header.append('')
        
        # Add DRAM_DQ_PIN struct
        header.append(self.generate_dram_dq_pin_struct())
        header.append('')
        
        # Add BOARD_DRAM_DQ_PIN_MAP struct
        header.append(self.generate_board_dram_map_struct())
        header.append('')
        
        # Close guard
        header.extend(['', f'#endif /* {guard_name} */'])
        
        return '\n'.join(header)


def main():
    # Create a new instance of the generator
    generator = DQMapGenerator()

    # Add system includes
    generator.add_include('MyPorting.h', False)
    generator.add_include('APCB.h', False)
    generator.add_include('ApcbCustomizedDefinitions.h', False)
    generator.add_include('ApcbCustomizedBoardDefinitions.h', False)

    # Generate and save the header file
    header_content = generator.generate('dqmap.h')
    
    # Save to file
    with open('dqmap.h', 'w') as f:
        f.write(header_content)

if __name__ == '__main__':
    main()