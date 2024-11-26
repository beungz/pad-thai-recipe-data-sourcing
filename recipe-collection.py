import numpy as np
import pandas as pd
from scrape_yummly import y_open_chrome, y_create_recipe_list_from_search, y_create_xml_list, y_get_recipe_link_from_all_xml, y_get_ingredients_from_recipe_list_from_search, y_get_ingredients_from_recipe_list_from_xml, y_get_ingredients_from_one_recipe_link
from scrape_allrecipes import a_open_chrome, a_create_xml_list, a_get_recipe_link_from_all_xml, a_get_ingredients_from_recipe_list_from_xml, a_get_ingredients_from_one_recipe_link



def load_data(webscraped_data_directory, manual_input_directory):
    '''Load nine CSV and return nine dataframes for use in other functions'''
    # Read the CSV into the dataframe
    try:
        df_Y_recipe = pd.read_csv(f"{webscraped_data_directory}yummly_recipe_data.csv")
        df_A_recipe = pd.read_csv(f"{webscraped_data_directory}allrecipes_recipe_data.csv")

        df_Y_ingredient = pd.read_csv(f"{webscraped_data_directory}yummly_ingredient_data.csv")
        df_A_ingredient = pd.read_csv(f"{webscraped_data_directory}allrecipes_ingredient_data.csv")

        df_ingredient_manual_edit = pd.read_csv(f"{manual_input_directory}ingredient_manual_edit.csv")
        df_ingredient_name_mapping = pd.read_csv(f"{manual_input_directory}ingredient_name_mapping.csv")
        df_ingredient_category_mapping = pd.read_csv(f"{manual_input_directory}ingredient_category_mapping.csv")
        df_ingredient_unit_mapping = pd.read_csv(f"{manual_input_directory}ingredient_unit_mapping.csv")
        df_unit_conversion = pd.read_csv(f"{manual_input_directory}unit_conversion.csv")
        return df_Y_recipe, df_A_recipe, df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion 
    except Exception as err:
        print(f"Error occurred: {err}")



def create_combined_recipe(df_Y_recipe, df_A_recipe, final_dataset_directory):
    '''Create combined_recipe.csv as part of the final dataset, and return relevant dataframe'''
    # Reformat the recipe_id by adding leading "Y" for recipes from Yummly, and leading "A" for recipes from Allrecipes
    df_Y_recipe['recipe_id'] = "Y" + df_Y_recipe['recipe_id'].astype(str).str.zfill(3)
    df_A_recipe['recipe_id'] = "A" + df_A_recipe['recipe_id'].astype(str).str.zfill(3)

    # For recipe dataframes, rename spare columns with "recipe_source", and set recipe_source to either "yummly" or "allrecipes"
    df_Y_recipe.rename(columns={'Unnamed: 0': 'recipe_source'}, inplace=True)
    df_A_recipe.rename(columns={'Unnamed: 0': 'recipe_source'}, inplace=True)

    df_Y_recipe['recipe_source'] = "yummly"
    df_A_recipe['recipe_source'] = "allrecipes"

    # Calculate weighted average of ratings, with number of reviewer (recipe_num_of_reviewers) as a weight; Normalize review scores for each website (recipe source) with its own mean, and max = 5, min = 1 (max and min for both website, that all users can give in the review)
    Y_WAR = sum(df_Y_recipe['recipe_ratings'] * df_Y_recipe['recipe_num_of_reviewers'])/df_Y_recipe['recipe_num_of_reviewers'].sum()
    A_WAR = sum(df_A_recipe['recipe_ratings'] * df_A_recipe['recipe_num_of_reviewers'])/df_A_recipe['recipe_num_of_reviewers'].sum()

    # Calculate new normalized ratings, by subtracting weighted average of ratings from the original ratings, then dividing by 4 (=range of scores, from 1 to 5)
    # This results in new ratings ranging from -1 to 1. 
    # After that, rescale them by adding 1 and dividing it by 2, in order to get new ratings ranging from 0 to 1
    df_Y_recipe['recipe_ratings_normalized'] = ((df_Y_recipe['recipe_ratings'] - Y_WAR)/(5-1)+1)/2
    df_A_recipe['recipe_ratings_normalized'] = ((df_A_recipe['recipe_ratings'] - A_WAR)/(5-1)+1)/2

    # Merge the two recipe dataframes into single recipe dataframe
    df_combined_recipe = pd.concat([df_Y_recipe, df_A_recipe], ignore_index=True)

    # Save df_combined_recipe into CSV file
    df_combined_recipe.to_csv(f"{final_dataset_directory}combined_recipe.csv")
    return df_combined_recipe



