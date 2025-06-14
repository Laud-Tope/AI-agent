import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Import our custom components
from agent.file_processor import FileProcessor
from agent.ai_analyzer import AIAnalyzer
from agent.organizer import FileOrganizer

class FileAgentHandler(FileSystemEventHandler):
    """Handles file system events and processes new files"""
    
    def __init__(self):
        self.processor = FileProcessor()
        self.analyzer = AIAnalyzer()
        self.organizer = FileOrganizer()
        print("🤖 AI File Agent initialized and ready!")
    
    def on_created(self, event):
        """Called when a new file is created in the monitored folder"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        print(f"\n📁 New file detected: {Path(file_path).name}")
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        self.process_file(file_path)
    
    def process_file(self, file_path: str):
        """Process a single file through the entire pipeline"""
        print(f"\n🔄 Processing: {Path(file_path).name}")
        
        # Step 1: Check if we can process this file type
        if not self.processor.can_process(file_path):
            print(f"⚠️  Unsupported file type: {Path(file_path).suffix}")
            return
        
        # Step 2: Extract content from file
        print("📖 Extracting content...")
        file_data = self.processor.extract_content(file_path)
        
        if 'error' in file_data:
            print(f"❌ Failed to process file: {file_data['error']}")
            return
        
        # Step 3: Analyze content with AI
        print("🧠 Analyzing with AI...")
        analysis = self.analyzer.analyze_content(file_data)
        
        # Step 4: Organize file based on analysis
        print("📂 Organizing file...")
        organization_result = self.organizer.organize_file(file_data, analysis)
        
        # Step 5: Show results
        if organization_result.get('status') == 'success':
            print(f"✅ File processed successfully!")
            print(f"   Category: {analysis.get('category', 'unknown')}")
            print(f"   Summary: {analysis.get('summary', 'No summary available')}")
            print(f"   Location: {organization_result['new_path']}")
        else:
            print(f"❌ Failed to organize file: {organization_result.get('error', 'Unknown error')}")
    
    def process_existing_files(self, input_dir: str):
        """Process all existing files in the input directory"""
        input_path = Path(input_dir)
        files = [f for f in input_path.iterdir() if f.is_file()]
        
        if not files:
            print(f"📂 No files found in {input_dir}")
            return
        
        print(f"🔍 Found {len(files)} existing files to process")
        
        for file_path in files:
            self.process_file(str(file_path))
            time.sleep(0.5)  # Small delay between files
        
        # Generate report after processing all files
        print("\n📊 Generating summary report...")
        report = self.organizer.generate_report()
        print(report)


class AIFileAgent:
    """Main AI File Processing Agent"""
    
    def __init__(self, input_dir: str = "input"):
        self.input_dir = Path(input_dir)
        self.input_dir.mkdir(exist_ok=True)
        
        self.handler = FileAgentHandler()
        self.observer = Observer()
    
    def start_monitoring(self):
        """Start monitoring the input directory for new files"""
        print(f"👀 Starting to monitor: {self.input_dir.absolute()}")
        
        # Process any existing files first
        self.handler.process_existing_files(str(self.input_dir))
        
        # Set up file monitoring
        self.observer.schedule(self.handler, str(self.input_dir), recursive=False)
        self.observer.start()
        
        print(f"\n🚀 Agent is now running!")
        print(f"   Drop files into: {self.input_dir.absolute()}")
        print(f"   Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping agent...")
            self.observer.stop()
        
        self.observer.join()
        print("👋 Agent stopped successfully!")
    
    def process_single_file(self, file_path: str):
        """Process a single file without monitoring"""
        print(f"🔄 Processing single file: {file_path}")
        self.handler.process_file(file_path)
        
        # Generate report
        report = self.handler.organizer.generate_report()
        print(report)


# Example usage and testing functions
def run_agent():
    """Main function to run the agent"""
    agent = AIFileAgent()
    agent.start_monitoring()

def test_single_file(file_path: str):
    """Test the agent with a single file"""
    agent = AIFileAgent()
    agent.process_single_file(file_path)

def create_test_files():
    """Create some test files for demonstration"""
    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)
    
    # Create test text file
    with open(input_dir / "test_document.txt", "w") as f:
        f.write("""
        Meeting Notes - Project Alpha
        Date: 2024-06-05
        
        Key Discussion Points:
        - Budget approval needed for Q3
        - Team expansion plans
        - New client requirements
        
        Action Items:
        - Follow up with finance team
        - Schedule client meeting
        - Review project timeline
        """)
    
    # Create test data file
    import pandas as pd
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Department': ['Engineering', 'Marketing', 'Sales'],
        'Salary': [85000, 65000, 70000]
    }
    df = pd.DataFrame(data)
    df.to_csv(input_dir / "employee_data.csv", index=False)
    
    print("✅ Test files created in input/ directory")

if __name__ == "__main__":
    print("🤖 AI File Processing Agent")
    print("=" * 40)
    
    # Check if API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Please add your API key to the .env file")
        print("   Example: OPENAI_API_KEY=your_key_here")
        exit(1)
    
    choice = input("""
Choose an option:
1. Run agent (monitor input folder)
2. Create test files
3. Process single file
4. Exit

Enter choice (1-4): """).strip()
    
    if choice == "1":
        run_agent()
    elif choice == "2":
        create_test_files()
        print("Now you can run option 1 to process them!")
    elif choice == "3":
        file_path = input("Enter file path: ").strip()
        if os.path.exists(file_path):
            test_single_file(file_path)
        else:
            print("File not found!")
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("Invalid choice!")