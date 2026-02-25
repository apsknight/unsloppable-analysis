#!/usr/bin/env python3
"""
Static site generator for Unsloppable Analysis.
Reads markdown files and generates HTML pages.
"""

import os
import re
import json
from pathlib import Path
from string import Template

ANALYSIS_DIR = Path("/Users/apsknight/Documents/primary-vault/Investing/unsloppable_results")
TEMPLATE_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "docs"

CLASSIFICATION_MAP = {
    "Unsloppable + Beneficiary": ("bg-green-100 text-green-800", "Unsloppable\n+Beneficiary", "UnsloppableBeneficiary"),
    "Unsloppable + High Transition Risk": ("bg-blue-100 text-blue-800", "High\nTransition", "UnsloppableHighTransitionRisk"),
    "Unsloppable + Macro Exposed": ("bg-yellow-100 text-yellow-800", "Macro\nExposed", "UnsloppableMacroExposed"),
    "Sloppable + Beneficiary": ("bg-red-100 text-red-800", "Sloppable\n+Beneficiary", "SloppableBeneficiary"),
    "Sloppable + Clankerable": ("bg-red-200 text-red-900", "Sloppable\n+Clankerable", "SloppableClankerable"),
}


def get_score_class(score):
    """Get color class based on vulnerability score."""
    try:
        score = int(score)
        if score <= 3:
            return "text-green-600"
        elif score <= 6:
            return "text-yellow-600"
        else:
            return "text-red-600"
    except (ValueError, TypeError):
        return "text-gray-600"


def get_macro_risk_class(risk):
    """Get color class based on macro risk."""
    risk_lower = risk.lower()
    if "low" in risk_lower:
        return "text-green-600"
    elif "medium" in risk_lower:
        return "text-yellow-600"
    else:
        return "text-red-600"


def parse_markdown(file_path):
    """Parse a markdown file and extract structured data."""
    content = file_path.read_text(encoding='utf-8')
    
    data = {
        "ticker": "",
        "company_name": "",
        "ai_score": "",
        "robotics_score": "",
        "ai_beneficiary": "",
        "robotics_beneficiary": "",
        "value_chain": "",
        "final_classification": "TEMP_MARKER",
        "macro_risk": "",
        "moat_sources": "",
        "key_insights": [],
        "q1": "", "q2": "", "q3": "", "q4": "",
        "q5": "", "q6": "", "q7": "", "q8": "",
    }
    
    lines = content.split('\n')
    
    # Extract title
    for line in lines:
        match = re.match(r'#\s+([^(]+)\s+\(([^)]+)\)', line.strip())
        if match:
            data["company_name"] = match.group(1).strip()
            data["ticker"] = match.group(2).strip()
            break
    
    # Parse sections
    current_section = None
    current_value = []
    
    for line in lines:
        line = line.strip()
        
        # Skip header lines
        if not line or line.startswith('#'):
            # Save current section before switching
            if current_section and current_value:
                if current_section == "key_insights":
                    data[current_section] = [l.lstrip('- ') for l in current_value if l.strip()]
                else:
                    print(f"    Saving {current_section}: {current_value[:2]}")
                    data[current_section] = " ".join(current_value).strip()
            current_section = None
            current_value = []
            continue
        
        # Parse key-value pairs in Overview
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip().rstrip('*').strip('-* ')
            value = value.strip()
            
            if key == "AI Software Vulnerability Score":
                match = re.search(r'(\d+)', value)
                if match:
                    data["ai_score"] = match.group(1)
            elif key == "Robotics Vulnerability Score":
                match = re.search(r'(\d+)', value)
                if match:
                    data["robotics_score"] = match.group(1)
            elif key == "AI Beneficiary":
                data["ai_beneficiary"] = value
            elif key == "Robotics Beneficiary":
                data["robotics_beneficiary"] = value
            elif key == "Value Chain Position":
                data["value_chain"] = value
            elif key == "Final Classification":
                data["final_classification"] = value
            elif key == "Macro Contagion Risk":
                data["macro_risk"] = value
    
    # Also parse Moat Sources and Key Insights sections separately
    in_moat = False
    in_insights = False
    moat_lines = []
    insight_lines = []
    
    for line in lines:
        line = line.strip()
        if line == "## Moat Sources":
            in_moat = True
            in_insights = False
        elif line == "## Key Insights":
            in_moat = False
            in_insights = True
        elif line.startswith('## Pressure'):
            in_moat = False
            in_insights = False
        elif in_moat and line:
            moat_lines.append(line)
        elif in_insights and line.startswith('- '):
            insight_lines.append(line[2:])
    
    data["moat_sources"] = " ".join(moat_lines).strip()
    data["key_insights"] = insight_lines
    
    return data


