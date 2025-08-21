#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sigil AceChecker Plugin for validating EPUB files using Ace by DAISY

This plugin integrates with Ace by DAISY (https://github.com/daisy/ace)
which is developed and maintained by the DAISY under the MIT License.

Author: [jun-hyung-joon]
License: MIT License
Version: 1.0.0
"""

import sys
import os
import tempfile
import subprocess
import json
import zipfile
import urllib.request
import urllib.error
from typing import Optional, Tuple, Dict, Any, List

# Constants
TIMEOUT_SUBPROCESS = 10  # seconds for subprocess calls
TIMEOUT_ACE_CHECK = 300  # seconds for Ace check (5 minutes)
TIMEOUT_VERSION_CHECK = 10  # seconds for version check
NPM_REGISTRY_URL = 'https://registry.npmjs.org/@daisy/ace/latest'
USER_AGENT = 'Sigil-Ace-Plugin/1.0'

# Output string constants
ICONS = {
    'start': '🔍',
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'book': '📖',
    'package': '📦',
    'tool': '🔧',
    'document': '📄',
    'chart': '📊',
    'folder': '📁',
    'location': '📍',
    'link': '🔗',
    'code': '💻',
    'info': '📖',
    'list': '📋',
    'clock': '⏰',
    'party': '🎉'
}

MESSAGES = {
    'start': "Ace by DAISY accessibility check started",
    'complete': "Accessibility check completed",
    'ace_check': "Checking Ace by DAISY installation...",
    'ace_found': "Ace by DAISY found: {}",
    'ace_not_found': "Ace by DAISY is not installed.",
    'epub_prepare': "Preparing current EPUB file...",
    'ace_running': "Running Ace by DAISY accessibility check...",
    'ace_complete': "Ace by DAISY processing completed",
    'ace_warning': "Ace by DAISY warning: {}",
    'epub_created': "EPUB created successfully (size: {:,} bytes)",
    'error_occurred': "Error occurred: {}",
    'results_title': "Accessibility Check Results",
    'no_violations': "Congratulations! No accessibility violations found!",
    'violations_found': "Accessibility issues found ({} items):",
    'passed_files': "Files that passed ({} items):",
    'missing_metadata': "Missing accessibility metadata ({} items):",
    'version_check': "Checking for Ace by DAISY updates...",
    'version_latest': "You have the latest version of Ace by DAISY",
    'version_outdated': "New version available: {} (you have: {})",
    'version_update_cmd': "To update, run: npm install -g @daisy/ace",
    'version_check_failed': "Could not check for updates"
}

def run(bk: Any) -> int:
    """Sigil plugin main function - Run Ace by DAISY check immediately"""
    try:
        print("=" * 60)
        print(f"{ICONS['start']} {MESSAGES['start']}")
        print("=" * 60)
        
        # Check Ace by DAISY installation and find path (only once)
        ace_info = find_and_verify_ace()
        if not ace_info:
            return -1
        
        ace_path, ace_version = ace_info
        
        # Check for updates
        check_ace_updates(ace_version)
        
        # Create EPUB file
        print(f"{ICONS['book']} {MESSAGES['epub_prepare']}")
        epub_path = create_temp_epub(bk)
        
        try:
            # Run Ace by DAISY check
            print(f"{ICONS['start']} {MESSAGES['ace_running']}")
            result = run_ace_check(epub_path, ace_path)
            
            # Display results
            display_results(result)
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(epub_path)
            except (OSError, FileNotFoundError):
                pass
        
        print("=" * 60)
        print(f"{ICONS['success']} {MESSAGES['complete']}")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"{ICONS['error']} {MESSAGES['error_occurred'].format(str(e))}")
        return -1

def find_and_verify_ace() -> Optional[Tuple[str, str]]:
    """Check Ace by DAISY installation and return path/version info"""
    print(f"{ICONS['tool']} {MESSAGES['ace_check']}")
    
    ace_info = find_ace_executable()
    
    if ace_info:
        ace_path, ace_version = ace_info
        print(f"{ICONS['success']} {MESSAGES['ace_found'].format(ace_version)}")
        return ace_info
    
    print(f"{ICONS['error']} {MESSAGES['ace_not_found']}")
    return None

def find_ace_executable() -> Optional[Tuple[str, str]]:
    """Find Ace by DAISY executable path and verify version (cross-platform)"""
    import platform
    
    system = platform.system().lower()
    
    if system == 'windows':
        possible_paths = [
            'ace.cmd',
            'ace',
            os.path.expanduser('~\\AppData\\Roaming\\npm\\ace.cmd'),
            os.path.expanduser('~\\AppData\\Roaming\\npm\\ace'),
            'C:\\Program Files\\nodejs\\ace.cmd',
            'C:\\Program Files (x86)\\nodejs\\ace.cmd',
        ]
    elif system == 'darwin':  # macOS
        possible_paths = [
            'ace',
            '/usr/local/bin/ace',
            '/opt/homebrew/bin/ace',  # Apple Silicon Homebrew
            os.path.expanduser('~/node_modules/.bin/ace'),
            os.path.expanduser('~/.npm-global/bin/ace'),
            '/usr/local/lib/node_modules/@daisy/ace/bin/ace.js',
            '/opt/homebrew/lib/node_modules/@daisy/ace/bin/ace.js',  # Apple Silicon
            '/usr/local/lib/node_modules/.bin/ace',
        ]
    else:  # Linux
        possible_paths = [
            'ace',
            '/usr/local/bin/ace',
            '/usr/bin/ace',
            os.path.expanduser('~/.npm-global/bin/ace'),
            os.path.expanduser('~/node_modules/.bin/ace'),
        ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, '--version'], 
                                   capture_output=True, text=True, timeout=TIMEOUT_SUBPROCESS)
            if result.returncode == 0:
                version = result.stdout.strip()
                return (path, version)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError, FileNotFoundError):
            continue
    return None

def check_ace_updates(current_version: str) -> None:
    """Check for Ace by DAISY updates and display message if available"""
    try:
        print(f"{ICONS['tool']} {MESSAGES['version_check']}")
        
        # Get latest version from npm registry
        url = NPM_REGISTRY_URL
        req = urllib.request.Request(url)
        req.add_header('User-Agent', USER_AGENT)
        
        with urllib.request.urlopen(req, timeout=TIMEOUT_VERSION_CHECK) as response:
            data = json.loads(response.read().decode('utf-8'))
            latest_version = data.get('version', '')
            
            if latest_version:
                # Clean version strings for comparison
                current_clean = clean_version(current_version)
                latest_clean = clean_version(latest_version)
                
                if compare_versions(latest_clean, current_clean) > 0:
                    print(f"{ICONS['warning']} {MESSAGES['version_outdated'].format(latest_version, current_version)}")
                    print(f"   {MESSAGES['version_update_cmd']}")
                    print()
                else:
                    print(f"{ICONS['success']} {MESSAGES['version_latest']}")
            else:
                print(f"{ICONS['warning']} {MESSAGES['version_check_failed']}")
                
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError) as e:
        print(f"{ICONS['warning']} {MESSAGES['version_check_failed']}: {str(e)}")

def clean_version(version_str: str) -> str:
    """Clean version string to extract just the version numbers"""
    import re
    # Extract version pattern like "1.3.7" from strings like "v1.3.7" or "1.3.7-alpha"
    match = re.search(r'(\d+\.\d+\.\d+)', version_str)
    return match.group(1) if match else version_str.strip()

def compare_versions(version1: str, version2: str) -> int:
    """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal"""
    def version_tuple(v):
        return tuple(map(int, v.split('.')))
    
    try:
        v1_tuple = version_tuple(version1)
        v2_tuple = version_tuple(version2)
        
        if v1_tuple > v2_tuple:
            return 1
        elif v1_tuple < v2_tuple:
            return -1
        else:
            return 0
    except (ValueError, AttributeError):
        return 0  # If comparison fails, assume equal

def extract_filename_from_assertion(assertion: Dict[str, Any]) -> str:
    """Helper function to extract filename from assertion"""
    filename = ''
    if '_file_url' in assertion:
        file_url = assertion['_file_url']
        filename = os.path.basename(file_url)
    elif 'earl:testSubject' in assertion and 'url' in assertion['earl:testSubject']:
        file_url = assertion['earl:testSubject']['url']
        filename = os.path.basename(file_url)
    return filename

def create_temp_epub(bk: Any) -> str:
    """Create temporary EPUB from current book"""
    with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
        epub_path = temp_file.name
    
    try:
        with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # mimetype file (uncompressed)
            zipf.writestr('mimetype', 'application/epub+zip', zipfile.ZIP_STORED)
            
            # META-INF/container.xml
            container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
            zipf.writestr('META-INF/container.xml', container_xml)
            
            # OPF file
            opf_data = bk.get_opf()
            zipf.writestr('OEBPS/content.opf', opf_data)
            
            # NCX file (if exists)
            try:
                ncx_data = bk.get_ncx()
                if ncx_data:
                    zipf.writestr('OEBPS/toc.ncx', ncx_data)
            except (AttributeError, OSError):
                pass
            
            # All manifest files
            for (file_id, href, mime_type) in bk.manifest_iter():
                try:
                    file_data = bk.readfile(file_id)
                    if isinstance(file_data, str):
                        file_data = file_data.encode('utf-8')
                    zipf.writestr(f'OEBPS/{href}', file_data)
                except (AttributeError, OSError, UnicodeDecodeError) as e:
                    print(f"Failed to add file {href}: {str(e)}")
                    continue
            
            # Other files
            for book_href in bk.other_iter():
                try:
                    if book_href.startswith('META-INF/'):
                        continue  # Already added
                    file_data = bk.readotherfile(book_href)
                    if isinstance(file_data, str):
                        file_data = file_data.encode('utf-8')
                    zipf.writestr(book_href, file_data)
                except (AttributeError, OSError, UnicodeDecodeError) as e:
                    print(f"Failed to add other file {book_href}: {str(e)}")
                    continue
        
        # Verify created file
        file_size = os.path.getsize(epub_path)
        print(f"{ICONS['package']} {MESSAGES['epub_created'].format(file_size)}")
        
        return epub_path
        
    except (OSError, zipfile.BadZipFile, UnicodeDecodeError) as e:
        try:
            os.unlink(epub_path)
        except (OSError, FileNotFoundError):
            pass
        raise Exception(f"Failed to create EPUB file: {str(e)}")

def run_ace_check(epub_path: str, ace_executable: str) -> Dict[str, Any]:
    """Run Ace by DAISY CLI"""
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Run Ace by DAISY
            cmd = [
                ace_executable, epub_path, 
                '--outdir', temp_dir,
                '--force'
            ]
            
            result = subprocess.run(cmd, 
                                   capture_output=True, 
                                   text=True, 
                                   timeout=TIMEOUT_ACE_CHECK)  # 5 minute timeout
            
            # Log Ace by DAISY output (simple)
            if result.stdout:
                print(f"{ICONS['document']} {MESSAGES['ace_complete']}")
            
            if result.stderr and result.returncode != 0:
                print(f"{ICONS['warning']} {MESSAGES['ace_warning'].format(result.stderr)}")
            
            # Read JSON result file
            json_path = os.path.join(temp_dir, 'report.json')
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                raise Exception("Could not find check result file.")
                
        except subprocess.TimeoutExpired:
            raise Exception("Check timeout exceeded (5 minutes)")
        except (subprocess.SubprocessError, OSError, json.JSONDecodeError, FileNotFoundError) as e:
            raise Exception(f"Error running Ace by DAISY: {str(e)}")

def display_results(ace_result: Dict[str, Any]) -> None:
    """Display check results"""
    print()
    print(f"{ICONS['chart']} {MESSAGES['results_title']}")
    print("=" * 60)
    
    # Collect actual check items
    all_checks = []
    top_level_assertions = ace_result.get('assertions', [])
    
    # Process each top-level assertion
    for top_assertion in top_level_assertions:
        nested_assertions = top_assertion.get('assertions', [])
        
        if nested_assertions:  # Has nested check items
            # Get parent file info
            top_subject = top_assertion.get('earl:testSubject', {})
            
            # Add file info to each nested assertion
            for nested in nested_assertions:
                # Add file info directly
                if top_subject and 'url' in top_subject:
                    nested['_file_url'] = top_subject['url']
                all_checks.append(nested)
        else:  # No nested items (mostly pass)
            all_checks.append(top_assertion)
    
    # Classify results
    violations = []
    passes = []
    
    for check in all_checks:
        outcome = check.get('earl:result', {}).get('earl:outcome', '')
        if outcome == 'fail':
            violations.append(check)
        elif outcome == 'pass':
            passes.append(check)
    
    total_checks = len(all_checks)
    
    # Summary info
    print(f"Total check items: {total_checks}")
    print(f"Passed items: {len(passes)} {ICONS['success']}")
    print(f"Failed items: {len(violations)} {ICONS['error']}")
    print()
    
    # Check target info
    test_subject = ace_result.get('earl:testSubject', {})
    if isinstance(test_subject, dict):
        metadata = test_subject.get('metadata', {})
        title = metadata.get('dc:title', '')
        if title:
            print(f"{ICONS['book']} Check target: {title}")
        
        epub_version = test_subject.get('epubVersion', '')
        if epub_version:
            print(f"{ICONS['book']} EPUB version: {epub_version}")
    
    # Check completion time
    date = ace_result.get('dct:date', '')
    if date:
        print(f"{ICONS['clock']} Check time: {date}")
    
    print()
    
    # Display failed items in detail
    if violations:
        print(f"{ICONS['error']} {MESSAGES['violations_found'].format(len(violations))}")
        print("-" * 60)
        
        for i, violation in enumerate(violations, 1):
            test_info = violation.get('earl:test', {})
            result_info = violation.get('earl:result', {})
            
            # Basic info
            title = test_info.get('dct:title', 'Unknown issue')
            test_description = test_info.get('dct:description', '')
            result_description = result_info.get('dct:description', '')
            impact = test_info.get('earl:impact', '')
            
            print(f"{i}. {title}")
            if impact:
                impact_icon = "🔴" if impact == "serious" else "🟡" if impact == "moderate" else "🟢"
                print(f"   Severity: {impact_icon} {impact}")
            
            if result_description:
                print(f"   Issue: {result_description}")
            
            if test_description:
                print(f"   Description: {test_description}")
            
            # File info display
            filename = extract_filename_from_assertion(violation)
            if filename:
                print(f"   {ICONS['folder']} File: {filename}")
            
            # Location info
            if 'earl:pointer' in violation:
                pointer = violation['earl:pointer']
                if isinstance(pointer, dict):
                    if 'css' in pointer:
                        css_selectors = pointer['css']
                        if isinstance(css_selectors, list) and css_selectors:
                            print(f"   {ICONS['location']} Location: {' > '.join(css_selectors)}")
                    if 'cfi' in pointer:
                        cfi = pointer['cfi']
                        if isinstance(cfi, list) and cfi and cfi != ["/"]:
                            print(f"   {ICONS['link']} CFI: {' '.join(cfi)}")
            
            # HTML code snippet
            if 'html' in violation:
                html_snippet = violation['html']
                if html_snippet:
                    print(f"   {ICONS['code']} HTML: {html_snippet}")
            
            # Help link
            help_info = test_info.get('help', {})
            if isinstance(help_info, dict) and 'url' in help_info:
                help_url = help_info['url']
                print(f"   {ICONS['info']} Solution: {help_url}")
            
            # WCAG standards
            ruleset_tags = test_info.get('rulesetTags', [])
            if ruleset_tags:
                wcag_tags = [tag for tag in ruleset_tags if 'wcag' in tag.lower()]
                if wcag_tags:
                    print(f"   {ICONS['list']} WCAG standards: {', '.join(wcag_tags)}")
            
            print()
    else:
        print(f"{ICONS['party']} {MESSAGES['no_violations']}")
        print()
    
    # Files that passed
    if passes:
        print(f"{ICONS['success']} {MESSAGES['passed_files'].format(len(passes))}")
        file_names = set()
        for pass_item in passes:
            filename = extract_filename_from_assertion(pass_item)
            if filename:
                file_names.add(filename)
        
        for filename in sorted(file_names):
            print(f"   • {filename}")
        print()
    
    # Missing accessibility metadata
    a11y_metadata = ace_result.get('a11y-metadata', {})
    missing_metadata = a11y_metadata.get('missing', [])
    if missing_metadata:
        print(f"{ICONS['list']} {MESSAGES['missing_metadata'].format(len(missing_metadata))}")
        for metadata in missing_metadata:
            print(f"   • {metadata}")
        print()

def main() -> int:
    print("This script should only be run as a Sigil plugin.")
    return -1

if __name__ == "__main__":
    sys.exit(main())