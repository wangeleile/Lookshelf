import markdown2
from bs4 import BeautifulSoup
import json

def markdown_to_html(markdown_text):
    """Convert Markdown text to HTML"""
    return markdown2.markdown(markdown_text)

def html_to_json(html_content):
    """Convert HTML content to a structured JSON, grouping everything under H1 tags."""
    soup = BeautifulSoup(html_content, 'html.parser')
    result = {}
    current_header = None
    content = []
    for element in soup:
        if element.name == 'h1':
            if current_header:
                # Save the previous section before starting a new one
                result[current_header] = content
                content = []
            current_header = element.text
        elif current_header:
            # This handles converting the HTML elements back to a string format.
            # You might need more sophisticated handling for complex structures.
            content.append(str(element))
    
    # Don't forget to add the last section if there's no closing H1
    if current_header:
        result[current_header] = content
    
    return result

def markdown_file_to_json(file_path):
    """Read a markdown file and convert its content to JSON, grouped by H1 tags."""
    with open(file_path, 'r', encoding='utf-8') as file:
        markdown_content = file.read()
    
    html_content = markdown_to_html(markdown_content)
    json_content = html_to_json(html_content)
    
    # Define your output JSON file name
    output_file_path = file_path.rsplit('.', 1)[0] + '.json'
    
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_content, json_file, ensure_ascii=False, indent=4)
    
    print(f"Markdown content from '{file_path}' has been converted to JSON and saved to '{output_file_path}'")

# Example usage
markdown_file_path = 'books.md'  # Update this path to your markdown file
markdown_file_to_json(markdown_file_path)
