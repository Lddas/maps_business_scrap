"""
Data Exporter - Exports business data to Excel/CSV
"""
import pandas as pd
from datetime import datetime


class DataExporter:
    def __init__(self):
        self.df = None
    
    def create_dataframe(self, businesses):
        """Create a pandas DataFrame from business data"""
        if not businesses:
            print("No businesses to export")
            return None
        
        self.df = pd.DataFrame(businesses)
        return self.df
    
    def export_to_excel(self, filename=None):
        """Export data to Excel file"""
        if self.df is None or self.df.empty:
            print("No data to export")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"businesses_without_websites_{timestamp}.xlsx"
        
        self.df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Data exported to {filename}")
        return filename
    
    def export_to_csv(self, filename=None):
        """Export data to CSV file"""
        if self.df is None or self.df.empty:
            print("No data to export")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"businesses_without_websites_{timestamp}.csv"
        
        self.df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")
        return filename
    
    def get_dataframe(self):
        """Get the current DataFrame"""
        return self.df

