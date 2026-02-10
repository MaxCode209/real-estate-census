"""
Script to fetch and summarize all available variables from Census 2023 ACS 5-year data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from collections import defaultdict

def fetch_all_variables(year='2023'):
    """Fetch all variable definitions from Census API."""
    url = f"https://api.census.gov/data/{year}/acs/acs5/variables.json"
    
    try:
        print(f"Fetching variables from Census API for year {year}...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        variables = data.get('variables', {})
        
        print(f"Found {len(variables)} total variables")
        return variables
        
    except Exception as e:
        print(f"Error fetching variables: {e}")
        return {}

def categorize_variables(variables):
    """Categorize variables by their prefix/category."""
    categories = defaultdict(list)
    
    # Category mapping based on variable prefixes
    category_map = {
        'B01': 'Age and Sex',
        'B02': 'Race',
        'B03': 'Hispanic Origin',
        'B05': 'Ancestry',
        'B08': 'Commuting (Journey to Work)',
        'B09': 'Unpaid Care',
        'B10': 'Grandparents',
        'B11': 'Household/Family Type',
        'B12': 'Marital Status',
        'B13': 'Fertility',
        'B14': 'School Enrollment',
        'B15': 'Educational Attainment',
        'B16': 'Language Spoken at Home',
        'B17': 'Poverty Status',
        'B18': 'Disability Status',
        'B19': 'Income',
        'B20': 'Earnings',
        'B21': 'Veteran Status',
        'B22': 'Food Stamps/SNAP',
        'B23': 'Employment Status',
        'B24': 'Industry',
        'B25': 'Housing',
        'B26': 'Occupancy',
        'B27': 'Housing Costs',
        'B28': 'Housing Value',
        'B29': 'Housing Tenure',
        'B30': 'Housing Structure',
        'B25': 'Housing Characteristics',  # Overlaps with B25
    }
    
    for var_code, var_info in variables.items():
        if not var_code.startswith('B') or var_code.endswith('M'):  # Skip margin of error variables for now
            continue
            
        # Get first 3 digits for category
        prefix = var_code[:3] if len(var_code) >= 3 else var_code[:2]
        
        # Find category
        category = None
        for cat_prefix, cat_name in category_map.items():
            if var_code.startswith(cat_prefix):
                category = cat_name
                break
        
        if not category:
            # Try 2-digit prefix
            prefix_2 = var_code[:2]
            if prefix_2 == 'B0':
                category = 'Demographics (B01-B09)'
            elif prefix_2 == 'B1':
                category = 'Social Characteristics (B10-B19)'
            elif prefix_2 == 'B2':
                category = 'Economic Characteristics (B20-B29)'
            else:
                category = 'Other'
        
        categories[category].append({
            'code': var_code,
            'label': var_info.get('label', ''),
            'concept': var_info.get('concept', '')
        })
    
    return categories

def print_summary(categories):
    """Print a summarized list of variables by category."""
    print("\n" + "="*80)
    print("CENSUS 2023 ACS 5-YEAR VARIABLES - SUMMARY BY CATEGORY")
    print("="*80)
    
    # Sort categories
    sorted_cats = sorted(categories.items())
    
    for category, vars_list in sorted_cats:
        print(f"\n{category} ({len(vars_list)} variables)")
        print("-" * 80)
        
        # Show first 10 variables as examples
        for var in vars_list[:10]:
            label = var['label'][:60] + '...' if len(var['label']) > 60 else var['label']
            print(f"  {var['code']:12} - {label}")
        
        if len(vars_list) > 10:
            print(f"  ... and {len(vars_list) - 10} more variables")

def create_detailed_summary(categories, output_file):
    """Create a detailed markdown summary file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Census 2023 ACS 5-Year Variables - Complete Summary\n\n")
        f.write(f"**Total Variables:** {sum(len(v) for v in categories.values())}\n\n")
        f.write("---\n\n")
        
        sorted_cats = sorted(categories.items())
        
        for category, vars_list in sorted_cats:
            f.write(f"## {category} ({len(vars_list)} variables)\n\n")
            
            # Group by concept for better organization
            concepts = defaultdict(list)
            for var in vars_list:
                concept = var.get('concept', 'Other')
                concepts[concept].append(var)
            
            for concept, concept_vars in sorted(concepts.items()):
                f.write(f"### {concept}\n\n")
                f.write("| Variable Code | Label |\n")
                f.write("|---------------|-------|\n")
                
                for var in concept_vars[:20]:  # Limit to 20 per concept
                    label = var['label'].replace('|', '\\|')  # Escape pipes
                    f.write(f"| `{var['code']}` | {label} |\n")
                
                if len(concept_vars) > 20:
                    f.write(f"| ... | *{len(concept_vars) - 20} more variables* |\n")
                
                f.write("\n")
            
            f.write("---\n\n")

if __name__ == '__main__':
    print("Fetching Census 2023 ACS 5-Year Variables...")
    variables = fetch_all_variables('2023')
    
    if variables:
        categories = categorize_variables(variables)
        print_summary(categories)
        
        # Create detailed markdown file
        output_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'CENSUS_2023_ALL_VARIABLES.md'
        )
        create_detailed_summary(categories, output_file)
        print(f"\n\nDetailed summary saved to: {output_file}")
    else:
        print("Failed to fetch variables")
