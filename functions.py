import numpy as np
import pandas as pd
from plotly import graph_objs as go
from plotly import subplots


def load_data(fname1,fname2,fname3,fname4,fname5,fname6,fname7):

    # load data
    CY  = pd.read_csv(fname1,delimiter=';')
    NY  = pd.read_csv(fname2,delimiter=';')
    RNI = pd.read_csv(fname3,delimiter=';')
    UL  = pd.read_csv(fname4,delimiter=';')
    crop_char_sep = pd.read_csv(fname5,delimiter=',')
    crop_char  = pd.read_csv(fname6,delimiter=',')
    
    # crop_char_sep = crop_char_sep.values

    crop_char = crop_char.values
    mean_cover = crop_char[:,0]
    mean_structure = crop_char[:,1]
    mean_N_need = crop_char[:,2]


    CY = CY.values
    NY = NY.values
    for i in range(NY.shape[0]):
        for j in range(NY.shape[1]):
            NY[i,j] = float(NY[i,j].replace(',', '.'))

    RNI = RNI.values
    RNI = RNI.reshape(RNI.shape[1])
    for i in range(RNI.shape[0]):
        RNI[i] = float(RNI[i].replace(',', '.'))

    UL = UL.values
    UL = UL.reshape(UL.shape[1])
    for i in range(UL.shape[0]):
        UL[i] = float(UL[i].replace(',', '.'))
    df_cs = pd.read_csv(fname7,delimiter=',')

    return CY,NY,RNI,UL,crop_char_sep,crop_char,df_cs

def DefineSequenceNumber(df, df_cs):

    try:

        seqs =  []
        for i,row in df.iterrows():
            if (row['Crop 3'] == 'None') & (row['Crop 4'] == 'None'):
                seq =  df_cs.loc[(df_cs['Crop 1'] == row['Crop 1']) 
                                & (df_cs['Crop 2'] ==  row['Crop 2']) 
                                &  (df_cs['Crop 3'].isna()) 
                                & (df_cs['Crop 4'].isna())]['Sequences'].iloc[0]
                seq = int(seq.split()[-1]) - 1
            elif row['Crop 4'] == 'None':
                seq =  df_cs.loc[(df_cs['Crop 1'] == row['Crop 1']) 
                                & (df_cs['Crop 2'] ==  row['Crop 2']) 
                                &  (df_cs['Crop 3'] ==  row['Crop 3'])
                                & (df_cs['Crop 4'].isna())]['Sequences'].iloc[0]
                seq = int(seq.split()[-1]) - 1
            else:
                seq =  df_cs.loc[(df_cs['Crop 1'] == row['Crop 1']) 
                                & (df_cs['Crop 2'] ==  row['Crop 2']) 
                                &  (df_cs['Crop 3'] ==  row['Crop 3'])
                                & (df_cs['Crop 4'] ==  row['Crop 4'])]['Sequences'].iloc[0]
                seq = int(seq.split()[-1]) - 1

            seqs.append(seq)

        return seqs
    except:
        return [-1]
    
def getYield(seqs, fields, NY, CY):
    NY_total = [0]*np.size(NY,1)
    CY_total = [0]*np.size(CY,1)
    for i in range(np.size(seqs)):
        NY_total = NY_total + NY[seqs[i],:]*fields[i]
        CY_total = CY_total + CY[seqs[i],:]*fields[i]
    return np.array(NY_total), np.array(CY_total)

def getPercentages(NY_total, RNI):
    percentages_NY = NY_total / RNI
    percentages_NY = 100*percentages_NY
    np.around(percentages_NY.astype(np.double),3)
    theta = np.min(percentages_NY) # Theta is percentage van optimum theta, theta_hat!!!
    return percentages_NY, theta

def DefineCropYield(CY_total):
    group1 = [1, 10, 11, 19, 21, 22, 25, 26] # cereal and grain
    group2 = [3, 4, 12, 17, 18] # pulse and vegetables 1
    group3 = [0, 2, 5, 6,7, 8, 9, 13, 14, 15, 23, 24] # pulse and vegetables 2
    group4 = [16, 20] # oil and fats 

    # Total crop yield for each food group
    CY_food_group1 = 0
    CY_food_group2 = 0
    CY_food_group3 = 0
    CY_food_group4 = 0
    for i in group1:
        CY_food_group1 = CY_food_group1 + CY_total[i]

    for i in group2:
        CY_food_group2 = CY_food_group2 + CY_total[i]

    for i in group3:
        CY_food_group3 = CY_food_group3 + CY_total[i]

    for i in group4:
        CY_food_group4 = CY_food_group4 + CY_total[i]
    
    # Calculate the crop yield for 1 person for 1 day (which must be between minrat & maxrat)
    days = 1826
    population = 225521
    CY_food_group1 = CY_food_group1 / (days*population)
    CY_food_group2 = CY_food_group2 / (days*population)
    CY_food_group3 = CY_food_group3 / (days*population)
    CY_food_group4 = CY_food_group4 / (days*population)

    return [CY_food_group1, CY_food_group2, CY_food_group3, CY_food_group4]

