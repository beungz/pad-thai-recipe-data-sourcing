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
import unicodedata



def a_open_chrome():
    """Open chrome browser and return driver"""
    # Open Chrome Browser
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver



def a_create_xml_list(driver, initial_webscraped_data_directory):
    """Get list of xml links from the site map"""
    # Go to sitemap to obtain list of xml links
    sitemap_xml_url = 'https://www.allrecipes.com/sitemap.xml'
    driver.get(sitemap_xml_url)
    driver.implicitly_wait(20)

    # Use BeautifulSoup to scrape the data using the page_source returned from Selenium webdriver
    page_source2 = driver.page_source
    soup2 = BeautifulSoup(page_source2, 'html.parser')

    soup_xml = soup2.find_all("loc")
    xml_links = []

    for xml_record in soup_xml:
        xml_link = xml_record.getText().strip()
        if "https://www.allrecipes.com/sitemap_" in xml_link:
            xml_links.append(xml_link)
            print(xml_link)

    print("\nTotal number of xml links: ", len(xml_links))

    # Save the list of xml links into CSV
    xml_link_data = pd.DataFrame([xml_links], index=["xml_link"]).T
    xml_link_data.to_csv(f"{initial_webscraped_data_directory}allrecipes_xml_link_data.csv")
    return xml_links



def a_get_recipe_link_from_one_xml(driver, xml_link, count_recipe, first_xml, initial_webscraped_data_directory):
    '''Retrieve list of recipe links related to Pad Thai, from the XML link'''
    count_relevant_recipe = count_recipe
    recipe_id_list, recipe_link_list = [], []

    try:
        # Go to individual xml link
        driver.get(xml_link)
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
    
            if ("pad-thai" in recipe_link.lower()) and ("https://www.allrecipes.com/recipe/" in recipe_link.lower()):
                # If pad-thai is found in the link address, then append the recipe link to the list
                count_relevant_recipe += 1
                print(count_relevant_recipe)
                print(recipe_link)
            
                recipe_id_list.append(count_relevant_recipe)
                recipe_link_list.append(recipe_link)

        print("Total number of relevant recipes: ", count_relevant_recipe)
        time.sleep(5)

        # Save all relevant recipe links found into CSV
        recipe_alllink_data = pd.DataFrame([recipe_id_list, recipe_link_list], index=["recipe_id", "recipe_link"]).T
        if first_xml:
            recipe_alllink_data.to_csv(f"{initial_webscraped_data_directory}allrecipes_recipe_alllink_data.csv")
        else:
            recipe_alllink_data.to_csv(f"{initial_webscraped_data_directory}allrecipes_recipe_alllink_data.csv", mode="a", index=True, header=False)

        return count_relevant_recipe
    except:
        print("Error occured")
        # Reopen Chrome Browser
        driver.quit()
        driver = webdriver.Chrome(options=webdriver.ChromeOptions())
        driver.maximize_window()
        return a_get_recipe_link_from_one_xml(driver, xml_link, count_recipe, first_xml, initial_webscraped_data_directory)



def a_get_recipe_link_from_all_xml(driver, xml_links, initial_webscraped_data_directory):
    """Looping through all xml links to get recipe links with pad-thai in the link address"""
    count_recipe = 0
    first_xml = True
    count_xml = -1

    for xml_link in xml_links:
        count_xml += 1
        print("\n", xml_link)
        count_recipe = a_get_recipe_link_from_one_xml(driver, xml_link, count_recipe, first_xml, initial_webscraped_data_directory)
        first_xml = False
    return count_recipe



