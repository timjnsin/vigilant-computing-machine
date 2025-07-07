# run_model.py

import argparse
from pathlib import Path
import yaml

# Import the core components of our financial modeling package
from distillery_model.core.model import DistilleryModel
from distillery_model.outputs.excel import create_excel_report
# from distillery_model.outputs.pdf import create_pdf_summary      # Placeholder for future PDF output
# from distillery_model.outputs.dashboard import run_dashboard  # Placeholder for future web dashboard

def load_assumptions(config_path: Path) -> tuple[dict, list[dict]]:
    """
    Loads model assumptions from the specified YAML configuration file.

    Args:
        config_path (Path): The path to the assumptions.yaml file.

    Returns:
        tuple[dict, list[dict]]: A tuple containing the dictionary of constant
                                 assumptions and a list of scenario dictionaries.
    """
    print(f"Loading assumptions from: {config_path}")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    constants = config.get('constants', {})
    scenarios = config.get('scenarios', [])
    
    if not scenarios:
        raise ValueError("No scenarios found in the configuration file.")
        
    return constants, scenarios

def main():
    """
    Main entry point for the financial model generation script.
    Orchestrates loading data, running the model for a selected scenario,
    and generating all specified output files.
    """
    # --- 1. Setup Argument Parser ---
    parser = argparse.ArgumentParser(
        description="Run The Brogue Distillery financial model for a specific scenario."
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="Base Case",
        choices=["Base Case", "Upside Case", "Downside Case"],
        help="The name of the scenario to run. Defaults to 'Base Case'."
    )
    args = parser.parse_args()

    # --- 2. Load Assumptions from YAML ---
    config_path = Path(__file__).parent / "distillery_model" / "config" / "assumptions.yaml"
    constants, scenarios = load_assumptions(config_path)
    
    # --- 3. Select the Correct Scenario ---
    try:
        selected_scenario = next(s for s in scenarios if s['name'] == args.scenario)
    except StopIteration:
        print(f"Error: Scenario '{args.scenario}' not found in configuration file.")
        return

    print(f"\n--- Running Model for: [{selected_scenario['name']}] ---")

    # --- 4. Instantiate and Run the Core Model ---
    print("Initializing calculation engine...")
    model = DistilleryModel(scenario_data=selected_scenario, constants=constants)
    
    print("Performing financial calculations...")
    results = model.run_model()
    print("Calculations complete.")

    # --- 5. Generate Outputs ---
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True) # Ensure the output directory exists
    
    scenario_filename_slug = selected_scenario['name'].replace(' ', '_')
    
    # Generate Excel Report
    excel_filename = output_dir / f"Brogue_Distillery_Model_{scenario_filename_slug}.xlsx"
    print(f"Generating Excel report: {excel_filename.name}...")
    create_excel_report(results, selected_scenario, constants, str(excel_filename))

    # # Generate PDF Summary (future implementation)
    # pdf_filename = output_dir / f"Brogue_Distillery_Summary_{scenario_filename_slug}.pdf"
    # print(f"Generating PDF summary: {pdf_filename.name}...")
    # create_pdf_summary(results, str(pdf_filename))

    # # Launch Web Dashboard (future implementation)
    # if args.dashboard:
    #     print("Launching interactive web dashboard...")
    #     run_dashboard(results)

    print("\n--- Model Run Successfully Completed ---")
    print(f"All output files are located in the '{output_dir.name}' directory.")

if __name__ == "__main__":
    main()
