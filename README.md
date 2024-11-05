# Table of Contents
# Team Names
## [Almaamar Alkiyumi](#almaamar-alkiyumi-1)
## [Jason Yang](#jason-yang-1)
## [Matt Myers](#j-matthew-myers)
# Project Description (Assignment 2)
# User Stories and Design Diagrams
## User Stories
1. As a business analyst, I want to scrape product data from multiple e-commerce websites so that I can efficiently gather information for market research and pricing analysis. 

2. As a developer, I want to update the scraper’s hardcoded components through an easy-to-use interface so that I can quickly adapt to website changes without manual code edits. 

3. As an engineer, I want to scrape data from a specific product page by entering a URL so that I can retrieve the information I need without learning to code. 

4. As a business user, I want to filter the scraped data by specific parameters like price or category so that I can extract only the most relevant information for my reports. 

## Design Diagrams

### Design Level 0
![D0](/Design%20Diagrams/D0.png)

### Design Level 1
![D1](/Design%20Diagrams/D1.png)

### Design Level 2
![D2](/Design%20Diagrams/D2.png)

## Description of Diagrams
### Design Level 0
The user wants to see more detailed information about a product inserts a URL using the web scraper. Goes through cloud services, then returns with specific data on the product.
### Design Level 1
The user wanted to gather more information on the product pricing to compare with other markets, it goes through the cloud service in which depending on who is using the web application returns data that can be analyzed. 
### Design Level 2
This web scraping project allows users to input a product URL into a web scraper UI, which then processes the URL to extract relevant information. The scraper breaks down the URL and sends it to cloud services like Scraping Bee for conversion into an HTML string. This string is passed to Beautiful Soup for parsing, creating a structured HTML object. Pandas is used to extract specific data from the parsed HTML, which is then stored as a CSV file, Excel file, and in AWS S3 storage. The data is analyzed using tools like AWS QuickSight and Hey Marvin AI to provide insights based on user requirements.
# Project Tasks and Timeline
## Task List
### Almaamar Alkiyumi
#### Task List:
1. **Redesign the existing scraper to allow users to target reviews of all products on a specific page** of a website, instead of scraping the entire website.
2. **Redesign the existing scraper to allow users to target reviews of a specific product on a website**, instead of scraping the entire website.
3. **Develop an executable (.exe)** that allows users to easily launch the UI and automatically run all required dependencies for the scraper.
4. **Test and validate the functionality and usability** of both interfaces to ensure they meet specified requirements and perform as intended.
5. **Document the entire project development process**, including detailed steps for setting up, configuring, and running the application. Additionally, create comprehensive user guides for both business users and developers, outlining how to interact with the UI, manage scraping tasks, and monitor website changes.


### Jason Yang
#### Task List:
1. **Develop and refine the existing backend components of the scraper** to be more user-friendly and adaptable to changes.
2. **Research about advanced techniques that can improve the algorithms** for more efficient data scraping and data storage optimization.
3. **Develop and design a developer interface** for developers to manage and update the scraper’s hardcoded components.
4. **Test and troubleshoot** to ensure that the integration within the existing systems are performing as intended.

### Matt Myers
#### Task List:
1. **Evaluate the existing user interface for the web scraper. Document findings.** Note what works and what doesn't. Gather any prior design restrictions and evaluate them to see if they are still applicable.
2. **Design a maintainable user interface following best practices. Document design choices.** Study UI best practices and learn what common pitfalls to avoid.
3. **Research frontend frameworks and make an informed selection for the project. Document rationalization for selection.** Review user testimony for popular frameworks such as React, Svelte, Tailwind CSS, etc. Discuss with team the pros and cons of each and see which would be best for integrating with the rest of the tech stack.
4. **Develop the user interface in the selected frontend framework. Document development process and how maintenance should be performed in order to maintain selected design patterns.** Incrementally implement the features of the user interface. Collaborate on documentation for how the frontend will communicate with the backend.
5. **Gather user feedback on the frontend user experience. Apply the feedback if reasonable and possible.** Seek out possible test users to gather feedback on how the UI is presented, if the operation of the tool makes sense, etc. Apply any recommendations if they are applicable, and update documentation as needed.
6. **Test user interface against multiple different aspect ratios to ensure it is operable and presentable on many different screens. Document any findings during this process.** Ensure that the UI works on several common display sizes and orientations.

