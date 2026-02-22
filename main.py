def get_cpwp_course_content():
    # Original implementation to extract course content
    content = []
    pdf_links = []
    response = requests.get(COURSE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Assuming the content is structured in a specific way
    for item in soup.find_all('div', class_='course-item'):
        title = item.find('h3').text
        description = item.find('p').text
        content.append({'title': title, 'description': description})
        
        # Extracting PDF links
        for link in item.find_all('a'):
            href = link.get('href')
            if href.endswith('.pdf'):
                pdf_links.append(href)
    
    return content, pdf_links
