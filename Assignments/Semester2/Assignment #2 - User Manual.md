# **User Manual for Web Scraping and Sentiment Analysis**

Welcome to the **Small Appliances Team**! This user manual is designed to help you get started with the **web scraping** process, including setting up your environment, running the scrapers, and analyzing the data. This guide focuses specifically on the **web scraper** and its related workflows, ensuring you have all the information you need to successfully scrape product data and reviews from various websites.

---

## **Table of Contents**
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Web Scraping Overview](#web-scraping-overview)
4. [Running the Web Scrapers](#running-the-web-scrapers)
5. [Scraping Workflow](#scraping-workflow)
6. [Dependencies and Tools](#dependencies-and-tools)
7. [Troubleshooting and Support](#troubleshooting-and-support)

---

## **Introduction**

The **web scraper** is a critical tool for the Small Appliances Team. It collects product information and customer reviews from multiple e-commerce websites, including **Amazon**, **Best Buy**, **Walmart**, and others. The scraped data is then used for sentiment analysis, market research, and product performance evaluation.

This manual will guide you through the process of setting up the scraper, running it, and handling the data it collects. By the end of this guide, you’ll be able to scrape product data, format it, and prepare it for further analysis.

---

## **Getting Started**

### **1. Setting Up Your Environment**
- **PC Setup**: Contact **Jeff Sosebee** to get your PC set up with the necessary software and permissions.
- **GitHub Access**: Create a GitHub account if you don’t already have one. Reach out to **John Hooker** on the electronics team to get added to the Midea GitHub group.
- **Directory Structure**: Ensure you are in the correct directory for your product line. Use the command `cd *product line*` to navigate to the appropriate folder.

### **2. Key Contacts**
- **Josh Phillips**: For technical questions related to web scraping, Python, or debugging.
- **Brad Li**: For assistance with running the scrapers and troubleshooting.
- **Matt Hunter (Manager)**: For general questions and guidance on your tasks.

---

## **Web Scraping Overview**

The **web scraper** collects product information and reviews from the following websites:
- Amazon.com
- BestBuy.com
- Costco.com
- HomeDepot.com
- Lowes.com
- Walmart.com

The scraper uses two main methods:
1. **Selenium Chrome Driver**: Scrapes data locally on your machine.
2. **Scraping Bee API**: Scrapes data online using an API key.

### **How the Scrapers Work**
1. **Scraping Product Information**:
   - The scraper navigates through product pages, extracts product details (name, price, URL), and stores them in a list of dictionaries.
   - The data is then converted into a pandas DataFrame and exported to an Excel file.

2. **Scraping Reviews**:
   - The scraper visits each product URL, extracts reviews, and stores them in a list of dictionaries.
   - The reviews are then converted into a pandas DataFrame and exported to an Excel file.

3. **Formatting and Combining Reviews**:
   - Reviews from multiple websites are combined into a single DataFrame.
   - Duplicate reviews are filtered out using SHA-256 encryption.

---

## **Running the Web Scrapers**

### **1. Terminal Commands**
To run the scrapers, follow these steps:
1. Navigate to the correct directory using `cd *product line*`.
2. Run the following scripts in order:
   - `scrape_product.py`: Scrapes product information and reviews.
   - `tag_and_predict_sentiment_product.py`: Tags reviews by topic and predicts sentiment.
   - `custom_sentiment_calculation.py`: Performs additional sentiment analysis for visualization.

### **2. Preparing the Link**
- Go to a website like Amazon, search for a product, and copy the link.
- Paste the link into `scrape_YourAppliance.py` and edit it by removing the page number (if using Scraping Bee).

### **3. Running the Scraper**
- **Selenium Version**:
  - The scraper will open the website using the Chrome driver, navigate through all pages, and extract product information and reviews.
  - The data is stored in a pandas DataFrame and exported to an Excel file.
- **Scraping Bee Version**:
  - The scraper will loop through the pages by changing the page number in the URL.
  - The data is parsed using BeautifulSoup and stored in a pandas DataFrame.

---

## **Scraping Workflow**

### **1. Scraping Product Information**
- The scraper extracts product details (name, price, URL) from each product card on the website.
- The data is stored in a list of dictionaries and converted to a pandas DataFrame.
- The DataFrame is exported to an Excel file for reference.

### **2. Scraping Reviews**
- The scraper visits each product URL, extracts reviews, and stores them in a list of dictionaries.
- The reviews are converted to a pandas DataFrame and exported to an Excel file.

### **3. Formatting and Combining Reviews**
- Reviews from multiple websites are combined into a single DataFrame.
- Duplicate reviews are filtered out using SHA-256 encryption.
- The combined data is exported to an Excel file for further analysis.

---

## **Dependencies and Tools**

### **1. Key Tools**
- **NordVPN**: To avoid IP blocking when using the Selenium Chrome Driver.
- **ChromeDriver**: Must be updated whenever Chrome is updated. Download the latest version [here](https://developer.chrome.com/docs/chromedriver/downloads).
- **ScrapingBee API**: Used for online scraping. Contact Josh or Brad if you run out of credits.
- **Python Modules**:
  - `selenium`: For browser automation.
  - `beautifulsoup`: For parsing HTML.
  - `pandas`: For data manipulation and Excel file handling.
  - `nltk`: For natural language processing.
  - `tqdm`: For progress bars during scraping.
  - `aws-comprehend`: For sentiment analysis.
  - `chatgpt-api`: For tagging reviews by topic.

---

## **Troubleshooting and Support**

### **1. Common Issues**
- **IP Blocking**: Ensure NordVPN is connected when using Selenium.
- **ChromeDriver Errors**: Update ChromeDriver whenever Chrome is updated.
- **ScrapingBee Credits**: Contact Josh or Brad if you run out of credits.

### **2. Support Contacts**
- **Josh Phillips**: For technical questions and debugging.
- **Brad Li**: For assistance with running scrapers.
- **Matt Hunter**: For general guidance and project direction.

---

## **Conclusion**

This manual provides a comprehensive guide to using the **web scraper** for the Small Appliances Team. By following these steps, you’ll be able to efficiently collect product data and reviews from multiple websites, format the data, and prepare it for further analysis. If you have any questions or run into issues, don’t hesitate to reach out to the team for support.

Good luck, and happy scraping!