## Timeline and Effort Matrix
| Task | Sprints | Effort | Assigned To |
|------|--------:|--------:|-------------:|
| Redesign the existing scraper to allow users to target reviews of all products on a specific page | Jan 6 2025 - Feb 3 2025 | 90% Almaamar, 5% Jason, 5% Matt | Almaamar Alkiyumi |
| Research about advanced techniques that can improve the algorithms | Jan 6 2025 - Feb 3 2025 | 90% Jason, 5% Almaamar, 5% Matt |Jason Yang |
| Research frontend frameworks and make an informed selection for the project. Document rationalization for selection | Jan 6 2025 - Feb 3 2025 | 90% Matt, 5% Jason, 5% Almaamar | Matt Myers |
| Redesign the existing scraper to allow users to target reviews of a specific product on a website | Jan 6 2025 - Feb 3 2025 | 90% Almaamar, 5% Jason, 5% Matt | Almaamar Alkiyumi |
| Evaluate the existing user interface for the web scraper. Document findings | Jan 6 2025 - Feb 3 2025 | 90% Matt, 5% Jason, 5% Almaamar | Matt Myers |
| Document the entire project development process | Jan 6 2025 - Mar 3 2025 | 90% Almaamar, 5% Jason, 5% Matt | Almaamar Alkiyumi |
| Design a maintainable user interface following best practices. Document design choices | Feb 3 2025 - Mar 3 2025 | 90% Matt, 5% Jason, 5% Almaamar | Matt Myers |
| Develop and refine the existing backend components of the scraper | Feb 3 2025 - Mar 3 2025 | 90% Jason, 5% Almaamar, 5% Matt | Jason Yang |
| Develop the user interface in the selected frontend framework. Document development process and how maintenance should be performed in order to maintain selected design patterns | Feb 3 2025 - Mar 3 2025 | 90% Matt, 5% Jason, 5% Almaamar | Matt Myers |
| Develop and design a developer interface | Feb 3 2025 - Mar 3 2025 | 90% Jason, 5% Almaamar, 5% Matt | Jason Yang |
| Develop an executable (.exe) | Mar 3 2025 - Apr 7 2025 | 90% Almaamar, 5% Jason, 5% Matt | Almaamar Alkiyumi |
| Gather user feedback on the frontend user experience. Apply the feedback if reasonable and possible | Mar 3 2025 - Apr 7 2025 | 90% Matt, 5% Jason, 5% Almaamar | Matt Myers |
| Test and validate the functionality and usability | Mar 3 2025 - Apr 7 2025 | 90% Almaamar, 5% Jason, 5% Matt | Almaamar Alkiyumi |
| Test and troubleshoot | Mar 3 2025 - Apr 7 2025 | 90% Jason, 5% Almaamar, 5% Matt | Jason Yang |
| Test user interface against multiple different aspect ratios to ensure it is operable and presentable on many different screens. Document any findings during this process | Mar 3 2025 - Apr 7 2025 | 90% Matt, 5% Jason, 5% Almaamar | Matt Myers |