def generate_index(companies):
    """Generate the index.html page."""
    template = (TEMPLATE_DIR / "index.html").read_text()
    
    stats = {
        "UnsloppableBeneficiary": 0,
        "UnsloppableHighTransitionRisk": 0,
        "UnsloppableMacroExposed": 0,
        "SloppableBeneficiary": 0,
        "SloppableClankerable": 0,
    }
    
    company_data = []
    for c in companies:
        classification = c.get("final_classification", "")
        badge_class, short, css_class = CLASSIFICATION_MAP.get(classification, ("bg-gray-100 text-gray-800", "Unknown", ""))
        
        stats[css_class] = stats.get(css_class, 0) + 1
        
        company_data.append({
            "Ticker": c.get("ticker", ""),
            "CompanyName": c.get("company_name", c.get("ticker", "")),
            "ClassificationShort": short.replace("\n", " "),
            "ClassificationClass": css_class,
            "BadgeClass": badge_class,
            "AIScore": c.get("ai_score", "N/A"),
            "RoboticsScore": c.get("robotics_score", "N/A"),
            "MoatSources": (c.get("moat_sources", "") or "")[:100] + "...",
        })
    
    result = template
    
    for key, value in stats.items():
        result = result.replace("{{." + key + "}}", str(value))
    
    companies_html = ""
    for c in company_data:
        companies_html += f'''
            <a href="/unsloppable-analysis/{c["Ticker"]}.html" 
               class="block bg-white p-6 rounded-lg shadow hover:shadow-md transition classification-{c["ClassificationClass"]}">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-lg font-bold">{c["Ticker"]}</h3>
                        <p class="text-sm text-gray-600">{c["CompanyName"]}</p>
                    </div>
                    <span class="px-2 py-1 text-xs font-medium rounded {c["BadgeClass"]}">
                        {c["ClassificationShort"].replace(chr(10), " ")}
                    </span>
                </div>
                <div class="mt-4 grid grid-cols-2 gap-2 text-sm">
                    <div>
                        <span class="text-gray-500">AI Vuln:</span>
                        <span class="font-medium">{c["AIScore"]}/10</span>
                    </div>
                    <div>
                        <span class="text-gray-500">Robot Vuln:</span>
                        <span class="font-medium">{c["RoboticsScore"]}/10</span>
                    </div>
                </div>
                <div class="mt-2 text-xs text-gray-500">
                    {c["MoatSources"]}
                </div>
            </a>
'''
    
    result = re.sub(r'\{\{range \.\w+\}\}.*?\{\{end\}\}', '', result, flags=re.DOTALL)
    result = result.replace('id="companies"', 'id="companies">' + companies_html)
    
    return result


def generate_company_page(data):
    """Generate a company detail page."""
    template = (TEMPLATE_DIR / "company.html").read_text()
    
    classification = data.get("final_classification", "")
    badge_class, _, _ = CLASSIFICATION_MAP.get(classification, ("bg-gray-100 text-gray-800", "Unknown", ""))
    
    subs = {
        "Ticker": data.get("ticker", ""),
        "CompanyName": data.get("company_name", data.get("ticker", "")),
        "FinalClassification": data.get("final_classification", "Unknown"),
        "BadgeClass": badge_class,
        "AIScore": data.get("ai_score", "N/A"),
        "RoboticsScore": data.get("robotics_score", "N/A"),
        "AIScoreClass": get_score_class(data.get("ai_score", 0)),
        "RoboticsScoreClass": get_score_class(data.get("robotics_score", 0)),
        "ValueChain": data.get("value_chain", "Unknown"),
        "MacroRisk": data.get("macro_risk", "Unknown").split(' - ')[0],
        "MacroRiskClass": get_macro_risk_class(data.get("macro_risk", "")),
        "AIBeneficiary": data.get("ai_beneficiary", "N/A"),
        "RoboticsBeneficiary": data.get("robotics_beneficiary", "N/A"),
        "MoatSources": data.get("moat_sources", "N/A"),
        "KeyInsights": data.get("key_insights", []),
        "Q1": data.get("q1", "N/A"),
        "Q2": data.get("q2", "N/A"),
        "Q3": data.get("q3", "N/A"),
        "Q4": data.get("q4", "N/A"),
        "Q5": data.get("q5", "N/A"),
        "Q6": data.get("q6", "N/A"),
        "Q7": data.get("q7", "N/A"),
        "Q8": data.get("q8", "N/A"),
    }
    
    result = template
    for key, value in subs.items():
        if isinstance(value, list):
            continue
        result = result.replace(f"{{.{key}}}", str(value))
    
    insights_html = ""
    for insight in data.get("key_insights", []):
        insights_html += f"<li>{insight}</li>\n"
    result = result.replace('{{range .KeyInsights}}', '').replace('{{end}}', '').replace('<li>{{.}}</li>', insights_html)
    
    return result


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    companies = []
    for md_file in ANALYSIS_DIR.glob("*.md"):
        print(f"Processing {md_file.name}...")
        data = parse_markdown(md_file)
        print(f"  -> final_classification: {repr(data.get('final_classification', 'MISSING')[:30])}")
        data = parse_markdown(md_file)
        if data.get("ticker"):
            companies.append(data)
            
            html = generate_company_page(data)
            (OUTPUT_DIR / f"{data['ticker']}.html").write_text(html)
    
    print(f"Generated {len(companies)} company pages")
    
    index_html = generate_index(companies)
    (OUTPUT_DIR / "index.html").write_text(index_html)
    print(f"Generated index.html")
    
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("To preview locally: cd docs && python -m http.server 8000")


if __name__ == "__main__":
    main()
