# User Stories
1. As a business analyst, I want to scrape product data from multiple e-commerce websites so that I can efficiently gather information for market research and pricing analysis. 

2. As a developer, I want to update the scraper’s hardcoded components through an easy-to-use interface so that I can quickly adapt to website changes without manual code edits. 

3. As an engineer, I want to scrape data from a specific product page by entering a URL so that I can retrieve the information I need without learning to code. 

4. As a business user, I want to filter the scraped data by specific parameters like price or category so that I can extract only the most relevant information for my reports. 

# Design Diagrams

## Design Level 1
The user wants to see more detailed information about a product inserts a URL using the web scraper. Goes through cloud services, then returns with specific data on the product. 
![D0](/Design%20Diagrams/D0.png)

## Design Level 2
The user wanted to gather more information on the product pricing to compare with other markets, it goes through the cloud service in which depending on who is using the web application returns data that can be analyzed. 
![D1](/Design%20Diagrams/D1.png)

## Design Level 3
This web scraping project allows users to input a product URL into a web scraper UI, which then processes the URL to extract relevant information. The scraper breaks down the URL and sends it to cloud services like Scraping Bee for conversion into an HTML string. This string is passed to Beautiful Soup for parsing, creating a structured HTML object. Pandas is used to extract specific data from the parsed HTML, which is then stored as a CSV file, Excel file, and in AWS S3 storage. The data is analyzed using tools like AWS QuickSight and Hey Marvin AI to provide insights based on user requirements. 
![D2](/Design%20Diagrams/D2.png)