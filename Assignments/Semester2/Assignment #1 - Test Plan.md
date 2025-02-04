1. Overall Test Plan Strategies

*One to three paragraphs describing general testing strategies employed by your project*

2. Test Case Descriptions
List a series of 10-25 tests for validating your project outcomes. For each test provide the following:
    1. test case identifier (a number or unique name)
    2. purpose of test
    3. description of test
    4. inputs used for test
    5. expected outputs/results
    6. normal/abnormal/boundary case indication
    7. blackbox/whitebox test indication
    8. functional/performance test indication
    9. unit/integration test indication

    Terminology:
    - normal testing: testing with expected inputs in normal operating conditions. 
    - abnormal testing: testing with exceptional inputs or conditions. 
    - boundary testing: testing focused on subdivisions of an input domain 
    - blackbox testing: testing based on the requirements specification. 
    - whitebox testing: testing based on knowledge of the implementation. 
    - functional testing: testing based on expected features. 
    - performance testing: testing based on expected performance criteria such as 
    - eed, power consumption, accuracy within tolerances, etc. 
    - unit testing: testing of individual components or modules. 
    - integration testing: testing of interfaces between components and
        
    1.1 Backend Test 1 
    1.2 This test will ensure that the scraper successfully fetches web pages. 
    1.3 This test will ensure that the scraper fetches a web page successfully from a given URL by sending the correct GET requests.  
    1.4 Inputs: A valid web page URL 
    1.5 Outputs: HTML content of the web page. 
    1.6 Normal 
    1.7 Blackbox 
    1.8 Functional 
    1.9 Unit Test 

    2.1 Backend Test 2 
    2.2 This test will test error handling to ensure the scraper doesn’t crash under unexpected conditions. 
    2.3 The scraper should handle invalid URLs, timeouts, connection errors, and missing fields without crashing. 
    2.4 Inputs: Missing fields such as a HTML without the required elements 
    2.5 Outputs: Handle missing fields along with other errors by raising an exception 
    2.6 Abnormal 
    2.7 Blackbox 
    2.8 Functional 
    2.9 Unit Test 

    3.1 Backend Test 3 
    3.2 The purpose of this test is to optimize performance and efficiency of the scraper. 
    3.3 A poorly optimized scraper can slow down due to unnecessary requests, redundant processing, or inefficient parsing. This test will test the scraper’s speed and resource usage. 
    3.4 Inputs: Large HTML page or multiple pages 
    3.5 Outputs: Completion withing acceptable time without redundant requests. 
    3.6 Boundary 
    3.7 Blackbox 
    3.8 Performance 
    3.9 Unit Test 

    4.1 Backend Test 4 
    4.2 This test will ensure that the scraper’s extracted data is stored and/or sent correctly. 
    4.3 Many scrapers save data on SQLite, MongoDB, or send it to an API for analysis and the purpose of this test is to ensure that the scraped data is correctly stored or processed. 
    4.4 Inputs: A dictionary of extracted data 
    4.5 Outputs: Proper storage in SQLite, MongoDB, or API. 
    4.6 Normal. 
    4.7 Blackbox. 
    4.8 Functional. 
    4.9 Integration Test 

    5.1 Frontend Test 1 
    5.2 Ensure UI loads properly on different devices. 
    5.3 Test responsiveness and layout. 
    5.4 Inputs: Various screen sizes and resolutions. 
    5.5 Outputs: UI elements adapt correctly. 
    5.6 Normal. 
    5.7 Blackbox. 
    5.8 Functional. 
    5.9 Unit Test. 

    6.1 Frontend Test 2 
    6.2 Validate form inputs and user interactions. 
    6.3 Ensure correct data submission and validation messages. 
    6.4 Inputs: Valid and invalid user inputs. 
    6.5 Outputs: Correct error handling and success messages. 
    6.6 Abnormal. 
    6.7 Blackbox. 
    6.8 Functional. 
    6.9 Unit Test. 

    7.1 Frontend Test 3 
    7.2 Test UI against multiple aspect ratios. 
    7.3 Ensure UI is operable and presentable. 
    7.4 Inputs: Various display sizes. 
    7.5 Outputs: UI remains functional across screens. 
    7.6 Boundary. 
    7.7 Blackbox. 
    7.8 Performance. 
    7.9 Unit Test. 

    8.1 Backend Test 5 
    8.2 Validate integration between scraper and database. 
    8.3 Ensure smooth data transfer. 
    8.4 Inputs: Extracted data from scraper. 
    8.5 Outputs: Proper storage and retrieval. 
    8.6 Normal. 
    8.7 Whitebox. 
    8.8 Functional. 
    8.9 Integration Test. 

    9.1 Frontend Test 4 
    9.2 Validate API communication with UI. 
    9.3 Ensure correct display of fetched data. 
    9.4 Inputs: API responses. 
    9.5 Outputs: Correct rendering of data. 
    9.6 Normal. 
    9.7 Blackbox. 
    9.8 Functional. 
    9.9 Integration Test. 

    10.1 Frontend Test 5 
    10.2 Validate user authentication. 
    10.3 Ensure proper login and access control. 
    10.4 Inputs: Valid and invalid login credentials. 
    10.5 Outputs: Successful login or appropriate error message. 
    10.6 Abnormal. 
    10.7 Blackbox. 
    10.8 Functional. 
    10.9 Integration Test.

3. Overall Test Case Matrix

|Test Case ID|Normal/Abnormal/Boundary|Blackbox/Whitebox|Functional/Performance|Unit/Integration|
|-|-|-|-|-|
|B1|Normal|Blackbox|Functional|Unit|
|B2|Abnormal|Blackbox|Functional|Unit|
|B3|Boundary|Blackbox|Performance|Unit|
|B4|Normal|Blackbox|Functional|Integration|
|B5|Normal|Whitebox|Functional|Integration|
|F1|Normal|Blackbox|Functional|Unit|
|F2|Abnormal|Blackbox|Functional|Unit|
|F3|Boundary|Blackbox|Performance|Unit|
|F4|Normal|Blackbox|Functional|Integration|
|F5|Abnormal|Blackbox|Functional|Integration|