def create_combined_ingredient(df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion, final_dataset_directory):
    '''Create combined_ingredient.csv as part of the final dataset, and return relevant dataframe'''
    # Reformat the recipe_id by adding leading "Y" for recipes from Yummly, and leading "A" for recipes from Allrecipes
    df_Y_ingredient['recipe_id'] = "Y" + df_Y_ingredient['recipe_id'].astype(str).str.zfill(3)
    df_A_ingredient['recipe_id'] = "A" + df_A_ingredient['recipe_id'].astype(str).str.zfill(3)

    # For ingredient dataframes, rename spare columns with "ingredient_id", and set ingredient_id equal to {recipe_id}_{current ingredient no}
    df_Y_ingredient.rename(columns={'Unnamed: 0': 'ingredient_id'}, inplace=True)
    df_A_ingredient.rename(columns={'Unnamed: 0': 'ingredient_id'}, inplace=True)

    df_Y_ingredient['ingredient_id'] = df_Y_ingredient['recipe_id'] + "_" + df_Y_ingredient['ingredient_id'].astype(str).str.zfill(2)
    df_A_ingredient['ingredient_id'] = df_A_ingredient['recipe_id'] + "_" + df_A_ingredient['ingredient_id'].astype(str).str.zfill(2)

    # For ingredient dataframes, add a new column "recipe_source", and set recipe_source to either "yummly" or "allrecipes"
    df_Y_ingredient['recipe_source'] = "yummly"
    df_A_ingredient['recipe_source'] = "allrecipes"

    # Merge the two ingredient dataframes into single ingredient dataframe
    df_combined_ingredient = pd.concat([df_Y_ingredient, df_A_ingredient], ignore_index=True)

    # Clean the ingredient name in the ingredient dataframe, by trimming (strip), and make them all lowercase
    df_combined_ingredient['ingredient_name'] = df_combined_ingredient['ingredient_name'].astype(str).str.lower()
    df_combined_ingredient['ingredient_name'] = df_combined_ingredient['ingredient_name'].astype(str).str.strip()

    # Rename ingredient_amount and ingredient_unit to original_ingredient_amount and original_ingredient_unit, respectively
    df_combined_ingredient.rename(columns={'ingredient_amount': 'original_ingredient_amount'}, inplace=True)
    df_combined_ingredient.rename(columns={'ingredient_unit': 'original_ingredient_unit'}, inplace=True)

    # Mapping ingredient_name with common name, and assign ingredient_category, from two mapping tables

    # Overwrite ingredient name with new name from df_ingredient_manual_edit
    df_ingredient_new_name = df_ingredient_manual_edit.drop(["ingredient_amount", "ingredient_unit"], axis=1, inplace=False)
    df_ingredient_new_name.dropna(subset=["ingredient_name"], inplace=True)

    for index, row in df_ingredient_new_name.iterrows():
        df_combined_ingredient.loc[df_combined_ingredient['ingredient_id'] == row['ingredient_id'], ['ingredient_name']] = row['ingredient_name']

    # Add ingredient amount/unit as new_ingredient_amount/new_ingredient_unit from df_ingredient_manual_edit
    df_combined_ingredient['new_ingredient_amount'] = df_combined_ingredient['original_ingredient_amount']
    df_combined_ingredient['new_ingredient_unit'] = df_combined_ingredient['original_ingredient_unit']

    df_ingredient_new_amount = df_ingredient_manual_edit.drop(["ingredient_name"], axis=1, inplace=False)
    df_ingredient_new_amount.dropna(subset=["ingredient_amount", "ingredient_unit"], inplace=True)

    for index, row in df_ingredient_new_amount.iterrows():
        df_combined_ingredient.loc[df_combined_ingredient['ingredient_id'] == row['ingredient_id'], ['new_ingredient_amount']] = row['ingredient_amount']
        df_combined_ingredient.loc[df_combined_ingredient['ingredient_id'] == row['ingredient_id'], ['new_ingredient_unit']] = row['ingredient_unit']

    # Map ingredient_name with common name from df_ingredient_name_mapping
    df_combined_ingredient['common_ingredient_name'] = ""

    for index, row in df_ingredient_name_mapping.iterrows():
        df_combined_ingredient.loc[df_combined_ingredient['ingredient_name'] == row['original_ingredient_name'], ['common_ingredient_name']] = row['common_ingredient_name']

    # Assign ingredient category to each ingredient, by using df_ingredient_category_mapping
    df_combined_ingredient['ingredient_category'] = ""
    df_combined_ingredient['default_unit'] = ""

    for index, row in df_ingredient_category_mapping.iterrows():
        df_combined_ingredient.loc[df_combined_ingredient['common_ingredient_name'] == row['common_ingredient_name'], ['ingredient_category']] = row['ingredient_category']
        df_combined_ingredient.loc[df_combined_ingredient['common_ingredient_name'] == row['common_ingredient_name'], ['default_unit']] = row['default_unit']

    # Map new_ingredient_unit with mapped_unit from df_ingredient_unit_mapping
    for index, row in df_ingredient_unit_mapping.iterrows():
        df_combined_ingredient.loc[df_combined_ingredient['new_ingredient_unit'] == row['ingredient_unit'], ['new_ingredient_unit']] = row['mapped_unit']

    # Fill NaN in new_ingredient_unit with default_unit
    df_combined_ingredient['new_ingredient_unit'] = df_combined_ingredient['new_ingredient_unit'].fillna(df_combined_ingredient['default_unit'])

    # Convert new_ingredient_amount from new_ingredient_unit to default_unit
    for index, row in df_unit_conversion.iterrows():
        df_combined_ingredient.loc[(df_combined_ingredient['new_ingredient_unit'] == row['unit_X']) & (df_combined_ingredient['default_unit'] == row['unit_Y']), ['new_ingredient_amount']] *= row['equivalent_Y_for_oneX']
        df_combined_ingredient.loc[(df_combined_ingredient['new_ingredient_unit'] == row['unit_X']) & (df_combined_ingredient['default_unit'] == row['unit_Y']), ['new_ingredient_unit']] = row['unit_Y']

    # Save df_combined_ingredient into CSV file
    df_combined_ingredient.to_csv(f"{final_dataset_directory}combined_ingredient.csv")
    return df_combined_ingredient


