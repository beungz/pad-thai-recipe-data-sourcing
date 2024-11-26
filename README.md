# Pad Thai Recipe Dataset: Data Sourcing Code
### **Author**: Matana Pornluanprasert<br>
### **Date**: 26 November 2024<br>

This is a data sourcing code that collect Pad Thai recipe data from two food recipe portal websites, Yummly.com and Allrecipes.com, in their recipe and review section, where creators posted their own recipes publicly and let other users give review scores. The scraped data was organized and cleaned first before consolidating into a single dataset.<br>

Normalized ratings are calculated in order to facilitate comparison of ratings from two different recipe sources, because the mean of ratings from the two websites are different. For example, ratings given by a website with a lot of food experts may be lower compared to a website targeting beginners.<br>

There are some missing data in original ingredient amount/unit from the sources and are intentionally left missing as it is. The new ingredient unit utilitzed default unit, to fill in missing ingredient units.<br>

Unit conversion has been applied such that all similar ingredients used the same default_unit, where possible.<br>

Name of the same ingredient may be different from one recipe to another as it has several alternative names in English (and other languages), so the mapping table of the ingredient name is used to map these alternative names to common name.<br>

Ingredient category is provided as an alternative to common ingredient names. There are over 178 ingredients in the dataset (608 for original ingredient names), while the number of ingredient category is just 27.<br>

### **Data Sources**:<br>
Recipe data was scraped from the following websites:
- [Yummly](https://www.yummly.com)
- [Allrecipes](https://www.allrecipes.com)

The dataset includes information such as recipe names, ingredients, and creator names, which were originally posted by the users of these platforms. Please refer to the list of creators provided in combined_recipe.csv<br>

### **License for the Dataset**:<br>
The dataset is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to use, modify, and distribute this dataset for non-commercial purposes, provided that you give appropriate credit to the author.<br>

### **License for Data Sourcing Code**:<br>
The data sourcing code in this repository is licensed under the [MIT License](https://opensource.org/licenses/MIT).<br>

### **Important Disclaimer**:<br>
The dataset itself is provided for **research and educational purposes only**. Users of this dataset should be mindful of the **terms of service** and **intellectual property rights** of **Yummly.com** and **Allrecipes.com** when using this data.<br>
<br>
***

# Requirements and How to run the code

### **Requirements**:<br>
```
numpy==2.1.3
pandas==2.2.3
matplotlib==3.9.2
seaborn==0.13.2
requests==2.31.0
beautifulsoup4==4.12.3
selenium==4.25.0
pytest==8.3.3
```
<br>

### **How to run the code**:<br>
***
To run the code, type the followings in the terminal<br>

On Windows:<br>

```
py recipe-collection.py
```

On other systems:<br>

```
python recipe-collection.py
```
<br>

### **Unit Test**
***

Run `pytest`<br>

```
pytest recipe-collection.py
```

This will run 8 test functions in recipe-collection<br>
<br>
***

# Dataset Structure
There are four main directories, which used to keep data in different stages of the data collection process. The final dataset can be located in folder **final_dataset_for_kaggle**

| Folder                                   | Description     |
|------------------------------------------|-----------------|
| 1. initial_file_from_webscraping         | Files generated from the data sourcing code, primarily store links to recipes, and xml links generated from sitemap. It also includes temporary recipe data from search on Yummly.com, which is used later to produce the final result. |
| 2. final_result_from_webscraping         | Recipe data and ingredient data from the two websites, before consolidation |
| 3. manual_input_for_mapping_conversion   | Manual input files used to map ingredient name to common name, map measurement unit to common unit, convert unit, map common ingredient name to ingredient category, and provide manual overrides/revisions to the ingredient name/amount/unit |
| 4. final_dataset_for_kaggle              | Final dataset, which includes consolidated recipe data, ingredient data, reformatted ingredient data, top 30 ingredients, top 10 ingredients, and recipe count for each ingredient |
<br>

### **1. initial_file_from_webscraping**<br>

| File         | Description     |
|--------------|-----------------|
| yummly_xml_link_data.csv and allrecipes_xml_link_data.csv  | Files generated from the data sourcing code, to store xml links generated from sitemap. |
| yummly_recipe_alllink_data.csv and allrecipes_recipe_alllink_data.csv | Files generated from the data sourcing code, to store links to all recipes |
| yummly_recipe_data_from_search.csv | temporary recipe data from search on Yummly.com, which is used later to produce the final result |
<br>

### **2. final_result_from_webscraping**<br>

| File         | Description     |
|--------------|-----------------|
| yummly_recipe_data.csv and allrecipes_recipe_data.csv | Recipe data from the two websites, before consolidation |
| yummly_ingredient_data.csv and allrecipes_ingredient_data.csv | Ingredient data from the two websites, before consolidation |
<br>

### **3. manual_input_for_mapping_conversion**<br>

| File         | Description     |
|--------------|-----------------|
| ingredient_name_mapping.csv | Manual input files used to map ingredient name to common name |
| ingredient_unit_mapping.csv | Manual input files used to map measurement unit to common unit |
| unit_conversion.csv | Manual input files used to perform unit conversion |
| ingredient_category_mapping.csv | Manual input files used to map common ingredient name to ingredient category |
| ingredient_manual_edit.csv | Manual input files used to provide manual overrides/revisions to the ingredient name/amount/unit |
<br>

### **4. final_dataset_for_kaggle**<br>

| File         | Description     |
|--------------|-----------------|
| combined_recipe.csv | consolidated recipe data |
| combined_ingredient.csv | consolidated ingredient data |
| reformatted_combined_ingredient.csv, top30.csv, and top10.csv | reformatted ingredient data, top 30 ingredients, and top 10 ingredients |
| ingredient_sorted_recipe_count.csv | recipe count for each ingredient |
<br>

### **Column Description for the Final Dataset**<br>

| Column Name         | Description     |
|--------------|-----------------|
| recipe_id | unique id assigned to all recipe |
| recipe_source | source of the recipe: either yummly or allrecipes |
| recipe_name | recipe name given by the creator |
| recipe_creator_name | name of the recipe creator |
| recipe_ratings | average review scores as given by users on the two websites, in a scale from 1 to 5 |
| recipe_ratings_normalized | normalized score, with the mean and score range, with the final range from 0 to 1 |
| recipe_num_of_reviewers | number of reviewers who rate each recipe |
| recipe_num_saved | number of users on Yummly.com who saved the recipe for reading later |
| recipe_link | link to recipes |
| ingredient_id | unique id assigned to all ingredients (same ingredient but in different recipe > different ingredient_id)  |
| ingredient_name, original_ingredient_amount, original_ingredient_unit | original name, amount, and unit of ingredient on the websites |
| common_ingredient_name, new_ingredient_amount, new_ingredient_unit | common name, new (converted) amount, and new unit of ingredient after mapping/unit conversion and applying manual overrides |
| ingredient_category | category of ingredient  |
| ingredient_remainder | description attached to the ingredient, which include detail of ingredient and preparation instruction, available on Yummly.com  |
| default_unit | default unit which is used in final dataset for each ingredient type |
| columns with ingredient name | amount of ingredient used in each recipe, in reformatted_combined_ingredient.csv, top30.csv, and top10.csv |
<br>