# ABET Concerns Essay
## Economic Constraints
Although Midea has agreed to fund the project, the budget is limited to less than $200 per month. This constraint requires the team to manage resources carefully, ensuring that the use of paid services like AWS and Scraping Bee stays within the monthly budget. Balancing performance with cost efficiency will be key. The team might need to explore cost-saving alternatives, such as optimizing the number of API calls or using free-tier services wherever possible. This financial limitation could influence the scale and frequency of data collection.
## Security Constraints
Security is a crucial factor due to the nature of web scraping and data storage. The project involves accessing and storing data from e-commerce websites, which raises concerns about data protection and privacy. It's important to ensure that sensitive information is not exposed during the scraping process or while storing it in cloud services like AWS. The team must implement proper encryption, access controls, and regular security audits to prevent unauthorized access and ensure compliance with data privacy regulations.
## Legal Constraints
There are potential legal challenges in web scraping, particularly concerning the terms of service of websites being scraped. Many websites have restrictions on automated data extraction, and violating these terms could lead to legal issues. The team needs to ensure that the scraping activities comply with all relevant regulations, such as not scraping private or copyrighted content without permission. This legal constraint may limit the scope of websites that can be targeted and require a thorough review of each website's legal policies before scraping.
## Ethical Constraints
The project must address ethical concerns regarding data collection, especially when scraping user reviews and product information. Ensuring that the collected data is used in a fair and transparent manner is essential to avoid harm to individuals or businesses. Ethical web scraping practices include respecting website policies, obtaining permission where necessary, and avoiding any misuse of the gathered data. The team must also ensure that the project does not contribute to misinformation or data manipulation, promoting ethical use of the information for analysis.

# PPT Slideshow (Assignment 8)
# Self-Assessment Essays (Assignment 3)
# Professional Biographies
## Almaamar Alkiyumi

### Professional Biography

I am currently enrolled as a Senior at the University of Cincinnati pursuing an undergraduate degree in Computer Science, graduating in May 2026. I have a strong background in data science, software development, and web development. I'm passionate about solving complex problems and building scalable solutions.

### Contact Me