def create_reformatted_combined_ingredient(df_combined_recipe, df_combined_ingredient, df_ingredient_category_mapping, final_dataset_directory):
    '''Create the remaining three files for final dataset: reformatted_combined_ingredient.csv, top30.csv, top10.csv'''
    # Create a new dataframe with all ingredients and top 30 ingredients, for preliminary analysis
    df_ingredient_all = df_combined_recipe.drop(["recipe_creator_name", "recipe_num_of_reviewers", "recipe_num_saved", "recipe_link"], axis=1, inplace=False)
    df_ingredient_all.set_index('recipe_id')
    df_ingredient_top30 = df_ingredient_all
    df_combined_ingredient_compact = df_combined_ingredient.drop(["ingredient_id", "ingredient_name", "original_ingredient_amount", "original_ingredient_unit", "ingredient_remainder", "recipe_source", "new_ingredient_unit", "ingredient_category", "default_unit"], axis=1, inplace=False)

    # Calculate the recipe count for each ingredient, then sort them by recipe count (descending)
    df_ingredient_category_mapping['recipe_count'] = 0
    for index, row in df_ingredient_category_mapping.iterrows():
        df_ingredient_category_mapping.loc[df_ingredient_category_mapping['common_ingredient_name'] == row['common_ingredient_name'], 'recipe_count'] = (df_combined_ingredient['common_ingredient_name'] == row['common_ingredient_name']).sum()

    df_ingredient_sorted_recipe_count = df_ingredient_category_mapping.sort_values(by='recipe_count', ascending=False)
    df_ingredient_sorted_recipe_count.reset_index(inplace=True)
    df_ingredient_sorted_recipe_count.drop(['index'], axis=1, inplace=True)
    all_ingredient_list = df_ingredient_sorted_recipe_count['common_ingredient_name']

    # Save the recipe count data for each ingredient into CSV
    df_ingredient_sorted_recipe_count.to_csv(f"{final_dataset_directory}ingredient_sorted_recipe_count.csv")

    # Update df_ingredient_all dataframe with new_ingredient_amount from df_combined_ingredient_compact
    blank_columns_1 = pd.DataFrame(np.nan, index=df_ingredient_all.index, columns=all_ingredient_list)
    df_ingredient_all = pd.concat([df_ingredient_all, blank_columns_1], axis=1)
    for current_ingredient in all_ingredient_list:
        new_df = df_combined_ingredient_compact.loc[df_combined_ingredient_compact['common_ingredient_name'] == current_ingredient, ['recipe_id', 'new_ingredient_amount']]
        new_df.rename(columns={'new_ingredient_amount': current_ingredient}, inplace=True)
        new_df.set_index('recipe_id')
        merged_df = pd.merge(df_ingredient_all, new_df, on='recipe_id', how='left', suffixes=('', '_updated'))
        df_ingredient_all[current_ingredient] = merged_df[current_ingredient + '_updated'].combine_first(merged_df[current_ingredient])

    # Save the top 30 ingredient data into CSV
    df_ingredient_all.to_csv(f"{final_dataset_directory}reformatted_combined_ingredient.csv")

    # Get a list of top 30 ingredients, by number recipes that used these ingredients
    top_30_ingredients = df_ingredient_sorted_recipe_count.head(30)['common_ingredient_name']
    ingredients_from_11_to_30 = df_ingredient_sorted_recipe_count.iloc[10:30]['common_ingredient_name']

    # Update df_ingredient_top30 dataframe with new_ingredient_amount from df_combined_ingredient_compact
    blank_columns_2 = pd.DataFrame(np.nan, index=df_ingredient_top30.index, columns=top_30_ingredients)
    df_ingredient_top30 = pd.concat([df_ingredient_top30, blank_columns_2], axis=1)
    for current_ingredient in top_30_ingredients:
        new_df = df_combined_ingredient_compact.loc[df_combined_ingredient_compact['common_ingredient_name'] == current_ingredient, ['recipe_id', 'new_ingredient_amount']]
        new_df.rename(columns={'new_ingredient_amount': current_ingredient}, inplace=True)
        new_df.set_index('recipe_id')
        merged_df = pd.merge(df_ingredient_top30, new_df, on='recipe_id', how='left', suffixes=('', '_updated'))
        df_ingredient_top30[current_ingredient] = merged_df[current_ingredient + '_updated'].combine_first(merged_df[current_ingredient])

    # Save the top 30 ingredient data into CSV
    df_ingredient_top30.to_csv(f"{final_dataset_directory}top30.csv")

    # Remove 11th-30th ingredient from the top 30 to get df_ingredient_top10. Save the top 10 ingredient data into CSV
    df_ingredient_top10 = df_ingredient_top30.drop(ingredients_from_11_to_30, axis=1, inplace=False)
    df_ingredient_top10.to_csv(f"{final_dataset_directory}top10.csv")
    return df_ingredient_all



