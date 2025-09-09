#!/usr/bin/env python3
"""
PDF Documentation Generator for Climatee Project
Converts the HTML documentation to PDF format for easy distribution
"""

import os
import sys
from pathlib import Path

def generate_pdf_documentation():
    """Generate PDF documentation from HTML file"""
    
    print("🌍 Climatee Documentation Generator")
    print("=" * 50)
    
    # Check if required packages are available
    try:
        import weasyprint
        print("✅ WeasyPrint found - PDF generation available")
    except ImportError:
        print("❌ WeasyPrint not found. Installing...")
        os.system("pip install weasyprint")
        try:
            import weasyprint
            print("✅ WeasyPrint installed successfully")
        except ImportError:
            print("❌ Failed to install WeasyPrint. Using alternative method...")
            return generate_pdf_alternative()
    
    # File paths
    html_file = Path("CLIMATEE_DOCUMENTATION.html")
    pdf_file = Path("CLIMATEE_DOCUMENTATION.pdf")
    
    if not html_file.exists():
        print(f"❌ HTML documentation file not found: {html_file}")
        return False
    
    try:
        print(f"📄 Converting {html_file} to PDF...")
        
        # Generate PDF from HTML
        weasyprint.HTML(filename=str(html_file)).write_pdf(str(pdf_file))
        
        print(f"✅ PDF documentation generated: {pdf_file}")
        print(f"📊 File size: {pdf_file.stat().st_size / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return generate_pdf_alternative()

def generate_pdf_alternative():
    """Alternative PDF generation method using browser automation"""
    
    print("\n🔄 Trying alternative PDF generation method...")
    
    try:
        # Try using playwright for PDF generation
        os.system("pip install playwright")
        os.system("playwright install chromium")
        
        from playwright.sync_api import sync_playwright
        
        html_file = Path("CLIMATEE_DOCUMENTATION.html").absolute()
        pdf_file = Path("CLIMATEE_DOCUMENTATION.pdf")
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{html_file}")
            page.pdf(path=str(pdf_file), format="A4", print_background=True)
            browser.close()
        
        print(f"✅ PDF generated using Playwright: {pdf_file}")
        return True
        
    except Exception as e:
        print(f"❌ Alternative method failed: {e}")
        print("\n💡 Manual PDF Generation Instructions:")
        print("1. Open CLIMATEE_DOCUMENTATION.html in your browser")
        print("2. Press Ctrl+P (or Cmd+P on Mac)")
        print("3. Select 'Save as PDF' as destination")
        print("4. Choose 'More settings' and enable 'Background graphics'")
        print("5. Click 'Save' to generate PDF")
        return False

def create_documentation_package():
    """Create a complete documentation package"""
    
    print("\n📦 Creating documentation package...")
    
    # Create docs directory
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Copy files to docs directory
    files_to_copy = [
        "README.md",
        "CLIMATEE_PROJECT_DOCUMENTATION.md",
        "CLIMATEE_DOCUMENTATION.html"
    ]
    
    for file_name in files_to_copy:
        source = Path(file_name)
        if source.exists():
            destination = docs_dir / file_name
            destination.write_text(source.read_text(), encoding='utf-8')
            print(f"✅ Copied {file_name} to docs/")
    
    # Create index file
    index_content = """# Climatee Documentation Package

This package contains comprehensive documentation for the Climatee Climate Data Management System.

## Files Included

1. **README.md** - Quick start guide and project overview
2. **CLIMATEE_PROJECT_DOCUMENTATION.md** - Complete technical documentation
3. **CLIMATEE_DOCUMENTATION.html** - Interactive HTML documentation
4. **CLIMATEE_DOCUMENTATION.pdf** - PDF version (if generated)

## How to Use

- **For quick overview**: Start with README.md
- **For complete reference**: Open CLIMATEE_DOCUMENTATION.html in your browser
- **For offline reading**: Use the PDF version
- **For technical details**: Refer to CLIMATEE_PROJECT_DOCUMENTATION.md

## System Requirements

- Python 3.8+
- Django 5.1
- Modern web browser for HTML documentation

## Support

For questions or support, contact: support@climatee.org

---
Generated on: """ + str(Path().cwd()) + """
Documentation Version: 2.0.0
"""
    
    (docs_dir / "INDEX.md").write_text(index_content)
    print("✅ Created documentation index")
    
    print(f"\n📁 Documentation package created in: {docs_dir.absolute()}")
    return docs_dir

def main():
    """Main function to generate all documentation"""
    
    print("Starting Climatee documentation generation...")
    
    # Generate PDF
    pdf_success = generate_pdf_documentation()
    
    # Create documentation package
    docs_dir = create_documentation_package()
    
    # Copy PDF if generated
    pdf_file = Path("CLIMATEE_DOCUMENTATION.pdf")
    if pdf_success and pdf_file.exists():
        (docs_dir / "CLIMATEE_DOCUMENTATION.pdf").write_bytes(pdf_file.read_bytes())
        print("✅ PDF added to documentation package")
    
    print("\n🎉 Documentation generation complete!")
    print(f"📂 All files available in: {docs_dir.absolute()}")
    
    # Show summary
    print("\n📋 Documentation Summary:")
    print("- README.md: Project overview and quick start")
    print("- CLIMATEE_DOCUMENTATION.html: Interactive documentation")
    print("- CLIMATEE_PROJECT_DOCUMENTATION.md: Technical reference")
    if pdf_success:
        print("- CLIMATEE_DOCUMENTATION.pdf: Printable PDF version")
    
    print("\n🌍 Climatee - Climate Data Management System")
    print("Documentation ready for distribution!")

if __name__ == "__main__":
    main()