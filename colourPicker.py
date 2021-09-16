# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 18:48:32 2021

@author: sebas
"""

#Ideas for using k-means clustering comes from: 
#https://www.geeksforgeeks.org/extract-dominant-colors-of-an-image-using-python/

from PIL import Image
import numpy as np
import pandas as pd
from scipy.cluster.vq import whiten, kmeans
import os
import PySimpleGUI as sg
import io
import pyperclip

def getColours(pokemon, k):
    path = "pokemon_images/" + pokemon + ".png"
    #Opening Image
    img = Image.open(path)
    
    #Flattening and converting to dataframe
    npArr = np.array(img)
    npArr = npArr.reshape((npArr.shape[0]*npArr.shape[1],4))
    df = pd.DataFrame(npArr, 
                      columns=['red','green','blue','a'])
    
    #Drop transparent values
    df = df[(df['a']!=0) | (df['red']!=0) | (df['green']!=0) | (df['blue']!=0)].reset_index(drop=True)
    
    #Scale colours by standard deviation as preparation for k-means clustering
    df["scaled red"] = whiten(df["red"])
    df["scaled green"] = whiten(df["green"])
    df["scaled blue"] = whiten(df["blue"])
    
    #Perform k means clusters
    cluster_centres, _ = kmeans(df[['scaled red',
                                                 'scaled green',
                                                 'scaled blue']], k)
    
    dominant_colours = []
    
    #Get standard deviations of each colour for de-normalizing
    red_std, green_std, blue_std = df[["red","green","blue"]].std()
    
    for cluster in cluster_centres:
        dominant_colours.append([int(cluster[0]*red_std),
                                 int(cluster[1]*green_std),
                                 int(cluster[2]*blue_std)])
    
    #Create image display of colour palette
    height = 80
    width = 400
    colWidth = int(width/k)
    #Make numpy array of image
    paletteImg = np.array([[[x]*colWidth for x in dominant_colours] for i in range(height)])
    #Reshape to n x m x k dimensions
    paletteImg = paletteImg.reshape((paletteImg.shape[0],paletteImg.shape[1]*paletteImg.shape[2],3))
    #Create image
    paletteImg = Image.fromarray(np.uint8(paletteImg))
    #Convert to bytes for PySimpleGUI Image display
    b = io.BytesIO()
    paletteImg.save(b,"png")
    paletteImgBytes = b.getvalue()
    
    #Convert colours to hex for tableau output
    hex_strings = []
    for colour in dominant_colours:
        temp = ""
        for rgb in colour:
            temp = temp + "0" * (2 - len(str(hex(rgb)).replace("0x",""))) + str(hex(rgb)).replace("0x","")
        hex_strings.append(temp)
        
    #Create tableau output xml tag
    header = "<color-palette name=\"" + pokemon + "\" type = \"regular\">"
    footer = "</color-palette>"
    xml = header
    for colour in hex_strings:
        xml = xml + "\n" + "<color>#" + colour + "</color>"
    xml = xml + "\n" + footer
    return paletteImgBytes, xml

#Create list of pokemon for drop-down menu
available_pokemon = [x.replace(".png","") for x in os.listdir("pokemon_images")]
available_pokemon.sort()

#Initial pokemon
pokemon = "Bulbasaur"

#Black line as initial image for colour range
testImage = Image.fromarray(np.uint8(np.zeros((1,250,3))))
b = io.BytesIO()
testImage.save(b, "png")
testBytes = b.getvalue()

layout = [[sg.Image("icon.png", size=(100,100)),
               sg.Text("Pokemon Colour Palette Picker",
                       font=("bold",16),
                       text_color="black",
                       background_color="white")],
          [sg.Text("Choose a pokemon",
                   text_color="black",
                   background_color="white"), 
               sg.Combo(available_pokemon, default_value=pokemon)],
          [sg.Text("Choose number of colours",
                   text_color="black",
                   background_color="white"), 
               sg.Spin([i for i in range(2,21)], initial_value=6)],
          [sg.Button("Go!")],
          [sg.Image(("pokemon_images/" + pokemon + ".png"), key="pokeImage",
                    background_color="white")],
          [sg.Image(testBytes, key="paletteImage", background_color="white")],
          [sg.InputText("", readonly=True, key="tableauXML"),
               sg.Button("Copy to clipboard")],
        ]


window = sg.Window("Pokemon Colour Palette", layout, background_color="white")
XML = ""
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == "Go!":
        pokemon = values[1]
        k = values[2]
        if pokemon in available_pokemon:
            paletteImg, XML = getColours(pokemon, k)
            window["tableauXML"].update(XML)
            newPokemonImg = Image.open("pokemon_images/" + pokemon + ".png")
            b = io.BytesIO()
            newPokemonImg.save(b, "png")
            newPokemonImgB = b.getvalue()
            window["pokeImage"].update(newPokemonImgB)
            window["paletteImage"].update(paletteImg)
        else:
            pass
    elif event == "Copy to clipboard":
        pyperclip.copy(XML)
    
window.close()