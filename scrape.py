import requests
import json

url = "https://app-api.starzplay.com/api/reports/support/faq?language=en&tenantId=1"

headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    
    scraped_data = {}
    
    for category_data in data:
        category = category_data["category"]
        scraped_data[category] = []
        
        for content in category_data["content"]:
            question = content["question"]
            answer = content["answer"]
            
            # removing <br> by replacing it with nothing aand replacing "&quot;" with \" 
            answer = answer.replace("<br>", "")
            answer = answer.replace("&quot;", "\"")
            
            scraped_data[category].append({"question": question, "answer": answer})
    
    with open("scraped_data.json", "w") as json_file:
        json.dump(scraped_data, json_file, indent=4)
    
    print("Scraped data has been written to scraped_data.json.")
else:
    print("Failed to fetch data from the API:", response)