def test_load_data():
    '''Test loading data from CSV, by checking if data in relevant dataframe aligned with expectation'''
    webscraped_data_directory = "final_result_from_webscraping/"
    manual_input_directory = "manual_input_for_mapping_conversion/"
    df_Y_recipe, df_A_recipe, df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion = load_data(webscraped_data_directory, manual_input_directory)
    assert [(df_Y_recipe['recipe_ratings'].mean().astype(float) <= 5) & (df_A_recipe['recipe_id'].max().astype(float) > 10) & 
            (df_Y_ingredient['ingredient_amount'].max().astype(float) > 0) & (df_A_ingredient['ingredient_amount'].max().astype(float) > 0) &
            (df_ingredient_manual_edit['ingredient_amount'].max().astype(float) > 0) &
            (df_ingredient_name_mapping.loc[df_ingredient_name_mapping['original_ingredient_name'] == 'fish sauce', 'common_ingredient_name'] == 'fish sauce') &
            (df_ingredient_category_mapping.loc[df_ingredient_category_mapping['common_ingredient_name'] == 'fish sauce', 'ingredient_category'] == 'sauce / salt') &
            (df_ingredient_unit_mapping.loc[df_ingredient_unit_mapping['ingredient_unit'] == 'oz.', 'mapped_unit'] == 'ounce') &
            (df_unit_conversion.loc[(df_unit_conversion['unit_X'] == 'cup') & (df_unit_conversion['unit_Y'] == 'tablespoon'), 'equivalent_Y_for_oneX'] == 16)]
    
