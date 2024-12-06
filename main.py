import requests
from decouple import config
import click
import json
import pandas as pd
import os


# Process the PDF file using the Unstract API and return the output in JSON format
def process_pdf(file):
    # Get the API key from the environment variables
    api_key = config('UNSTRACT_API_KEY')
    # API endpoint
    api_url = 'https://us-central.unstract.com/deployment/api/org_yGJu9w4WIwc5aPW0/PDF_to_Excel/'
    # Headers and payload
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    payload = {'timeout': 300, 'include_metadata': False}
    # Files
    files = [('files', ('file', open(file, 'rb'), 'application/octet-stream'))]
    # Send the request
    response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
    # Return the response
    return response.json()['message']['result'][0]['result']['output']


# Flatten the JSON data
def flatten_json(data):
    # Output dictionary
    out = {}

    # Function to flatten the JSON data
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    # Call the function to flatten the data and return the output
    flatten(data)
    return out


# Define a Click command to process the PDF file
@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output filename.')
@click.option('--file_format', '-f', type=click.Choice(['json', 'xlsx']), default='json', help='Output format (json or xlsx).')
def process_file(input_file, output, file_format):
    # If the output filename is not provided, use the input filename with the specified format
    if not output:
        output = os.path.splitext(input_file)[0] + f'.{file_format}'

    # Process the PDF file
    data = process_pdf(input_file)

    # Write the output to a file in the specified format
    if file_format == 'json':
        write_json(data, output)
    elif file_format == 'xlsx':
        write_xlsx(data, output)

    click.echo(f'File processed successfully. Output saved to {output}')


def write_json(data, output):
    """Write the data to a JSON file."""
    with open(output, 'w') as file:
        json.dump(data, file, indent=4)


def write_xlsx(data, output):
    """Write the data to a CSV file."""
    flattened_data = flatten_json(data)
    df = pd.DataFrame([flattened_data])
    df.to_excel(output, index=False)


if __name__ == '__main__':
    process_file()
