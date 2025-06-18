import PyPDF2
import re
from datetime import datetime
import json

class ElectricityBillParser:
    def _init_(self):
        self.bill_data = {}
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None
    
    def parse_bill_details(self, text):
        """Parse electricity bill details from extracted text"""
        if not text:
            return None
        
        # Initialize bill data dictionary
        bill_data = {
            'kwh_consumed': None,
            'sanctioned_load': None,
            'power_factor': 0,
            'bill_date': None,
            'due_date': None,
            'bill_number': None,
            'penalty': None,
            'payable_amount': None,
            'consumer_number': None,
            'consumer_name': None,
            'current_reading': None,
            'previous_reading': None,
            'current_bill': None,
            'previous_outstanding': None,
            'energy_charges': None,
            'fixed_charges': None,
            'taxes': None,
        }
        
        # Extract Units Consumed (kWh)
        kwh_patterns = [
            r'Units\s+Consumed\s+(\d+)',
            r'Units Consumed\s*:?\s*(\d+)',
            r'kWh Consumed\s*:?\s*(\d+)'
        ]
        for pattern in kwh_patterns:
            kwh_match = re.search(pattern, text, re.IGNORECASE)
            if kwh_match:
                bill_data['kwh_consumed'] = int(kwh_match.group(1))
                break
        
        # Extract Sanctioned Load
        load_patterns = [
            r'Sanctioned Load:\s*(\d+\.?\d*)\s*KW',
            r'Sanctioned Load\s*:\s*(\d+\.?\d*)',
            r'Load\s*:\s*(\d+\.?\d*)\s*KW'
        ]
        for pattern in load_patterns:
            load_match = re.search(pattern, text, re.IGNORECASE)
            if load_match:
                bill_data['sanctioned_load'] = float(load_match.group(1))
                break
        
        # Extract Bill Date
        bill_date_patterns = [
            r'Bill Date:\s*(\d{2}-[A-Za-z]{3}-\d{4})',
            r'Bill Date\s*:\s*(\d{2}-[A-Za-z]{3,4}-\d{4})',
            r'Bill Date\s*:\s*(\d{2}/\d{2}/\d{4})'
        ]
        for pattern in bill_date_patterns:
            bill_date_match = re.search(pattern, text, re.IGNORECASE)
            if bill_date_match:
                bill_data['bill_date'] = bill_date_match.group(1)
                break
        
        # Extract Due Date
        due_date_patterns = [
            r'Due Date:\s*(\d{2}-[A-Za-z]{3,4}-\d{4})',
            r'Due Date\s*:\s*(\d{2}/\d{2}/\d{4})',
            r'Payment Due Date\s*:\s*(\d{2}-[A-Za-z]{3,4}-\d{4})'
        ]
        for pattern in due_date_patterns:
            due_date_match = re.search(pattern, text, re.IGNORECASE)
            if due_date_match:
                bill_data['due_date'] = due_date_match.group(1)
                break
        
        # Extract Bill Number
        bill_no_patterns = [
            r'Bill No-(\d+)',
            r'Bill No\.\s*(\d+)',
            r'Bill Number\s*:\s*(\d+)',
            r'Bill No\s*:\s*(\d+)'
        ]
        for pattern in bill_no_patterns:
            bill_no_match = re.search(pattern, text, re.IGNORECASE)
            if bill_no_match:
                bill_data['bill_number'] = bill_no_match.group(1)
                break
        
        # Extract Payable Amount - Multiple patterns for better detection
        payable_patterns = [
            r'Payable Amount:\s*(\d+)',
            r'Payable Amount\s*:\s*₹?\s*(\d+(?:,\d+)*)',
            r'Amount Payable\s*:\s*₹?\s*(\d+(?:,\d+)*)',
            r'Total Amount\s*:\s*₹?\s*(\d+(?:,\d+)*)',
            r'Net Amount\s*:\s*₹?\s*(\d+(?:,\d+)*)'
        ]
        for pattern in payable_patterns:
            payable_match = re.search(pattern, text, re.IGNORECASE)
            if payable_match:
                amount_str = payable_match.group(1).replace(',', '')
                bill_data['payable_amount'] = float(amount_str)
                break
        
        # If payable amount not found, try to extract from current bill section
        if bill_data['payable_amount'] is None:
            current_bill_pattern = r'Current Bill\s*\([A-Z+\-]+\)\s*(\d+(?:\.\d+)?)'
            current_bill_match = re.search(current_bill_pattern, text)
            if current_bill_match:
                bill_data['current_bill'] = float(current_bill_match.group(1))
                
                # Look for previous outstanding
                outstanding_pattern = r'Previous Outstanding\s*\([A-Z]\)\s*(-?\d+(?:\.\d+)?)'
                outstanding_match = re.search(outstanding_pattern, text)
                if outstanding_match:
                    bill_data['previous_outstanding'] = float(outstanding_match.group(1))
                    # Calculate payable amount
                    bill_data['payable_amount'] = bill_data['current_bill'] + bill_data['previous_outstanding']
        
        # Extract Consumer Number/Account
        account_patterns = [
            r'Account-\s*(\d+)',
            r'Account\s*:\s*(\d+)',
            r'Consumer No\s*:\s*(\d+)',
            r'A/C No\s*:\s*(\d+)'
        ]
        for pattern in account_patterns:
            account_match = re.search(pattern, text, re.IGNORECASE)
            if account_match:
                bill_data['consumer_number'] = account_match.group(1)
                break
        
        # Extract Consumer Name
        name_patterns = [
            r'^([A-Z\s]+W/O\s[A-Z\s]+)',
            r'Name\s*:\s*([A-Z\s]+)',
            r'Consumer Name\s*:\s*([A-Z\s]+)'
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if name_match:
                bill_data['consumer_name'] = name_match.group(1).strip()
                break
        
        # Extract Current Reading
        current_reading_patterns = [
            r'Current Reading:\s*(\d+)',
            r'Present Reading\s*:\s*(\d+)',
            r'Current\s*:\s*(\d+)'
        ]
        for pattern in current_reading_patterns:
            current_reading_match = re.search(pattern, text, re.IGNORECASE)
            if current_reading_match:
                bill_data['current_reading'] = int(current_reading_match.group(1))
                break
        
        # Extract Previous Reading
        previous_reading_patterns = [
            r'Previous Reading:\s*(\d+)',
            r'Last Reading\s*:\s*(\d+)',
            r'Previous\s*:\s*(\d+)'
        ]
        for pattern in previous_reading_patterns:
            previous_reading_match = re.search(pattern, text, re.IGNORECASE)
            if previous_reading_match:
                bill_data['previous_reading'] = int(previous_reading_match.group(1))
                break
        
        # Extract Energy Charges
        energy_pattern = r'Energy Charges\s*\((?:₹|Rs\.?)?\s*\)\s*(\d+(?:\.\d+)?)'
        energy_match = re.search(energy_pattern, text)
        if energy_match:
            bill_data['energy_charges'] = float(energy_match.group(1))
        
        # Extract Fixed Charges
        fixed_pattern = r'Fixed Charges\s*\((?:₹|Rs\.?)?\s*\)\s*(\d+(?:\.\d+)?)'
        fixed_match = re.search(fixed_pattern, text)
        if fixed_match:
            bill_data['fixed_charges'] = float(fixed_match.group(1))
        
        # Extract Total Taxes
        tax_pattern = r'Total Taxes\s*\((?:₹|Rs\.?)?\s*\)\s*(\d+(?:\.\d+)?)'
        tax_match = re.search(tax_pattern, text)
        if tax_match:
            bill_data['taxes'] = float(tax_match.group(1))
        
        # Check for penalties/surcharges
        penalty_patterns = [
            r'Penalty[:\s]+(\d+\.?\d*)',
            r'Late Fee[:\s]+(\d+\.?\d*)',
            r'Additional Surcharge[:\s\(₹\)]+(\d+\.?\d*)',
            r'Surcharge\s*\([₹\s]\)\s(\d+)'
        ]
        
        penalty_amount = 0.0
        for pattern in penalty_patterns:
            penalty_match = re.search(pattern, text, re.IGNORECASE)
            if penalty_match:
                penalty_amount = float(penalty_match.group(1))
                break
        
        bill_data['penalty'] = penalty_amount
        
        return bill_data
    
    def parse_pdf_bill(self, pdf_path):
        """Main function to parse PDF bill and return extracted data"""
        print(f"Processing PDF: {pdf_path}")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        # Parse bill details
        bill_data = self.parse_bill_details(text)
        
        return bill_data
    
    def parse_text_bill(self, text):
        """Parse bill from raw text (for testing with extracted text)"""
        return self.parse_bill_details(text)
    
    def display_bill_info(self, bill_data):
        """Display formatted bill information"""
        if not bill_data:
            print("No bill data found!")
            return
        
        print("\n" + "="*60)
        print("ELECTRICITY BILL DETAILS")
        print("="*60)
        
        print(f"Consumer Name: {bill_data.get('consumer_name', 'N/A')}")
        print(f"Consumer Number: {bill_data.get('consumer_number', 'N/A')}")
        print(f"Bill Number: {bill_data.get('bill_number', 'N/A')}")
        print(f"Bill Date: {bill_data.get('bill_date', 'N/A')}")
        print(f"Due Date: {bill_data.get('due_date', 'N/A')}")
        print(f"kWh Consumed: {bill_data.get('kwh_consumed', 'N/A')} units")
        print(f"Sanctioned Load: {bill_data.get('sanctioned_load', 'N/A')} KW")
        print(f"Power Factor: {bill_data.get('power_factor', '0')}")
        print(f"Penalty/Surcharge: ₹{bill_data.get('penalty', '0')}")
        print(f"PAYABLE AMOUNT: ₹{bill_data.get('payable_amount', '0')}")
        print("="*90)
    
    def save_to_json(self, bill_data, output_file):
        """Save bill data to JSON file"""
        if bill_data:
            with open(output_file, 'w') as f:
                json.dump(bill_data, f, indent=4)
            print(f"Bill data saved to {output_file}")

# Example usage
def main():
    # Initialize parser
    parser = ElectricityBillParser()
    
    # Path to your PDF file
    pdf_path = "3008683892_04-06-2025.pdf"  # Replace with your PDF path
    
    try:
        # Parse the PDF bill
        bill_data = parser.parse_pdf_bill(pdf_path)
        
        if bill_data:
            # Display the extracted information
            parser.display_bill_info(bill_data)
            
            # Save to JSON file (optional)
            parser.save_to_json(bill_data, "bill_data.json")
            
            # Return specific fields as requested
            requested_fields = {
                'kwh': bill_data.get('kwh_consumed'),
                'sanctioned_load': bill_data.get('sanctioned_load'),
                'power_factor': bill_data.get('power_factor'),
                'bill_date': bill_data.get('bill_date'),
                'due_date': bill_data.get('due_date'),
                'bill_number': bill_data.get('bill_number'),
                'penalty': bill_data.get('penalty'),
                'amount': bill_data.get('payable_amount'),
                'consumer_number': bill_data.get('consumer_number')
            }
            
            print("\nExtracted Fields:")
            print("-" * 50)
            for key, value in requested_fields.items():
                print(f"{key}: {value}")
            
            return requested_fields
        else:
            print("Failed to extract bill data from PDF")
            return None
            
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

# Test with the provided text data
def test_with_sample_data():
    """Test the parser with the sample bill text"""
    sample_text = """RUPINDERJIT KAUR W/O MANMOHAN
SINGH
0.-NEAR UNION BANK / S. D. SCHOOL
. GANDHI ROAD MOGA .
Mobile:74XXXXX047
Email:cbms.XXXXXXXXXXint.co
Circle:FARIDKOT
Division: CITY DIVN MOGA
Sub-Division: SOUTH SUB DIVISION
MOGA(5225)
Category: SAP-SBM-NRS-
GEN
Connection Date:
Sanctioned Load:10.093 KW
Contract Load:0.00 KW
ACD: 5170
Meter Security: 625
Security Cons. Amount: 5170
Interest of Security: 0
Bill Cycle:3
Meter Status:O
Bill Status:OK
Meter Phase:3
Meter Type:E
Bill Date:04-JUN-2025
Current Reading:28627
Previous Reading: 27556
Bill No-500393014879
Meter Make: LINKWELL TELESYSTEMS
PVT LTD
Meter Digits: 5
Meter No.100017172990-9689633
Current Reading Date:04-JUN-
2025
Previous Reading Date:04-May-
2025
Bill days: 31
Account-
3007998329
Payable Amount: 10140
Due Date:
16-Jun-2025
(Cash/Online)
16-Jun-2025
(DD/Cheque)
Units
Consumed
1071
Current Bill
(A+B+C-
D+E+G+H) 10551.00
Previous Outstanding
(F) -414"""
    
    parser = ElectricityBillParser()
    bill_data = parser.parse_text_bill(sample_text)
    
    if bill_data:
        parser.display_bill_info(bill_data)
        return bill_data
    return None

if __name__ == "_main_":
    print("Testing with sample data:")
    test_with_sample_data()
    print("\n" + "="*60)
    print("For PDF parsing, run main() function")