def test_create_combined_recipe():
    '''Test creating combined_recipe, by checking if normalized ratings in returned dataframe is equal or less than 1'''
    webscraped_data_directory = "final_result_from_webscraping/"
    manual_input_directory = "manual_input_for_mapping_conversion/"
    final_dataset_directory = "final_dataset_for_kaggle/"
    df_Y_recipe, df_A_recipe, df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion = load_data(webscraped_data_directory, manual_input_directory)
    df_combined_recipe = create_combined_recipe(df_Y_recipe, df_A_recipe, final_dataset_directory)
    assert (df_combined_recipe['recipe_ratings_normalized'].max().astype(float) <= 1)

def test_create_combined_ingredient():
    '''Test creating combined_ingredient, by checking if max of new_ingredient_amount is positive'''
    webscraped_data_directory = "final_result_from_webscraping/"
    manual_input_directory = "manual_input_for_mapping_conversion/"
    final_dataset_directory = "final_dataset_for_kaggle/"
    df_Y_recipe, df_A_recipe, df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion = load_data(webscraped_data_directory, manual_input_directory)
    df_combined_ingredient = create_combined_ingredient(df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion, final_dataset_directory)
    assert (df_combined_ingredient['new_ingredient_amount'].max().astype(float) > 0)

def test_create_reformatted_combined_ingredient():
    '''Test creating combined_ingredient, by checking if max of new_ingredient_amount is positive'''
    webscraped_data_directory = "final_result_from_webscraping/"
    manual_input_directory = "manual_input_for_mapping_conversion/"
    final_dataset_directory = "final_dataset_for_kaggle/"
    df_Y_recipe, df_A_recipe, df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion = load_data(webscraped_data_directory, manual_input_directory)
    df_combined_recipe = create_combined_recipe(df_Y_recipe, df_A_recipe, final_dataset_directory)
    df_combined_ingredient = create_combined_ingredient(df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion, final_dataset_directory)
    df_ingredient_all = create_reformatted_combined_ingredient(df_combined_recipe, df_combined_ingredient, df_ingredient_category_mapping, final_dataset_directory)
    assert (df_ingredient_all['peanut'].max().astype(float) > 0)

def test_y_open_chrome():
    '''Test opening Chrome, go to the search page of Yummly.com and check if the number of recipes is more than 10'''
    driver, num_of_recipe = y_open_chrome()
    driver.quit()
    assert (num_of_recipe > 10)

def test_a_open_chrome():
    '''Test opening Chrome and check if the driver is ok by going to google.com'''
    driver = a_open_chrome()
    driver.get('https://www.google.com')
    web_title = driver.title
    driver.quit()
    assert (web_title)

