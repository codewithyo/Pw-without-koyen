def get_cpwp_course_content():
    import requests
    from bs4 import BeautifulSoup

    url = 'your_url_here'  # replace with the actual URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting PDF links explicitly
    pdf_links = []
    for link in soup.find_all('a', href=True):
        if link['href'].endswith('.pdf'):
            pdf_links.append(link['href'])

    return pdf_links
