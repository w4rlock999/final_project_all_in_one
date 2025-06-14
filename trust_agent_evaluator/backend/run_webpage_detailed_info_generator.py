import json
import os
from webpage_detailed_info_generator import WebpageDetailedInfoGenerator

def main():
    # Define input and output paths
    input_path = "./data/output/detailed_graph_with_jb.json"
    process_output_path = "./data/output/process_info.json"
    component_output_path = "./data/output/component_info.json"
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(process_output_path), exist_ok=True)
    
    try:
        # Read the detailed graph JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            detailed_graph_with_jb = json.load(f)
        
        # Initialize the generator
        generator = WebpageDetailedInfoGenerator(detailed_graph_with_jb)
        
        # Generate and save process info
        process_info = generator.generate_process_info()
        generator.save_process_info(process_output_path)
        print(f"Successfully generated process info at: {process_output_path}")
        
        # Generate and save component info
        component_info = generator.generate_component_info()
        generator.save_component_info(component_output_path)
        print(f"Successfully generated component info at: {component_output_path}")
        
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {input_path}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main() 