def test_y_get_ingredients_from_one_recipe_link():
    '''Test getting ingredient and recipe data from a recipe link'''
    recipe_link ='https://www.yummly.com/recipe/Chicken-Pad-Thai-2213155'
    recipe_id = 1
    recipe_data_csv_name = "test_y_recipe_data.csv"
    ingredient_data_csv_name = "test_y_ingredient_data.csv"
    first_recipe = True
    recipe_ratings = y_get_ingredients_from_one_recipe_link(recipe_link, recipe_id, None, first_recipe, recipe_data_csv_name, ingredient_data_csv_name)
    assert (recipe_ratings <= 5)

def test_a_get_ingredients_from_one_recipe_link():
    '''Test getting ingredient and recipe data from a recipe link'''
    recipe_link ='https://www.allrecipes.com/recipe/19306/sukhothai-pad-thai/'
    recipe_id = 1
    recipe_data_csv_name = "test_a_recipe_data.csv"
    ingredient_data_csv_name = "test_a_ingredient_data.csv"
    first_recipe = True
    recipe_ratings = a_get_ingredients_from_one_recipe_link(recipe_link, recipe_id, first_recipe, recipe_data_csv_name, ingredient_data_csv_name)
    assert (recipe_ratings <= 5)



def main():
    """Perform webscraping on Yummly.com and Allrecipes.com to get Pad Thai recipes, reorganize/clean the data, transform data as needed, and return the final Pad Thai Recipe Dataset"""
    initial_webscraped_data_directory = "initial_file_from_webscraping/"
    webscraped_data_directory = "final_result_from_webscraping/"
    manual_input_directory = "manual_input_for_mapping_conversion/"
    final_dataset_directory = "final_dataset_for_kaggle/"
    
    """Webscraping on Yummly.com"""
    # Open Chrome, go to search page, determine overall number of relevant recipes, and return driver
    driver, num_of_recipe = y_open_chrome()
    # Get the list of recipe from search
    y_create_recipe_list_from_search(driver, initial_webscraped_data_directory)
    # Get list of xml links from the site map
    xml_links = y_create_xml_list(driver, initial_webscraped_data_directory)
    # Looping through all xml links to get recipe links with pad-thai in the link address
    y_get_recipe_link_from_all_xml(driver, xml_links, initial_webscraped_data_directory)
    # Get ingredient data for the recipes from the search result
    y_get_ingredients_from_recipe_list_from_search(initial_webscraped_data_directory, webscraped_data_directory)
    # Get ingredient data for the recipe links from XML
    y_get_ingredients_from_recipe_list_from_xml(initial_webscraped_data_directory, webscraped_data_directory)

    """Webscraping on Allrecipes.com"""
    # Open Chrome and return driver
    driver = a_open_chrome()
    # Get list of xml links from the site map
    xml_links = a_create_xml_list(driver, initial_webscraped_data_directory)
    # Looping through all xml links to get recipe links with pad-thai in the link address
    a_get_recipe_link_from_all_xml(driver, xml_links, initial_webscraped_data_directory)
    # Get ingredient data for the recipe links from XML
    a_get_ingredients_from_recipe_list_from_xml(initial_webscraped_data_directory, webscraped_data_directory)

    """Combine recipes/ingredients from two websites (Yummly & Allrecipes)""" 
    # Load data from CSV file into nine dataframes
    df_Y_recipe, df_A_recipe, df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion = load_data(webscraped_data_directory, manual_input_directory)
    
    # Create two files for final dataset: combined_recipe.csv and combined_ingredient.csv, and return two relevant dataframes
    df_combined_recipe = create_combined_recipe(df_Y_recipe, df_A_recipe, final_dataset_directory)
    df_combined_ingredient = create_combined_ingredient(df_Y_ingredient, df_A_ingredient, df_ingredient_manual_edit, df_ingredient_name_mapping, df_ingredient_category_mapping, df_ingredient_unit_mapping, df_unit_conversion, final_dataset_directory)

    # Create the remaining three files for final dataset: reformatted_combined_ingredient.csv, top30.csv, top10.csv
    create_reformatted_combined_ingredient(df_combined_recipe, df_combined_ingredient, df_ingredient_category_mapping, final_dataset_directory)



if __name__ == '__main__':
	main()