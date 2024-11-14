# Import the CHeaderGenerator from the local file
from header_generator import DQMapGenerator

def main():
    # Create a new instance of the generator
    generator = DQMapGenerator()

    # Add system includes
    generator.add_include('MyPorting.h')
    generator.add_include('APCB.h')
    generator.add_include('ApcbCustomizedDefinitions.h')
    generator.add_include('ApcbCustomizedBoardDefinitions.h')

    # Generate and save the header file
    header_content = generator.generate('dqmap.h')
    
    # Save to file
    with open('dqmap.h', 'w') as f:
        f.write(header_content)

if __name__ == '__main__':
    main()