def a_get_ingredients_from_one_recipe_link(recipe_link, recipe_id, first_recipe, recipe_data_csv_name, ingredient_data_csv_name):
    """Retrieve ingredient data from a recipe URL"""
    try:
        # Open Chrome Browser and go to recipe URL
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        driver.get(recipe_link)
        driver.implicitly_wait(10)

        # Wait for the ingredient section to be present
        ingredient_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ratings-histogram__rows"))
        )

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        overall_recipe_info = soup.find("article", id="allrecipes-article_1-0")

        # Find recipe name and creator name
        recipe_name = overall_recipe_info.find("div", id="article-header--recipe_1-0").h1.getText().strip()
        recipe_creator_name = overall_recipe_info.find("span", id="mntl-bylines__item_1-0").getText().strip()

        try:
            # Find number of reviewers
            recipe_num_of_reviewers_string = overall_recipe_info.find("div", id="mm-recipes-review-bar__rating-count_1-0").getText().strip()
            recipe_num_of_reviewers = int(recipe_num_of_reviewers_string[1:-1])

            # Find ratings
            recipe_ratings_info = soup.findAll("div", class_="ratings-histogram__row")
            recipe_ratings = 0.0
            sum_ratings_level_mul_count = 0
            ratings_level = 5

            for CurrentRatingsLevel in recipe_ratings_info:
                if CurrentRatingsLevel.find("span", class_="ratings-histogram__count"):
                    ratings_count = int(CurrentRatingsLevel.find("span", class_="ratings-histogram__count").getText().strip())
                    sum_ratings_level_mul_count += ratings_count * ratings_level
                ratings_level -= 1

            recipe_ratings = sum_ratings_level_mul_count / recipe_num_of_reviewers
        except:
            return None

        # Print all relevant data for this recipe
        print(recipe_name)
        print(recipe_creator_name)
        print(recipe_ratings)
        print(recipe_num_of_reviewers)

        # Create dataframe for this recipe
        recipe_generic_data = pd.DataFrame([recipe_id, recipe_name, recipe_creator_name, recipe_ratings, recipe_num_of_reviewers, "", recipe_link], index=["recipe_id", "recipe_name", "recipe_creator_name", "recipe_ratings", "recipe_num_of_reviewers", "recipe_num_saved", "recipe_link"]).T

        # Find number of ingredients
        ingredient_info = soup.find("div", id="mm-recipes-structured-ingredients_1-0")
        ingredient_list = ingredient_info.findAll("li")
        recipe_id_list, ingredient_name_list, ingredient_amount_list, ingredient_unit_list, ingredient_remainder_list = [], [], [], [], []
        print("Number of Ingredients: ", len(ingredient_list))

        # Find ingredient name, amount, and unit
        if ingredient_list is not None:
            for CurrentIngredient in ingredient_list:

                ingredient_name, ingredient_amount, ingredient_unit, ingredient_remainder = "", "", "", ""
                if CurrentIngredient.find("span", attrs={"data-ingredient-name": "true"}):
                    ingredient_name = CurrentIngredient.find("span", attrs={"data-ingredient-name": "true"}).getText().strip()
                if CurrentIngredient.find("span", attrs={"data-ingredient-quantity": "true"}):
                    ingredient_amount = CurrentIngredient.find("span", attrs={"data-ingredient-quantity": "true"}).getText().strip()
                    ingredient_amount = a_convert_fraction_string_to_float(ingredient_amount)
                if CurrentIngredient.find("span", attrs={"data-ingredient-unit": "true"}):
                    ingredient_unit = CurrentIngredient.find("span", attrs={"data-ingredient-unit": "true"}).getText().strip()
                
                # Append new ingredient to the existing ingredient data
                recipe_id_list.append(recipe_id)
                ingredient_name_list.append(ingredient_name)
                ingredient_amount_list.append(ingredient_amount)
                ingredient_unit_list.append(ingredient_unit)
                ingredient_remainder_list.append("")

            # Create dataframe for ingredients of this recipe
            ingredient_data = pd.DataFrame([recipe_id_list, ingredient_name_list, ingredient_amount_list, ingredient_unit_list, ingredient_remainder_list], index=["recipe_id","ingredient_name","ingredient_amount","ingredient_unit","ingredient_remainder"]).T
            
            # Save recipe and ingredient data into CSV
            if recipe_ratings > 0.0:
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
            page_not_found = soup.find("div", id="mntl-not-found-content_1-0")
            if page_not_found is not None:
                print("Recipe does not exist")
                return None
        except:
            # Reopen Chrome Browser if error
            driver.quit()
            return a_get_ingredients_from_one_recipe_link(recipe_link, recipe_id, first_recipe, recipe_data_csv_name, ingredient_data_csv_name)



def a_convert_fraction_string_to_float(fraction_string):
    """Convert string of fraction in ingredient amount, such as 1/2 and 1/3 ounce, into float"""
    resulting_float = 0.0
    for s in fraction_string.split():
        if len(s) == 1:
            if unicodedata.name(s).startswith('VULGAR FRACTION'):
                resulting_float += unicodedata.numeric(s)
            else:
                resulting_float += float(Fraction(s))
        else:
            resulting_float += float(Fraction(s))
    return resulting_float



def a_get_ingredients_from_recipe_list_from_xml(initial_webscraped_data_directory, webscraped_data_directory):
    """Get ingredient data for the recipe links from XML"""
    recipe_alllink_data = pd.read_csv(f"{initial_webscraped_data_directory}allrecipes_recipe_alllink_data.csv")

    recipe_data_csv_name = f"{webscraped_data_directory}allrecipes_recipe_data.csv"
    ingredient_data_csv_name = f"{webscraped_data_directory}allrecipes_ingredient_data.csv"
    first_recipe = True
    count_recipe = 0

    # Loop through all recipes in the list
    for ind in recipe_alllink_data.index:
        current_recipe_link = recipe_alllink_data["recipe_link"][ind]
        count_recipe += 1
        print("\nRecipe ID: ",count_recipe)
        print("Link no: ", ind)
        current_recipe_ratings = a_get_ingredients_from_one_recipe_link(current_recipe_link, count_recipe, first_recipe, recipe_data_csv_name, ingredient_data_csv_name)
        if current_recipe_ratings is None:
            count_recipe -= 1
            print("Recipe Link: ", current_recipe_link)
            print("Skipped. There is no ratings for this recipe, or page not found.")
        if count_recipe >= 1:
            first_recipe = False
    return