- **Email**: alkiyuam@mail.uc.edu
- **LinkedIn**: [Almaamar Alkiyumi](https://www.linkedin.com/in/AlmaamarAlkiyumi/)

### 💼 Experience

#### Midea Group (U.S.) | Data Science Intern

- **Duration**: Jan 2024 – May 2024

#### University of Cincinnati (U.S.) | Engineering Teaching Assistant

- **Duration**: Jan 2023 - May 2023

#### The Cincinnati Insurance Company (U.S.) | Software Engineering Intern

- **Duration**: May 2023 – August 2023

#### Deloitte & Touché (M.E.) | Information Technology Audit Intern

- **Duration**: Aug 2022 – Dec 2022

### Skills

- **Programming Languages**: Python, C/C++, Visual Basic for Applications (VBA)
- **Web Development**: HTML, CSS, JavaScript, Django, ReactJS, MySQL, SQLite, PostgreSQL
- **Software**: Microsoft Office Suite, Visual Studio, LabVIEW, MATLAB, Wire Shark, GitHub, Amazon Web Services Cloud
- **Operating Systems**: Linux Ubuntu, Windows 7-11, macOS Monterey, Android & iOS
- **Other Tools**: Pandas, NumPy, Scikit-learn, Beautiful Soup, Matplotlib, Selenium

### Education

- **Bachelor of Science, Computer Science**
  - University of Cincinnati, Expected Graduation: May 2026
  - Honors: Dean’s List Recognition (4/4 Semesters), Fully Funded Scholarship (Ministry of Higher Education of Oman)

### Projects

#### Online Shop Application

- **Technologies**: Django, HTML, CSS, ReactJS & PostgreSQL
- **Repository**: [Online Shop Application](https://github.com/AAlkiyumi/online-shop-application)

#### Multi-Threaded Bulletin Board System

- **Technologies Used**: Python & Java
- **Repository**: [Multi-Threaded Bulletin Board System](https://github.com/AAlkiyumi/networking_final_project)

#### Multi-Threaded Web Server and FTP Client

- **Technologies Used**: Python
- **Repository**: [Multi-Threaded Web Server and FTP Client](https://github.com/AAlkiyumi/Multi-Threaded-Web-Server-and-FTP-Client)

#### Autonomous Product Retrieval System

- **Technologies**: EV3 LEGO MINDSTORMS, Python & VSCode EV3Dev extension
- **Repository**: [Autonomous Product Retrieval System]()

#### Prototype Mover Robot

- **Technologies**: EV3 LEGO MINDSTORMS & LabVIEW
- **Repository**: [Prototype Mover Robot]()

### Capstone Project Sought

I am seeking a capstone project that aligns with my expertise in full stack development, data science, data analysis, or machine learning. With strong proficiency in Python and web development, I am eager to tackle a project that allows me to leverage my skills in these areas. I am particularly interested in opportunities related to business domains, such as finance or accounting, where I can apply my technical skills to real-world challenges. However, I am also open to exploring other project ideas that align with my expertise and provide a meaningful challenge. My goal is to contribute to a project that showcases my capabilities and drives impactful results.

---

## Jason Yang

### Contact Information

- **Email**: Yang2j7@mail.uc.edu

### About Me

Hi, I’m Jason. I’ve had three co-op rotations at the same company International TechneGroup Inc. located in Milford, OH. The co-op experience consists mainly of Python and C++. Gained some fundamentals in game developing and tried creating my own game through Unity game engine alongside with a mentor from game developing field. Interested in anything developing and hands-on related projects.

### Co-op Experiences/Projects

#### ITI-Wipro, Milford, OH | Software Engineer Co-op

- Implemented 10+ software enhancements requested by our customers providing smoother user interfaces.
- Enhanced 15+ existing software features to be more reliable and stable for customer’s everyday needs.
- Provided quality check on significant defects in a native model that impacts downstream re-use.
- Identified unacceptable differences between native and derivative models and unintentional or undocumented changes between revisions of a model.

#### Game Development Project

- Developed a top-down 2D pixel game using the Unity game engine and C# script from scratch.
- Learned various concepts on game developing both technical and behavioral and self-discipline.
- Collaborated with game development mentor 1-2 times a month to discuss and report progress.
- Released a demo/trailer as the final product and presented it in front of mentor.

### Skills

- **Programming**: Python, C++, C#, HTML
- **Game Engine**: Unity, Unreal
- **Operating System**: Windows, macOS

### Areas of Interest

- Game Development
- Web App Development 
- Augmented Reality (AR) or Virtual Reality (VR)
- Software Development

---

## J. Matthew Myers

### Contact Info

- **Email**: myers3jm@mail.uc.edu

### Biography

Matt Myers is a senior at the University of Cincinnati. Matt will graduate in Spring, 2025 with a Bachelor's degree in computer science and a certificate in cyber operations with a focus on cyber attacks and security.

### Co-op Work Experience

#### Rotation 1

- **Title**: Embedded Security Firmware - Summer Student  
- **Company**: Lexmark International  
- **Employment Period**: May 2022 - Aug 2022  
- **Technical Skills**: C++, CMake, Cross-platform development, Git, Linux  
- **Non-technical Skills**: Microsoft Office, Scrum, Communication  

#### Rotation 2

- **Title**: Embedded Security Firmware - Spring Student  
- **Company**: Lexmark International  
- **Employment Period**: Jan 2023 - Apr 2023  
- **Technical Skills**: Python, C, YAML, HTML, CSS, JavaScript  
- **Non-technical Skills**: Microsoft Office, Scrum, Communication  

#### Rotation 3

- **Title**: Software Engineering Co-op  
- **Company**: SHP  
- **Employment Period**: Aug 2023 - Dec 2023  
- **Technical Skills**: C#, .NET Framework, Git, Autodesk Revit, Debugging  
- **Non-technical Skills**: Google Workspaces, Communication, Scrum  

#### Rotation 4

- **Title**: Software Engineering Co-op  
- **Company**: SHP  
- **Employment Period**: May 2024 - Aug 2024  
- **Technical Skills**: C#, .NET Framework, Git, Python, Rust, Autodesk Revit, Debugging  
- **Non-technical Skills**: Google Workspaces, Communication, Scrum  

### Project Sought

Matt is looking for a project that involves security and/or data science. Such projects might include:

- Secure web applications (Matt took a course on programming and hacking web apps)
    - This could include anything, such as a social network, e-commerce site, online game, etc.
- Some kind of security solution to protect individuals and/or their data

# Budget
# Appendix