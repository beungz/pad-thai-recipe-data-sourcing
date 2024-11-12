from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

import pandas as pd
from fractions import Fraction
import time



"""SECTION 1 : Determine overall number of relevant recipes"""
# Open Chrome Browser
chrome_options = webdriver.ChromeOptions()

driver = webdriver.Chrome(options=chrome_options)

driver.maximize_window()

search_result_url = 'https://www.yummly.com/recipes?q=pad%20thai&taste-pref-appended=true&sortBy=rel'

driver.get(search_result_url)

# Wait for the recipe section to be present
recipe_section = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "RecipeContainer"))
)

num_of_recipe_element = driver.find_element(By.CLASS_NAME, "recipe-container-title")

num_of_recipe_string = num_of_recipe_element.find_element(By.TAG_NAME, "span").text.split()[0].replace(",", "")
num_of_recipe = int(num_of_recipe_string)

print(num_of_recipe)



"""SECTION 2 : Determine number of relevant recipes that actually return from the website"""
body = driver.find_element(By.TAG_NAME, "body")

previous_recipe_count = 0
scroll_count = 20

for _ in range(scroll_count):
    # Scroll down
    body.send_keys(Keys.END) 

    # Check number of recipe loaded on the webpage
    recipe_records = driver.find_elements(By.CLASS_NAME, "recipe-card")
    current_recipe_count = len(recipe_records)

    # If number of recipe does not increase, then stop scrolling
    if current_recipe_count == previous_recipe_count:
        break
    else:
        print("Num of Recipes detected: ",current_recipe_count)
        previous_recipe_count = current_recipe_count

    # Scroll to the last recipe currently displayed
    time.sleep(5) # Wait to load the webpage.
    driver.execute_script("arguments[0].scrollIntoView()", recipe_records[-1])
    time.sleep(5) # Wait to load the webpage.
    driver.execute_script("arguments[0].scrollIntoView()", recipe_records[-1])

# Use BeautifulSoup to scrape the data using the page_source returned from Selenium webdriver
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')



"""SECTION 3 : Get list of recipes, links, together with some basic information for each recipe, from the search result in Section 2"""
soup_recipe_records = soup.find_all("div", class_="recipe-card")
count_recipe = 0
count_relevant_recipe = 0
count_recipe_with_ratings = 0

recipe_id_list, recipe_name_list, recipe_creator_name_list, recipe_ratings_list, recipe_num_saved_list, recipe_link_list = [], [], [], [], [], []

for recipe_record in soup_recipe_records:
    count_recipe += 1
    recipe_name = recipe_record.find("a", class_="card-title").getText().strip()
    recipe_creator_name = recipe_record.find("a", class_="source-link").getText().strip()
    
    if "pad thai" in recipe_name.lower():
        count_relevant_recipe += 1
        try:
            recipe_ratings_text = recipe_record.find("a", class_="review-stars")["title"].strip()
            recipe_ratings = float(recipe_ratings_text.split()[1])
            count_recipe_with_ratings += 1

            print("\n",count_recipe_with_ratings)
            print(recipe_name)
            print(recipe_creator_name)
            print("{:.2f}".format(recipe_ratings))

            recipe_num_saved = int(recipe_record.find("span", class_="count").getText().strip().replace("k", "000"))
            recipe_link = recipe_record.div.img["data-pin-url"].strip()

            print(recipe_num_saved)
            print(recipe_link)

            recipe_id_list.append(count_recipe_with_ratings)
            recipe_name_list.append(recipe_name)
            recipe_creator_name_list.append(recipe_creator_name)
            recipe_ratings_list.append(recipe_ratings)
            recipe_num_saved_list.append(recipe_num_saved)
            recipe_link_list.append(recipe_link)

        except:
            count_recipe_with_ratings += 0

print("\nTotal number of recipes: ", count_recipe)
print("Total number of relevant recipes: ", count_relevant_recipe)
print("Total number of recipes with ratings: ", count_recipe_with_ratings)
    
recipe_data_from_search = pd.DataFrame([recipe_id_list, recipe_name_list, recipe_creator_name_list, recipe_ratings_list, recipe_num_saved_list, recipe_link_list], index=["recipe_id", "recipe_name", "recipe_creator_name", "recipe_ratings", "recipe_num_saved", "recipe_link"]).T
recipe_data_from_search.to_csv("yummly_recipe_data_from_search.csv")



"""SECTION 4 : Get list of xml links from the site map"""
sitemap_xml_url = 'https://www.yummly.com/yummly-all-pages-us.xml'

driver.get(sitemap_xml_url)

driver.implicitly_wait(20)

