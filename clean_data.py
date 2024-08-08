import pandas as pd


file_path = 'your_file_path/CSL_1_U.xlsx' 
df_shearing = pd.read_excel(file_path, sheet_name='03 - Shearing', header=[9, 10])


df_shearing.columns = [' '.join(col).strip() for col in df_shearing.columns.values]

row_11_time_start = df_shearing.iloc[1]['Unnamed: 1_level_0 Time start of test']
row_12_shear_data = df_shearing.iloc[2][[
    'Unnamed: 23_level_0 Shear induced PWP',
    'Unnamed: 11_level_0 Axial strain',
    'Unnamed: 13_level_0 Volumetric strain',
    'Unnamed: 20_level_0 Excess PWP',
    "Unnamed: 19_level_0 p'",
    'Unnamed: 16_level_0 Deviator stress',
    'Unnamed: 22_level_0 Void ratio'
]]

print("Time start of test (Row 11):", row_11_time_start)
print("Shear data (Row 12):")
print(row_12_shear_data)