import pandas as pd

# List of words to pair with products
words = ['buy', 'price', 'discount', 'promotion', 'promo', 'shop', 'cheap', 'bargain', 'inexpensive', 'affordable']
# List of products to pair with words
products = ['sofas', 'convertible sofas', 'love seats', 'recliners', 'sofa beds']

# Create an empty list
keywords_list = []

# Loop through products
for product in products:
    # Loop through words
    for word in words:
        # Append combination
        keywords_list.append([product, product + ' ' + word])
        keywords_list.append([product, word + ' ' + product])
        
# Create a DataFrame from list
keywords_df = pd.DataFrame.from_records(keywords_list)

# Rename the columns of the DataFrame
keywords_df = keywords_df.rename(columns={0: "Ad Group", 1: "Keyword"})
# Add a campaign column

keywords_df.insert(0, 'Campaign','SEM_Sofas')
# Add a criterion type column

keywords_df.insert(3, 'Criterion Type','Exact')
# Make a copy of the keywords DataFrame

keywords_phrase = keywords_df.copy()
# Change criterion type match to phrase

keywords_phrase['Criterion Type'] = 'Phrase'
# Append the DataFrames

keywords_df_final = keywords_df.append(keywords_phrase, ignore_index=True)
# Save the final keywords to a CSV file

keywords_df_final.to_csv('keywords.csv', index = False)
# View a summary of our campaign work

summary = keywords_df_final.groupby(['Ad Group', 'Criterion Type'])['Keyword'].count()
print(summary)

# Looking at a summary of our campaign structure is good now that we've wrapped up our keyword work. We can do that by grouping by ad group and criterion type and counting by keyword.
# This summary shows us that we assigned specific keywords to specific ad groups, which are each part of a campaign. 
# In essence, we are telling Google (or Bing, etc.) that we want any of the words in each ad group to trigger one of the ads in the same ad group. 
# Separately, we will have to create another table for ads, which is a task for another day and would look something like this:

# Campaign	Ad Group	Headline 1	Headline 2	Description	Final URL
# SEM_Sofas	Sofas	Looking for Quality Sofas?	Explore Our Massive Collection	30-day Returns With Free Delivery Within the US. Start Shopping Now	DataCampSofas.com/sofas
# SEM_Sofas	Sofas	Looking for Affordable Sofas?	Check Out Our Weekly Offers	30-day Returns With Free Delivery Within the US. Start Shopping Now	DataCampSofas.com/sofas
# SEM_Sofas	Recliners	Looking for Quality Recliners?	Explore Our Massive Collection	30-day Returns With Free Delivery Within the US. Start Shopping Now	DataCampSofas.com/recliners
# SEM_Sofas	Recliners	Need Affordable Recliners?	Check Out Our Weekly Offers	30-day Returns With Free Delivery Within the US. Start Shopping Now DataCampSofas.com/recliners