# This code is taken from the GitHub repository jakobowsky/InvoiceAutomator
# This code is used to generate invoices using the data from the csv file.
# The csv file contains data for several invoices.
# The data includes (a.o.) company name and logo, (due) data, descriptions and notes.
# The following API is used for the invoices: https://invoice-generator.com

import csv
import os
from typing import List

# First several libraries have to be imported/installed.
import requests
import typer


# 'requests' is a library which makes it easier to make HTTP requests to API's
# 'typing' is a library for creating command line interfaces
# It is used in the end of this script to generate and save the invoices.
# Other libraries are just basic (common used) libraries.
# For example, the csv library is used to read the csv file with input data for the invoices.

# The following shows how we describe objects, what classes we use within the csv file.
# This  is the input for the invoice generator.
class Invoice:
    from_who: str
    to_who: str
    logo: str
    number: str
    date: str
    due_date: str
    items: List[dict]
    notes: str


# The following reads the data from the csv and converts it into a list that is used for each invoice.
class CSVParser:
    def __init__(self, csv_name: str) -> None:
        self.field_names = (
            'from_who',
            'to_who',
            'logo',
            'number',
            'date',
            'due_date',
            'items',
            'notes'
        )
        self.csv_name = csv_name

    # First open the csv file, take the first row of the file (start with header == 0 ) for the first invoice.
    # Continue for each new invoice with a new row of input date (+=1).

    def get_array_of_invoices(self) -> List[Invoice]:
        with open(self.csv_name, 'r') as f:
            reader = csv.DictReader(f, self.field_names)
            header = 0
            current_csv = []
            for row in reader:
                if header == 0:
                    header += 1
                    continue
                invoice_obj = Invoice(**row)
                # evaluate the string with object items, giving the dictionaries
                invoice_obj.items = eval(invoice_obj.items)
                # connect each csv line to the invoice generator
                current_csv.append(invoice_obj)
        # returning the array of the corresponding invoice
        return current_csv


# The ApiConnector allows us for each invoice to collect the data from the csv and send it to the invoice generator
class ApiConnector:
    def __init__(self) -> None:
        self.headers = {"Content-Type": "application/json"}
        self.url = 'https://invoice-generator.com'
        self.invoices_directory = f"{os.path.dirname(os.path.abspath(__file__))}/{'invoices'}"

    # Here we read the invoice from the csv file. use the data as input and obtain the invoice with this date
    def connect_to_api_and_save_invoice_pdf(self, invoice: Invoice) -> None:
        invoice_parsed = {
            'from': invoice.from_who,
            'to': invoice.to_who,
            'logo': invoice.logo,
            'number': invoice.number,
            'date': invoice.date,
            'due_date': invoice.due_date,
            'items': invoice.items,
            'notes': invoice.notes
        }
        r = requests.post(self.url, json=invoice_parsed, headers=self.headers)
        if r.status_code == 200 or r.status_code == 201:
            pdf = r.content
            self.save_invoice_to_pdf(pdf, invoice)
            typer.echo("File Saved")  # We ise typer to save the invoice with the data from the csv as pdf
        else:
            typer.echo("Fail :", r.text)

    # Save the invoices that are generated as pdfs within a seperate file in the directory
    # Each invoicee is given a number, so e.g. the first invoice is called 1_invoice.pdf, the second one 2_invoice.pdf etc.
    def save_invoice_to_pdf(self, pdf_content: str, invoice: Invoice) -> None:
        invoice_name = f"{invoice.number}_invoice.pdf"
        invoice_path = f"{self.invoices_directory}/{invoice_name}"
        with open(invoice_path, 'wb') as f:
            typer.echo(f"Generate invoice for {invoice_name}")
            f.write(pdf_content)


# Reading from the csv file and using the application programming interface
def main(csv_name: str = typer.Argument('invoices.csv')):
    typer.echo(f"Running script with - {csv_name}")
    csv_reader = CSVParser(csv_name)
    array_of_invoices = csv_reader.get_array_of_invoices()
    api = ApiConnector()
    for invoice in array_of_invoices:
        api.connect_to_api_and_save_invoice_pdf(invoice)


# Printing multiple invoices using typer (i.e. automatically create and save the pdfs)

if __name__ == "__main__":
    typer.run(main)

# Within the working directory (pythonProject) a file 'invoices' is needed to store the pdf's, otherwise warnings will be shown.
# Otherwise, savee_invoice_to_pdf will not work and the code will return error messages.
# The input for the invoices (the logo as well as the brand, data, prices etc) can be changed in the csv file.