# Use BeautifulSoup to scrape the data using the page_source returned from Selenium webdriver
page_source2 = driver.page_source
soup2 = BeautifulSoup(page_source2, 'html.parser')

soup_xml = soup2.find_all("loc")
xml_links = []

for xml_record in soup_xml:
    xml_link = xml_record.getText().strip()
    if "https://www.yummly.com/yummly-pages-recipe-" in xml_link:
        xml_links.append(xml_link)
        print(xml_link)

print("\nTotal number of xml links: ", len(xml_links))

xml_link_data = pd.DataFrame([xml_links], index=["xml_link"]).T
xml_link_data.to_csv("yummly_xml_link_data.csv")



"""SECTION 5 : Retrieve list of recipe links from the XML links returned from Section 4"""
def get_xml_link(driver, xml_link, count_recipe, first_xml):
    count_relevant_recipe = count_recipe
    recipe_id_list, recipe_link_list = [], []

    try:
        driver.get(xml_link)

        # driver.implicitly_wait(60)
        # Wait for the xml link section to be present
        xml_link_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "loc"))
        )

        # Use BeautifulSoup to scrape the data using the page_source returned from Selenium webdriver
        page_source3 = driver.page_source
        soup3 = BeautifulSoup(page_source3, 'html.parser')

        soup3_recipe_records = soup3.find_all("loc")

        for recipe_record in soup3_recipe_records:
            recipe_link = recipe_record.getText().strip()
    
            if "pad-thai" in recipe_link.lower():
                count_relevant_recipe += 1
                print(count_relevant_recipe)
                print(recipe_link)
            
                recipe_id_list.append(count_relevant_recipe)
                recipe_link_list.append(recipe_link)

        print("Total number of relevant recipes: ", count_relevant_recipe)
        time.sleep(5)

        recipe_alllink_data = pd.DataFrame([recipe_id_list, recipe_link_list], index=["recipe_id", "recipe_link"]).T
        if first_xml:
            recipe_alllink_data.to_csv("yummly_recipe_alllink_data.csv")
        else:
            recipe_alllink_data.to_csv("yummly_recipe_alllink_data.csv", mode="a", index=True, header=False)

        return count_relevant_recipe
    except:
        print("Error occured")
        # Reopen Chrome Browser
        driver.quit()
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        return get_xml_link(driver, xml_link, count_recipe, first_xml)

count_recipe = 0
first_xml = True
count_xml = -1

for xml_link in xml_links:
    count_xml += 1
    print("\n", xml_link)
    count_recipe = get_xml_link(driver, xml_link, count_recipe, first_xml)
    first_xml = False



