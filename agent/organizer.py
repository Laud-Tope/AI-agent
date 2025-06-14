# agent/organizer.py - Moves files and creates reports
import shutil
from pathlib import Path
from datetime import datetime
import json
from typing import Dict

class FileOrganizer:
    """Organizes files based on AI analysis and generates reports"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.setup_directories()
        self.processing_log = []
    
    def setup_directories(self):
        """Create output directory structure"""
        categories = ['documents', 'data', 'reports', 'personal', 'work', 'other']
        
        for category in categories:
            category_dir = self.output_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
        
        # Create reports directory
        (self.output_dir / 'reports').mkdir(exist_ok=True)
    
    def organize_file(self, file_data: Dict, analysis: Dict) -> Dict:
        """Move file to appropriate category folder"""
        source_path = Path(file_data['file_path'])
        category = analysis.get('category', 'other')
        
        # Create destination path
        dest_dir = self.output_dir / category
        dest_path = dest_dir / source_path.name
        
        # Handle duplicate names
        counter = 1
        while dest_path.exists():
            stem = source_path.stem
            suffix = source_path.suffix
            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        
        try:
            # Move the file
            shutil.move(str(source_path), str(dest_path))
            
            result = {
                'original_path': str(source_path),
                'new_path': str(dest_path),
                'category': category,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            # Add to processing log
            self.processing_log.append({
                'file': source_path.name,
                'analysis': analysis,
                'organization': result
            })
            
            print(f"✓ Moved {source_path.name} to {category}/ folder")
            return result
            
        except Exception as e:
            print(f"✗ Failed to move {source_path.name}: {str(e)}")
            return {
                'original_path': str(source_path),
                'error': str(e),
                'status': 'failed'
            }
    
    def generate_report(self) -> str:
        """Generate a summary report of all processed files"""
        if not self.processing_log:
            return "No files processed yet."
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_files': len(self.processing_log),
            'categories': {},
            'files': self.processing_log
        }
        
        # Count files by category
        for entry in self.processing_log:
            category = entry['analysis'].get('category', 'other')
            report['categories'][category] = report['categories'].get(category, 0) + 1
        
        # Save report
        report_path = self.output_dir / 'reports' / f"processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Create human-readable summary
        summary = f"""
FILE PROCESSING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Files Processed: {report['total_files']}

Files by Category:
"""
        for category, count in report['categories'].items():
            summary += f"  {category}: {count} files\n"
        
        summary += f"\nDetailed report saved to: {report_path}"
        
        print("✓ Report generated successfully")
        return summary