def create_figure(names,values):

    
    minrat = [250,30,30,15]
    maxrat = [500,130,130,40]

    red = 'rgba(242, 38, 19, .4)'
    green = 'rgba(63, 195, 128, .85)'
    black = 'rgba(255, 240, 0, 1)'

    # [y,x, color]
    eerste = []
    tweede = []
    derde = []
    vierde = []
    vijfde = []

    size = 4
    for ind in range(4):

        val = values[ind]
        name = names[ind]
        if val < minrat[ind]:
            first = [name, val - size, red]
            second = [name, size, black]
            third  = [name, minrat[ind] - val, red]
            fourth = [name, maxrat[ind]-minrat[ind], green]
            fifth = [name, 100, red]
        elif val == minrat[ind]:
            first = [name, minrat[ind] - size, red]
            second = [name, size, black]
            third  = [name, minrat[ind] - val, red]
            fourth = [name, maxrat[ind]-minrat[ind], green]
            fifth = [name, 100, red]
        elif (val > minrat[ind]) & (val<maxrat[ind]):
            first = [name, minrat[ind], red]
            second = [name, val-minrat[ind] - size, green]
            third  = [name, size, black]
            fourth = [name, maxrat[ind]-val, green]
            fifth = [name, 100, red]
        elif val == maxrat[ind]:
            first = [name, minrat[ind], red]
            second = [name, maxrat[ind]-minrat[ind] - size, green]
            third  = [name, size, black]
            fourth = [name, maxrat[ind]-val, green]
            fifth = [name, 100, red]
        elif val > maxrat[ind]:
            first = [name, minrat[ind], red]
            second = [name, maxrat[ind]-minrat[ind], green]
            third  = [name, val - maxrat[ind] - size, red]
            fourth = [name, size, black]
            fifth = [name, maxrat[ind]+ 100 - val, red]

        eerste.append(first)
        tweede.append(second)
        derde.append(third)
        vierde.append(fourth)
        vijfde.append(fifth)

    fig = go.Figure()
    fig = subplots.make_subplots(specs=[[{"secondary_y": True}]], print_grid=True)
    fig.add_trace(go.Bar(y=[eerste[0][0],eerste[1][0], eerste[2][0], eerste[3][0]], 
                        x=[eerste[0][1],eerste[1][1], eerste[2][1], eerste[3][1]],
                        marker=dict(color=[eerste[0][2],eerste[1][2], eerste[2][2], eerste[3][2]]), 
                        orientation='h',hoverinfo='none',))
    fig.add_trace(go.Bar(y=[tweede[0][0],tweede[1][0], tweede[2][0], tweede[3][0]], 
                        x=[tweede[0][1],tweede[1][1], tweede[2][1], tweede[3][1]],
                        marker=dict(color=[tweede[0][2],tweede[1][2], tweede[2][2], tweede[3][2]]), 
                        orientation='h',hoverinfo='none'))
    fig.add_trace(go.Bar(y=[derde[0][0],derde[1][0], derde[2][0], derde[3][0]], 
                        x=[derde[0][1],derde[1][1], derde[2][1], derde[3][1]],
                        marker=dict(color=[derde[0][2],derde[1][2], derde[2][2], derde[3][2]]), 
                        orientation='h',hoverinfo='none'))
    fig.add_trace(go.Bar(y=[vierde[0][0],vierde[1][0], vierde[2][0], vierde[3][0]], 
                        x=[vierde[0][1],vierde[1][1], vierde[2][1], vierde[3][1]],
                        marker=dict(color=[vierde[0][2],vierde[1][2], vierde[2][2], vierde[3][2]]), 
                        orientation='h',hoverinfo='none'))
    fig.add_trace(go.Bar(y=[vijfde[0][0],vijfde[1][0], vijfde[2][0], vijfde[3][0]], 
                        x=[vijfde[0][1],vijfde[1][1], vijfde[2][1], vijfde[3][1]],
                        marker=dict(color=[vijfde[0][2],vijfde[1][2], vijfde[2][2], vijfde[3][2]]), 
                        orientation='h',hoverinfo='none'))

    fig.update_layout(barmode='stack')
    fig.update_layout(showlegend=False)

    # fig.update_layout(width=600, height=250, yaxis2= dict(fixedrange= True,
    #                                                     range= [0, 1],
    #                                                     visible= False))

    return fig

def check_max(seqs,fields,NY,CY):

    NY_total, CY_total = getYield(seqs, fields, NY, CY)
    CY_food_groups = DefineCropYield(CY_total)

    maxrat = [500,130,130,40]

    return [1 if CY_food_groups[i] > maxrat[i] else 0 for i in range(4)]

def check_char(seq,crop_char, min_metrics):
    return [1 if crop_char[seq,i] < min_metrics[i] else 0 for i in range(3)]

def check_UL(perc, UL):
    return [1 if perc[i] > UL[i] else 0 for i in range(len(UL))]