"""SECTION 6 : Function to get ingredients from any given recipe URL"""
def get_ingredients(recipe_link, recipe_id, recipe_ratings_from_search, first_recipe, recipe_data_csv_name, ingredient_data_csv_name):
    try:
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()

        driver.get(recipe_link)
        driver.implicitly_wait(10)

        # Wait for the ingredient section to be present
        ingredient_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "IngredientLine"))
        )

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        overall_recipe_info = soup.find("div", class_="primary-info-text")

        recipe_name = overall_recipe_info.div.h1.getText().strip()
        recipe_creator_name = overall_recipe_info.div.find("span", class_="attribution").a.getText().strip()

        try:
            recipe_num_of_reviewers_string = overall_recipe_info.div.find("span", class_="count font-bold micro-text").getText().strip()
            recipe_num_of_reviewers = int(recipe_num_of_reviewers_string[1:-1].replace(",", ""))

            if recipe_ratings_from_search is None:
                recipe_ratings = 0
                for i in range(1,6):
                    star = overall_recipe_info.div.find("span", attrs={"data-star-number": str(i)}).get("class")
                    if star[1] == "full-star":
                        recipe_ratings += 1
                    elif star[1] == "half-star":
                        recipe_ratings += 0.5
            else:
                recipe_ratings = recipe_ratings_from_search
        except:
            return None
        
        try:
            recipe_saved = soup.find("div", class_="recipe-interactions-wrapper")
            recipe_num_saved = int(recipe_saved.find("span", class_="count").getText().strip().replace("k", "000"))
        except:
            recipe_num_saved = 0
        
        # print("\n", recipe_id)
        print(recipe_name)
        print(recipe_creator_name)
        print(recipe_ratings)
        print(recipe_num_of_reviewers)
        print(recipe_num_saved)

        recipe_generic_data = pd.DataFrame([recipe_id, recipe_name, recipe_creator_name, recipe_ratings, recipe_num_of_reviewers, recipe_num_saved, recipe_link], index=["recipe_id", "recipe_name", "recipe_creator_name", "recipe_ratings", "recipe_num_of_reviewers", "recipe_num_saved", "recipe_link"]).T

        ingredient_list = soup.findAll("li", class_="IngredientLine")

        recipe_id_list, ingredient_name_list, ingredient_amount_list, ingredient_unit_list, ingredient_remainder_list = [], [], [], [], []
        print("Number of Ingredients: ", len(ingredient_list))

        if ingredient_list is not None:
            for CurrentIngredient in ingredient_list:

                ingredient_name, ingredient_amount, ingredient_unit, ingredient_remainder = "", "", "", ""

                if CurrentIngredient.find("span", class_="ingredient"):
                    ingredient_name = CurrentIngredient.find("span", class_="ingredient").getText().strip()
                if CurrentIngredient.find("span", class_="amount"):
                    ingredient_amount = CurrentIngredient.find("span", class_="amount").span.getText().strip()
                    ingredient_amount = float(sum(Fraction(s) for s in ingredient_amount.split()))
                if CurrentIngredient.find("span", class_="unit"):
                    ingredient_unit = CurrentIngredient.find("span", class_="unit").getText().strip()
                if CurrentIngredient.find("span", class_="remainder"):
                    ingredient_remainder = CurrentIngredient.find("span", class_="remainder").getText().strip()

                recipe_id_list.append(recipe_id)
                ingredient_name_list.append(ingredient_name)
                ingredient_amount_list.append(ingredient_amount)
                ingredient_unit_list.append(ingredient_unit)
                ingredient_remainder_list.append(ingredient_remainder)
        
            ingredient_data = pd.DataFrame([recipe_id_list, ingredient_name_list, ingredient_amount_list, ingredient_unit_list, ingredient_remainder_list], index=["recipe_id","ingredient_name","ingredient_amount","ingredient_unit","ingredient_remainder"]).T

            if first_recipe:
                recipe_generic_data.to_csv(recipe_data_csv_name)
                ingredient_data.to_csv(ingredient_data_csv_name)
            else:
                recipe_generic_data.to_csv(recipe_data_csv_name, mode="a", index=True, header=False)
                ingredient_data.to_csv(ingredient_data_csv_name, mode="a", index=True, header=False)
            
            return recipe_ratings

        driver.quit()
    except:
        print("Error occured")
        print("Recipe ID: ", recipe_id)
        print("Recipe URL: ", recipe_link)

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        try:
            page_not_found = soup.find("div", class_="generic-not-found")
            if page_not_found is not None:
                print("Recipe does not exist")
                return None
        except:
            # Reopen Chrome Browser
            driver.quit()
            return get_ingredients(recipe_link, recipe_id, recipe_ratings_from_search, first_recipe, recipe_data_csv_name, ingredient_data_csv_name)



"""SECTION 7 : Get ingredient data for the recipes from the search result in Section 2"""
recipe_data_from_search = pd.read_csv("yummly_recipe_data_from_search.csv")
recipe_data_csv_name = "yummly_recipe_data.csv"
ingredient_data_csv_name = "yummly_ingredient_data.csv"
first_recipe = True

for ind in recipe_data_from_search.index:
    print("\nRecipe ID: ",recipe_data_from_search["recipe_id"][ind])
    get_ingredients(recipe_data_from_search["recipe_link"][ind], recipe_data_from_search["recipe_id"][ind], recipe_data_from_search["recipe_ratings"][ind], first_recipe, recipe_data_csv_name, ingredient_data_csv_name)
    first_recipe = False



"""SECTION 8 : Get ingredient data for the recipe links from Section 5 (links from XML)"""
recipe_alllink_data = pd.read_csv("yummly_recipe_alllink_data.csv")
recipe_data_from_search = pd.read_csv("yummly_recipe_data_from_search.csv")

recipe_data_csv_name = "yummly_recipe_data.csv"
ingredient_data_csv_name = "yummly_ingredient_data.csv"
first_recipe = False

count_recipe = len(recipe_data_from_search)

for ind in recipe_alllink_data.index:
    current_recipe_link = recipe_alllink_data["recipe_link"][ind]
    if not (current_recipe_link in recipe_data_from_search["recipe_link"].values):
        count_recipe += 1
        print("\nRecipe ID: ",count_recipe)
        print("Link no: ", ind)
        current_recipe_ratings = get_ingredients(current_recipe_link, count_recipe, None, first_recipe, recipe_data_csv_name, ingredient_data_csv_name)
        if current_recipe_ratings is None:
            count_recipe -= 1
            print("Recipe Link: ", current_recipe_link)
            print("Skipped. There is no ratings for this recipe, or page not found.")