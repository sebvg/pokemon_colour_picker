# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 17:47:33 2021

@author: sebas
"""

#Renames pokemon data to names instead of IDs.

import os
import pandas as pd

df = pd.DataFrame(os.listdir("D:\pokemon_colour_picker\pokemon_images"),columns=["file name"])
df["id"] = df["file name"].str.extract("(\d+)").astype(int)
df["qualifier"] = df["file name"].str.extract("\d+(.*)\.").fillna("").astype(str)
df.loc[df["qualifier"] != "", "delim"] = "-"

pokemon_names = pd.read_csv("pokemon.csv")["name"]

df["name"] = [pokemon_names[i-1] for i in df["id"]]
df["new file name"] = df["name"] + df["qualifier"] + ".png"


for i in range(len(df)):
    os.rename("pokemon_images/" + df["file name"][i], 
              "pokemon_images/" + df["new file name"][i])