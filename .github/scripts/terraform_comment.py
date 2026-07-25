#!/usr/bin/env python3
"""
Terraform PR Comment Generator for GitHub Actions
Pure Python - No JavaScript/NPM dependencies
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

def parse_plan_summary(plan_output: str) -> Dict:
    """Parse Terraform plan output for summary statistics."""
    result = {
        'add': 0,
        'change': 0,
        'destroy': 0,
        'resources_add': [],
        'resources_change': [],
        'resources_destroy': []
    }

    # Extract resource counts
    add_match = re.search(r'Plan:\s*(\d+)\s+to add', plan_output)
    change_match = re.search(r'(\d+)\s+to change', plan_output)
    destroy_match = re.search(r'(\d+)\s+to destroy', plan_output)

    if add_match:
        result['add'] = int(add_match.group(1))
    if change_match:
        result['change'] = int(change_match.group(1))
    if destroy_match:
        result['destroy'] = int(destroy_match.group(1))

    # Extract resource actions
    for line in plan_output.split('\n'):
        if '# ' in line and 'will be' in line:
            if 'created' in line:
                resource = re.search(r'#\s+(\S+)', line)
                if resource:
                    result['resources_add'].append(resource.group(1))
            elif 'updated' in line:
                resource = re.search(r'#\s+(\S+)', line)
                if resource:
                    result['resources_change'].append(resource.group(1))
            elif 'destroyed' in line:
                resource = re.search(r'#\s+(\S+)', line)
                if resource:
                    result['resources_destroy'].append(resource.group(1))

    return result

def create_plan_comment(plan_output: str, plan_error: str, output_file: str = None) -> str:
    """Create a formatted comment for PR with Terraform plan results."""
    comment = "## Terraform Plan Results\n\n"

    if plan_error and not plan_output:
        comment += "### ❌ Plan Failed\n\n"
        comment += "```\n" + plan_error[:5000] + "\n```"
        if output_file:
            with open(output_file, 'w') as f:
                f.write(comment)
        return comment

    # Parse the plan
    stats = parse_plan_summary(plan_output)

    # Summary section
    total_changes = stats['add'] + stats['change'] + stats['destroy']

    if total_changes > 0:
        comment += "### 📊 Summary\n\n"
        comment += "| Action | Count |\n"
        comment += "|--------|-------|\n"
        if stats['add'] > 0:
            comment += f"| ➕ Add | {stats['add']} |\n"
        if stats['change'] > 0:
            comment += f"| 🔄 Change | {stats['change']} |\n"
        if stats['destroy'] > 0:
            comment += f"| 🗑️ Destroy | {stats['destroy']} |\n"
    else:
        comment += "✅ No changes detected\n"
        comment += "\n*Infrastructure is already up to date.*"
        if output_file:
            with open(output_file, 'w') as f:
                f.write(comment)
        return comment

    # Resource details
    if stats['resources_add']:
        comment += "\n### ➕ Resources to Create\n\n"
        for resource in stats['resources_add'][:10]:
            comment += f"- `{resource}`\n"
        if len(stats['resources_add']) > 10:
            comment += f"\n*... and {len(stats['resources_add']) - 10} more*\n"

    if stats['resources_change']:
        comment += "\n### 🔄 Resources to Update\n\n"
        for resource in stats['resources_change'][:10]:
            comment += f"- `{resource}`\n"
        if len(stats['resources_change']) > 10:
            comment += f"\n*... and {len(stats['resources_change']) - 10} more*\n"

    if stats['resources_destroy']:
        comment += "\n### 🗑️ Resources to Destroy\n\n"
        for resource in stats['resources_destroy'][:10]:
            comment += f"- `{resource}`\n"
        if len(stats['resources_destroy']) > 10:
            comment += f"\n*... and {len(stats['resources_destroy']) - 10} more*\n"

    # Full plan output (collapsed if too long)
    if len(plan_output) > 5000:
        comment += "\n\n<details>\n<summary>📄 View Full Plan Output</summary>\n\n"
        comment += "```hcl\n" + plan_output[:5000] + "\n```\n"
        comment += "\n*Plan output truncated to 5000 characters*\n"
        comment += "\n</details>\n"
    else:
        comment += "\n### 📄 Full Plan Output\n\n"
        comment += "```hcl\n" + plan_output + "\n```"

    comment += "\n\n---\n"
    comment += "*This plan shows what would be deployed if this PR were merged.*"

    if output_file:
        with open(output_file, 'w') as f:
            f.write(comment)

    return comment

def create_deployment_comment(lambda_names: Dict, lambda_arns: Dict,
                             environment: str, version: str,
                             output_file: str = None) -> str:
    """Create a comment for successful deployment."""
    comment = "## ✅ Deployment Successful!\n\n"
    comment += f"**Environment:** {environment}\n"
    comment += f"**Version:** {version}\n\n"

    if lambda_names:
        comment += "### Deployed Lambdas\n\n"
        comment += "| Function Name | ARN |\n"
        comment += "|--------------|-----|\n"

        for key in lambda_names:
            comment += f"| {lambda_names[key]} | {lambda_arns.get(key, 'N/A')} |\n"
    else:
        comment += "No Lambda functions were deployed.\n"

    comment += "\n---\n"
    comment += f"*Deployed at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*"

    if output_file:
        with open(output_file, 'w') as f:
            f.write(comment)

    return comment

def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python terraform_comment.py [plan|deploy] [output_file]")
        print("  plan   - Generate comment from Terraform plan output")
        print("  deploy - Generate deployment success comment")
        print("  output_file - Optional file to write comment to")
        sys.exit(1)

    action = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if action == "plan":
        plan_output = os.environ.get('PLAN_OUTPUT', '')
        plan_error = os.environ.get('PLAN_ERROR', '')
        comment = create_plan_comment(plan_output, plan_error, output_file)
        if not output_file:
            print(comment)

    elif action == "deploy":
        lambda_names_str = os.environ.get('LAMBDA_NAMES', '{}')
        lambda_arns_str = os.environ.get('LAMBDA_ARNS', '{}')

        try:
            lambda_names = json.loads(lambda_names_str) if lambda_names_str else {}
            lambda_arns = json.loads(lambda_arns_str) if lambda_arns_str else {}
        except json.JSONDecodeError:
            lambda_names = {}
            lambda_arns = {}

        environment = os.environ.get('ENVIRONMENT', 'production')
        version = os.environ.get('LAMBDA_VERSION', 'unknown')

        comment = create_deployment_comment(lambda_names, lambda_arns, environment, version, output_file)
        if not output_file:
            print(comment)

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
